from __future__ import annotations

import logging
from datetime import datetime
import json
from typing import Any, Sequence

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import AiChatMessage, AiChatSession, User
from app.repositories import ai_chat as ai_chat_repo

logger = logging.getLogger(__name__)
settings = get_settings()
MAX_CHAT_ROUNDS = 12
GREETING_TEXT = "你好呀！我是 lulu，这篇文章有什么想要问我的吗？"


class AiChatError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _build_headers() -> dict[str, str]:
    if not settings.coze_api_token:
        raise AiChatError("未配置 Coze 访问令牌", status_code=500)
    return {
        "Authorization": f"Bearer {settings.coze_api_token}",
        "Content-Type": "application/json",
    }


def _get_story_snapshot(chat: AiChatSession) -> str:
    data = chat.extra if isinstance(chat.extra, dict) else {}
    text = data.get("story_text") if isinstance(data, dict) else ""
    return (text or "").strip()


def _normalize_coze_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        fragments: list[str] = []
        for block in content:
            if isinstance(block, dict):
                block_type = (block.get("type") or "").lower()
                if block_type in {"text", "raw_text", "paragraph"}:
                    text = block.get("text") or block.get("content")
                    if text:
                        fragments.append(str(text))
                elif "content" in block and isinstance(block["content"], list):
                    fragments.append(_normalize_coze_content(block["content"]))
        return "".join(fragments).strip()
    if isinstance(content, dict):
        inner = content.get("content")
        if inner is not None:
            return _normalize_coze_content(inner)
        text = content.get("text") or content.get("value")
        if text:
            return str(text).strip()
    return ""


