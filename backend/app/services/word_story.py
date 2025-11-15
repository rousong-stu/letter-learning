from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
import json
import re
from typing import Any, Iterable, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User, WordStory
from app.repositories import word_story as word_story_repo
from app.repositories import user_word_book as user_word_book_repo

logger = logging.getLogger(__name__)
settings = get_settings()
DEFAULT_SAMPLE_WORDS = [
    "abandon",
    "accurate",
    "acquire",
    "adapt",
    "analyze",
    "approach",
    "assume",
    "benefit",
    "challenge",
    "contribute",
    "decline",
    "define",
    "demand",
    "determine",
    "efficient",
    "essential",
    "evidence",
    "function",
    "impact",
    "maintain",
]

COURSE_LABEL_MAP = {
    "basic": "基础巩固班",
    "postgraduate": "考研冲刺班",
    "toefl": "托福强化班",
    "ielts": "雅思口语班",
}
DEFAULT_WORKFLOW_CLASS = "学习计划"
DEFAULT_WORKFLOW_LEVEL = "通用词库"


@dataclass
class WorkflowInputs:
    words: list[str]
    user_class: str
    english_level: str
    target_word_num: int
    conversation_name: str
    day_index: int | None = None


class WordStoryGenerationError(RuntimeError):
    pass


