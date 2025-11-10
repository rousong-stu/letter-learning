from __future__ import annotations

import logging
from datetime import date, datetime
import json
from typing import Any, Iterable, Optional
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User, WordStory
from app.repositories import word_story as word_story_repo

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


def _build_prompt(words: list[str]) -> str:
    joined = ", ".join(words)
    return (
        "Please craft a cohesive short passage (about 4 paragraphs) for advanced "
        "English learners."
        " The passage must naturally incorporate all of the following vocabulary words: "
        f"{joined}."
        " Use meaningful context so learners can infer each word's usage."
    )


def _build_headers() -> dict[str, str]:
    if not settings.coze_api_token:
        raise WordStoryGenerationError("未配置 Coze 访问令牌")
    return {
        "Authorization": f"Bearer {settings.coze_api_token}",
        "Content-Type": "application/json",
    }


async def _stream_story(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> tuple[str, dict[str, Any], Optional[str], dict[str, Optional[str]]]:
    chunk_buffer: list[str] = []
    story_parts: list[str] = []
    usage: dict[str, Any] = {}
    model_name: Optional[str] = None
    meta: dict[str, Optional[str]] = {"chat_id": None, "conversation_id": None}

    def process_event(event_type: str, data_payload: str):
        nonlocal usage, model_name
        if not data_payload or data_payload.strip() == "[DONE]":
            return
        try:
            parsed = json.loads(data_payload)
        except json.JSONDecodeError:
            return
        node: Any = parsed.get("data") if isinstance(parsed, dict) else None
        if not isinstance(node, dict) and isinstance(parsed, dict):
            node = parsed
        if not isinstance(node, dict):
            return

        event_key = event_type.lower()
        if event_key == "conversation.chat.created":
            meta["chat_id"] = (
                node.get("id") or node.get("chat_id") or meta.get("chat_id")
            )
            meta["conversation_id"] = node.get("conversation_id") or meta.get(
                "conversation_id"
            )
        elif event_key == "conversation.message.delta":
            text = node.get("content") or node.get("text")
            if text:
                chunk_buffer.append(text)
        elif event_key == "conversation.message.completed":
            if (
                node.get("role") == "assistant"
                and node.get("type") == "answer"
            ):
                content = node.get("content")
                if content:
                    story_parts.append(content)
                elif chunk_buffer:
                    story_parts.append("".join(chunk_buffer))
                chunk_buffer.clear()
        elif event_key == "conversation.chat.completed":
            usage = node.get("usage") or {}
            model_name = node.get("model_name") or node.get("model")
            meta["conversation_id"] = node.get("conversation_id") or meta.get(
                "conversation_id"
            )
            if not story_parts and chunk_buffer:
                story_parts.append("".join(chunk_buffer))
            chunk_buffer.clear()
        elif event_key == "error":
            msg = node.get("msg") or node.get("message") or str(node)
            raise WordStoryGenerationError(f"Coze 流式错误: {msg}")

    async with client.stream(
        "POST", "/v3/chat", headers=headers, json=payload
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
                    process_event(current_event, buffer_data)
                current_event = ""
                buffer_data = ""
                continue
            if line.startswith("event:"):
                current_event = line.split("event:", 1)[1].strip()
                continue
            if line.startswith("data:"):
                fragment = line.split("data:", 1)[1].strip()
                buffer_data = f"{buffer_data}\n{fragment}".strip()
                continue
        if current_event and buffer_data:
            process_event(current_event, buffer_data)

    story_text = "\n\n".join(
        part.strip() for part in story_parts if part and part.strip()
    ).strip()
    if not story_text:
        raise WordStoryGenerationError("未能从 Coze 流式响应中获取短文")

    return story_text, usage, model_name, meta


async def generate_story(
    session: AsyncSession,
    user: User,
    *,
    words: Iterable[str] | None = None,
    story_date: date | None = None,
    force: bool = False,
) -> WordStory:
    story_date = story_date or date.today()
    source_words = words or DEFAULT_SAMPLE_WORDS
    normalized_words = _normalize_words(source_words)
    existing = await word_story_repo.get_by_user_and_date(
        session, user.id, story_date
    )
    if existing and not force:
        return existing

    if not settings.coze_bot_id:
        raise WordStoryGenerationError("未配置 Coze 智能体 ID")

    prompt = _build_prompt(normalized_words)
    headers = _build_headers()
    payload = {
        "bot_id": settings.coze_bot_id,
        "user_id": f"{settings.coze_user_prefix}-{user.id}",
        "stream": True,
        "auto_save_history": True,
        "meta_data": {"trace_id": uuid4().hex},
        "additional_messages": [
            {
                "role": "user",
                "content_type": "text",
                "content": prompt,
            }
        ],
    }

    async with httpx.AsyncClient(
        base_url=settings.coze_api_base.rstrip("/"),
        timeout=httpx.Timeout(settings.coze_request_timeout_seconds),
    ) as client:
        (
            story_text,
            usage,
            model_name,
            chat_meta,
        ) = await _stream_story(client, headers, payload)
    generated_at = datetime.utcnow()
    story_tokens = usage.get("output_tokens") or usage.get("total_tokens")

    extra = {
        "chat_id": chat_meta.get("chat_id"),
        "conversation_id": chat_meta.get("conversation_id"),
        "usage": usage,
    }

    if existing:
        return await word_story_repo.update_word_story(
            session,
            existing,
            words=normalized_words,
            story_text=story_text,
            generated_at=generated_at,
            story_tokens=story_tokens,
            model_name=model_name,
            status="success",
            extra=extra,
        )

    return await word_story_repo.create_word_story(
        session,
        user_id=user.id,
        story_date=story_date,
        words=normalized_words,
        story_text=story_text,
        generated_at=generated_at,
        story_tokens=story_tokens,
        model_name=model_name,
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