async def _call_coze_chat(
    *,
    user: User,
    content: str,
    conversation_id: str | None,
) -> tuple[str | None, str, dict]:
    if not settings.coze_chat_bot_id:
        raise AiChatError("未配置 AI 对话智能体", status_code=500)

    payload: dict[str, Any] = {
        "bot_id": settings.coze_chat_bot_id,
        "stream": True,
        "user_id": f"{settings.coze_user_prefix}-chat-{user.id}",
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": content,
                "content_type": "text",
            }
        ],
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if settings.coze_chat_space_id:
        payload["space_id"] = settings.coze_chat_space_id

    async with httpx.AsyncClient(
        base_url=settings.coze_api_base.rstrip("/"),
        timeout=httpx.Timeout(settings.coze_request_timeout_seconds),
    ) as client:
        try:
            async with client.stream(
                "POST",
                "/v3/chat",
                headers=_build_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                gathered_text: list[str] = []
                final_answer = ""
                convo_id = conversation_id
                chat_id: str | None = None
                usage: dict | None = None

                def process_event(event_name: str | None, raw_payload: str) -> None:
                    nonlocal final_answer, convo_id, chat_id, usage
                    if not event_name or not raw_payload:
                        return
                    try:
                        data = json.loads(raw_payload)
                    except json.JSONDecodeError:
                        return
                    if not isinstance(data, dict):
                        return
                    name = event_name.strip().lower()
                    if name.startswith("conversation.chat"):
                        convo_id = data.get("conversation_id") or convo_id
                        chat_id = data.get("id") or chat_id
                        if name == "conversation.chat.failed":
                            error_msg = (
                                data.get("last_error", {}).get("msg")
                                or "AI 对话失败"
                            )
                            raise AiChatError(
                                f"AI 对话失败：{error_msg}", status_code=502
                            )
                        if name == "conversation.chat.completed":
                            usage = data.get("usage") or usage
                        return
                    if data.get("role") != "assistant":
                        return
                    if (data.get("type") or "").lower() != "answer":
                        return
                    text = _normalize_coze_content(
                        data.get("content") or data.get("delta")
                    )
                    if not text:
                        return
                    if name == "conversation.message.delta":
                        gathered_text.append(text)
                    elif name == "conversation.message.completed":
                        final_answer = text

                current_event: str | None = None
                buffer: list[str] = []

                async for raw_line in response.aiter_lines():
                    if raw_line is None:
                        continue
                    line = raw_line.strip()
                    if not line:
                        if current_event and buffer:
                            process_event(current_event, "\n".join(buffer))
                        current_event = None
                        buffer = []
                        continue
                    if line.startswith("event:"):
                        if current_event and buffer:
                            process_event(current_event, "\n".join(buffer))
                            buffer = []
                        current_event = line.split("event:", 1)[1].strip()
                        continue
                    if line.startswith("data:"):
                        buffer.append(line.split("data:", 1)[1].strip())
                        continue
                if current_event and buffer:
                    process_event(current_event, "\n".join(buffer))

                reply_text = final_answer or "".join(gathered_text).strip()
                if not reply_text:
                    raise AiChatError("Coze 未返回有效回复", status_code=502)
                return convo_id, reply_text, {
                    "chat_id": chat_id,
                    "usage": usage,
                }
        except AiChatError:
            raise
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text if exc.response is not None else ""
            logger.error("Coze chat HTTP error: %s %s", exc, detail)
            raise AiChatError("AI 对话服务暂不可用", status_code=502) from exc
        except httpx.HTTPError as exc:
            logger.exception("Coze chat request failed")
            raise AiChatError("AI 对话服务请求失败", status_code=502) from exc


async def start_chat_session(
    session: AsyncSession,
    user: User,
    *,
    story_text: str,
    word_story_id: int | None = None,
) -> tuple[AiChatSession, Sequence[AiChatMessage]]:
    snapshot = (story_text or "").strip()
    extra = {"story_text": snapshot} if snapshot else None
    chat = await ai_chat_repo.create_session(
        session,
        user_id=user.id,
        word_story_id=word_story_id,
        extra=extra,
    )
    await ai_chat_repo.append_message(
        session,
        chat_id=chat.id,
        sender="ai",
        content=GREETING_TEXT,
        payload={"skip_coze_history": True, "type": "greeting"},
    )
    messages = await ai_chat_repo.list_messages(session, chat.id)
    return chat, messages


async def get_chat_detail(
    session: AsyncSession, user: User, chat_id: int
) -> tuple[AiChatSession, Sequence[AiChatMessage]]:
    chat = await ai_chat_repo.get_by_id(session, chat_id, user.id)
    if not chat:
        raise AiChatError("会话不存在", status_code=404)
    messages = await ai_chat_repo.list_messages(session, chat.id)
    return chat, messages


async def send_chat_message(
    session: AsyncSession,
    user: User,
    chat_id: int,
    content: str,
) -> tuple[AiChatSession, list[AiChatMessage]]:
    chat = await ai_chat_repo.get_by_id(session, chat_id, user.id)
    if not chat:
        raise AiChatError("会话不存在", status_code=404)
    if chat.status != "active":
        raise AiChatError("会话已结束，请开启新对话", status_code=400)
    if chat.total_rounds >= MAX_CHAT_ROUNDS:
        raise AiChatError("每次对话最多持续12轮", status_code=400)

    message_text = (content or "").strip()
    if not message_text:
        raise AiChatError("请输入问题内容", status_code=400)

    history_messages = await ai_chat_repo.list_messages(session, chat.id)
    has_user_message = any(item.sender == "user" for item in history_messages)
    story_snapshot = _get_story_snapshot(chat)
    is_first_user = not has_user_message
    coze_text = message_text
    if is_first_user and story_snapshot:
        coze_text = f"短文内容：{story_snapshot}\n用户问题：{message_text}"

    conversation_id, reply_text, raw_response = await _call_coze_chat(
        user=user,
        content=coze_text,
        conversation_id=chat.coze_conversation_id,
    )

    user_msg = await ai_chat_repo.append_message(
        session,
        chat_id=chat.id,
        sender="user",
        content=message_text,
        payload={
            "coze_content": coze_text,
            "is_story_prefixed": is_first_user and bool(story_snapshot),
        },
    )
    ai_msg = await ai_chat_repo.append_message(
        session,
        chat_id=chat.id,
        sender="ai",
        content=reply_text,
        payload={"coze_response": raw_response},
    )

    chat.coze_conversation_id = conversation_id or chat.coze_conversation_id
    chat.total_rounds += 1
    if chat.total_rounds >= MAX_CHAT_ROUNDS and chat.status != "completed":
        chat.status = "completed"
        chat.ended_at = datetime.utcnow()

    await session.flush()
    return chat, [user_msg, ai_msg]