def _normalize_words(words: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for word in words:
        normalized = word.strip()
        if not normalized:
            continue
        cleaned.append(normalized)
    if not cleaned:
        raise ValueError("词表不能为空")
    return cleaned


def _build_headers() -> dict[str, str]:
    if not settings.coze_api_token:
        raise WordStoryGenerationError("未配置 Coze 访问令牌")
    return {
        "Authorization": f"Bearer {settings.coze_api_token}",
        "Content-Type": "application/json",
    }


def _split_story_sections(full_text: str) -> tuple[str, str]:
    label_story = "英文短文："
    label_image = "根据短文自动生成的插图："
    text = full_text.strip()
    if text.startswith(label_story):
        text = text[len(label_story) :].strip()
    image_caption = ""
    idx = text.find(label_image)
    if idx != -1:
        story = text[:idx].strip()
        image_caption = text[idx + len(label_image) :].strip()
    else:
        story = text.strip()
    return story, image_caption


def _extract_text_from_event(node: Any) -> str:
    if not isinstance(node, dict):
        return ""
    content = node.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        fragments: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") in {"text", "raw_text"}:
                    value = block.get("text") or block.get("content")
                    if value:
                        fragments.append(value)
        return "".join(fragments)
    if isinstance(content, dict) and isinstance(content.get("content"), list):
        fragments = [
            block.get("text") or block.get("content") or ""
            for block in content["content"]
            if isinstance(block, dict)
        ]
        return "".join(fragments)
    return node.get("text") or ""


def _extract_image_urls(event_payload: dict[str, Any]) -> list[str]:
    def _extract(blocks: Iterable[dict[str, Any]]) -> list[str]:
        urls: list[str] = []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "image" and isinstance(
                block.get("image"), dict
            ):
                url = block["image"].get("url")
                if url:
                    urls.append(url)
            elif block.get("type") == "images":
                for img in block.get("images") or []:
                    if isinstance(img, dict):
                        url = img.get("url")
                        if url:
                            urls.append(url)
        return urls

    data = event_payload.get("data") or event_payload
    content = data.get("content")
    if isinstance(content, list):
        return _extract(content)
    if isinstance(content, dict) and isinstance(content.get("content"), list):
        return _extract(content["content"])
    if isinstance(data.get("images"), list):
        return [
            img.get("url")
            for img in data["images"]
            if isinstance(img, dict) and img.get("url")
        ]
    return []


def _calculate_day_index(
    start_date: date, story_date: date, total_days: int | None
) -> int:
    if story_date <= start_date:
        return 1
    offset = (story_date - start_date).days
    day_idx = offset + 1
    if total_days:
        day_idx = min(day_idx, total_days)
    return max(1, day_idx)


def _map_course_label(code: str | None) -> str:
    if not code:
        return DEFAULT_WORKFLOW_CLASS
    return COURSE_LABEL_MAP.get(code, code) or DEFAULT_WORKFLOW_CLASS


async def _prepare_workflow_inputs(
    session: AsyncSession,
    user: User,
    story_date: date,
    override_words: Iterable[str] | None,
) -> WorkflowInputs:
    plan = await user_word_book_repo.get_latest_by_user(session, user.id)
    plan_words: list[str] = []
    day_index: int | None = None

    if plan:
        day_index = _calculate_day_index(plan.start_date, story_date, plan.total_days)
        plan_words = await user_word_book_repo.list_words_for_day(
            session,
            plan.id,
            day_index,
            plan.daily_quota or len(DEFAULT_SAMPLE_WORDS),
        )

    normalized_override: list[str] | None = None
    if override_words:
        normalized_override = _normalize_words(override_words)

    normalized_plan_words: list[str] | None = None
    if plan_words:
        normalized_plan_words = _normalize_words(plan_words)

    words = (
        normalized_override
        or normalized_plan_words
        or _normalize_words(DEFAULT_SAMPLE_WORDS)
    )
    user_class = _map_course_label(plan.course_code if plan else None)
    english_level = (
        plan.book.title if plan and plan.book and plan.book.title else DEFAULT_WORKFLOW_LEVEL
    )
    target_word_num = plan.daily_quota if plan and plan.daily_quota else len(words)
    conversation_name = f"{user.username}-{story_date.isoformat()}"

    return WorkflowInputs(
        words=words,
        user_class=user_class,
        english_level=english_level,
        target_word_num=target_word_num,
        conversation_name=conversation_name,
        day_index=day_index,
    )


def _build_workflow_payload(inputs: WorkflowInputs) -> dict[str, Any]:
    if not settings.coze_workflow_id:
        raise WordStoryGenerationError("未配置 Coze 工作流 ID")
    joined_words = ", ".join(inputs.words)
    return {
        "workflow_id": settings.coze_workflow_id,
        "stream": True,
        "additional_messages": [
            {
                "role": "user",
                "type": "question",
                "content_type": "text",
                "content": joined_words,
            }
        ],
        "parameters": {
            "CONVERSATION_NAME": inputs.conversation_name,
            "USER_CLASS": inputs.user_class,
            "USER_ENGLISH_LEVEL": inputs.english_level,
            "USER_TARGETWORD_NUM": str(inputs.target_word_num),
        },
    }


async def _stream_workflow_story(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> tuple[
    str,
    dict[str, Any],
    Optional[str],
    dict[str, Optional[str]],
    str,
    list[str],
]:
    chunks: list[str] = []
    image_urls: list[str] = []
    usage: dict[str, Any] = {}
    model_name: Optional[str] = None
    meta: dict[str, Optional[str]] = {"chat_id": None, "conversation_id": None}
    current_message_has_delta = False

    def process_event(event: dict[str, Any]):
        nonlocal usage, model_name, current_message_has_delta
        event_type = (event.get("event") or "").lower()
        data_node = event.get("data") or event
        if event_type == "conversation.chat.created":
            meta["chat_id"] = (
                data_node.get("id") or data_node.get("chat_id") or meta.get("chat_id")
            )
            meta["conversation_id"] = data_node.get("conversation_id") or meta.get(
                "conversation_id"
            )
        elif event_type == "conversation.message.delta":
            text = _extract_text_from_event(data_node)
            if text:
                chunks.append(text)
                current_message_has_delta = True
        elif event_type == "conversation.message.completed":
            if not current_message_has_delta and data_node.get("type") == "answer":
                text = _extract_text_from_event(data_node)
                if text:
                    chunks.append(text)
            current_message_has_delta = False
        elif event_type == "conversation.chat.completed":
            usage = data_node.get("usage") or {}
            model_name = data_node.get("model_name") or data_node.get("model")
        elif event_type == "error":
            msg = data_node.get("msg") or data_node.get("message") or str(data_node)
            raise WordStoryGenerationError(f"Coze 流式错误: {msg}")

        urls = _extract_image_urls(event)
        if urls:
            image_urls.extend(urls)

    async with client.stream(
        "POST", "/v1/workflows/chat", headers=headers, json=payload
    ) as resp:
        resp.raise_for_status()
        current_event = ""
        buffer_data = ""

        async for raw_line in resp.aiter_lines():
            if raw_line is None:
                continue
            line = raw_line.strip()
            if not line:
                if current_event and buffer_data:
                    payload_str = buffer_data.strip()
                    if payload_str and payload_str != "[DONE]":
                        try:
                            event = json.loads(payload_str)
                        except json.JSONDecodeError:
                            event = {}
                        if isinstance(event, dict):
                            event.setdefault("event", current_event)
                            process_event(event)
                current_event = ""
                buffer_data = ""
                continue
            if line.startswith("{") or line.startswith("["):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    process_event(event)
                continue
            if line.startswith("event:"):
                current_event = line.split("event:", 1)[1].strip()
                continue
            if line.startswith("data:"):
                fragment = line.split("data:", 1)[1].strip()
                buffer_data = f"{buffer_data}\n{fragment}".strip()
                continue

    raw_text = "".join(chunks).strip()
    story_text, image_caption = _split_story_sections(raw_text)
    if not story_text:
        raise WordStoryGenerationError("未能从 Coze 流式响应中获取短文")

    if not image_urls and image_caption:
        image_urls = re.findall(r"https?://[^\s]+", image_caption)

    deduped_urls = list(dict.fromkeys(image_urls))
    return story_text, usage, model_name, meta, image_caption, deduped_urls


async def generate_story(
    session: AsyncSession,
    user: User,
    *,
    words: Iterable[str] | None = None,
    story_date: date | None = None,
    force: bool = False,
) -> WordStory:
    story_date = story_date or date.today()
    existing = await word_story_repo.get_by_user_and_date(
        session, user.id, story_date
    )
    if existing and not force:
        return existing

    workflow_inputs = await _prepare_workflow_inputs(
        session, user, story_date, words
    )
    headers = _build_headers()
    payload = _build_workflow_payload(workflow_inputs)

    async with httpx.AsyncClient(
        base_url=settings.coze_api_base.rstrip("/"),
        timeout=httpx.Timeout(settings.coze_request_timeout_seconds),
    ) as client:
        (
            story_text,
            usage,
            model_name,
            chat_meta,
            image_caption,
            image_urls,
        ) = await _stream_workflow_story(client, headers, payload)

    generated_at = datetime.utcnow()
    story_tokens = (
        usage.get("output_count")
        or usage.get("output_tokens")
        or usage.get("token_count")
    )
    primary_image_url = image_urls[0] if image_urls else None

    extra = {
        "chat_id": chat_meta.get("chat_id"),
        "conversation_id": chat_meta.get("conversation_id"),
        "usage": usage,
        "image_caption": image_caption,
        "image_urls": image_urls,
        "workflow_params": {
            "user_class": workflow_inputs.user_class,
            "english_level": workflow_inputs.english_level,
            "target_word_num": workflow_inputs.target_word_num,
            "day_index": workflow_inputs.day_index,
        },
    }

    if existing:
        return await word_story_repo.update_word_story(
            session,
            existing,
            words=workflow_inputs.words,
            story_text=story_text,
            generated_at=generated_at,
            story_tokens=story_tokens,
            model_name=model_name,
            image_url=primary_image_url,
            image_caption=image_caption,
            status="success",
            extra=extra,
        )

    return await word_story_repo.create_word_story(
        session,
        user_id=user.id,
        story_date=story_date,
        words=workflow_inputs.words,
        story_text=story_text,
        generated_at=generated_at,
        story_tokens=story_tokens,
        model_name=model_name,
        image_url=primary_image_url,
        image_caption=image_caption,
        status="success",
        extra=extra,
    )


async def get_story_by_date(
    session: AsyncSession,
    user: User,
    story_date: date,
) -> WordStory | None:
    return await word_story_repo.get_by_user_and_date(session, user.id, story_date)


async def list_recent_stories(
    session: AsyncSession,
    user: User,
    *,
    limit: int = 30,
):
    return await word_story_repo.list_stories(session, user.id, limit=limit)
