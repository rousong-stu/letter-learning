from __future__ import annotations

import json
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User
from app.repositories import dictionary as dictionary_repo
from app.repositories import dictionary_translation as dictionary_translation_repo

logger = logging.getLogger(__name__)
settings = get_settings()


class DictionaryDefinitionTranslationError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _build_headers() -> dict[str, str]:
    if not settings.coze_api_token:
        raise DictionaryDefinitionTranslationError("未配置 Coze 访问令牌", status_code=500)
    return {
        "Authorization": f"Bearer {settings.coze_api_token}",
        "Content-Type": "application/json",
    }


def _build_prompt(word: str, part_of_speech: str | None, meaning: str) -> str:
    pos = f"（{part_of_speech}）" if part_of_speech else ""
    return (
        "请把下面 Merriam-Webster 词典的英文释义翻译成自然、准确的中文。"
        "保持专业、简洁，不要加入额外解释：\n"
        f"单词：{word}{pos}\n"
        f"英文释义：{meaning}"
    )


async def _stream_translation_from_coze(payload: dict) -> str:
    headers = _build_headers()
    buffers: list[str] = []

    def process_event(event_type: str, data_payload: str):
        if not data_payload or data_payload.strip() == "[DONE]":
            return
        try:
            parsed = json.loads(data_payload)
        except json.JSONDecodeError:
            return
        node = parsed.get("data") if isinstance(parsed, dict) else None
        if not isinstance(node, dict):
            node = parsed if isinstance(parsed, dict) else None
        if not isinstance(node, dict):
            return

        event_key = event_type.lower()
        message_type = (node.get("type") or "").lower()
        if event_key == "conversation.message.delta":
            if message_type == "answer":
                text = node.get("content") or node.get("text")
                if text:
                    buffers.append(text)
        elif event_key == "conversation.message.completed":
            if node.get("role") == "assistant" and message_type == "answer":
                content = node.get("content")
                if content:
                    buffers.append(content)
        elif event_key == "error":
            msg = node.get("msg") or node.get("message") or str(node)
            raise DictionaryDefinitionTranslationError(
                f"Coze 翻译失败：{msg}", status_code=502
            )

    async with httpx.AsyncClient(
        base_url=settings.coze_api_base.rstrip("/"),
        timeout=settings.coze_request_timeout_seconds,
    ) as client:
        async with client.stream(
            "POST",
            "/v3/chat",
            headers=headers,
            json=payload,
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

    content = "".join(buffers).strip()
    if not content:
        raise DictionaryDefinitionTranslationError("Coze 未返回中文释义", status_code=502)
    return content


async def translate_definition(
    session: AsyncSession,
    *,
    entry_id: int,
    definition_index: int,
    user: User,
    force: bool = False,
) -> dict:
    entry = await dictionary_repo.get_by_id(session, entry_id)
    if not entry:
        raise DictionaryDefinitionTranslationError("词典记录不存在", status_code=404)

    definitions = entry.definitions or []
    if definition_index < 0 or definition_index >= len(definitions):
        raise DictionaryDefinitionTranslationError("释义索引超出范围", status_code=400)

    existing = await dictionary_translation_repo.get_by_entry_and_index(
        session, entry.id, definition_index
    )
    if existing and not force:
        return existing

    target = definitions[definition_index]
    meaning = ""
    if isinstance(target, dict):
        meaning = str(target.get("meaning") or "").strip()
    elif isinstance(target, str):
        meaning = target.strip()
    if not meaning:
        raise DictionaryDefinitionTranslationError("没有可翻译的英文释义", status_code=400)

    if not settings.dictionary_translation_bot_id:
        raise DictionaryDefinitionTranslationError("未配置翻译智能体", status_code=500)

    prompt = _build_prompt(entry.word, entry.part_of_speech, meaning)
    payload = {
        "bot_id": settings.dictionary_translation_bot_id,
        "user_id": f"{settings.coze_user_prefix}-dict-{user.id}",
        "stream": True,
        "auto_save_history": False,
        "additional_messages": [
            {"role": "user", "content": prompt, "content_type": "text"}
        ],
    }
    if settings.dictionary_translation_space_id:
        payload["space_id"] = settings.dictionary_translation_space_id

    translation_text = await _stream_translation_from_coze(payload)

    record = await dictionary_translation_repo.upsert_translation(
        session,
        entry_id=entry.id,
        definition_index=definition_index,
        translation=translation_text,
        source="coze",
        metadata={"bot_id": settings.dictionary_translation_bot_id},
    )
    return record
