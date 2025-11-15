from __future__ import annotations

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.ai_chat import (
    AiChatMessageSchema,
    AiChatSendMessageRequest,
    AiChatSendMessageResponse,
    AiChatSessionCreateRequest,
    AiChatSessionDetailResponse,
    AiChatSessionSchema,
)
from app.services import ai_chat as ai_chat_service
from app.services.ai_chat import AiChatError
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/ai-chats")


@router.post("")
async def create_ai_chat_session(
    payload: AiChatSessionCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        chat, messages = await ai_chat_service.start_chat_session(
            session,
            current_user,
            story_text=payload.story_text,
            word_story_id=payload.word_story_id,
        )
        await session.commit()
    except AiChatError as exc:
        await session.rollback()
        return error_response(str(exc), code=exc.status_code)
    except Exception:
        await session.rollback()
        raise

    data = AiChatSessionDetailResponse(
        session=AiChatSessionSchema.model_validate(chat),
        messages=[AiChatMessageSchema.model_validate(item) for item in messages],
    )
    return success_response(data.model_dump())


@router.get("/{chat_id}")
async def get_ai_chat_detail(
    chat_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        chat, messages = await ai_chat_service.get_chat_detail(
            session, current_user, chat_id
        )
    except AiChatError as exc:
        return error_response(str(exc), code=exc.status_code)

    data = AiChatSessionDetailResponse(
        session=AiChatSessionSchema.model_validate(chat),
        messages=[AiChatMessageSchema.model_validate(item) for item in messages],
    )
    return success_response(data.model_dump())


@router.post("/{chat_id}/messages")
async def send_ai_chat_message(
    payload: AiChatSendMessageRequest,
    chat_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        chat, new_messages = await ai_chat_service.send_chat_message(
            session,
            current_user,
            chat_id,
            payload.content,
        )
        await session.commit()
    except AiChatError as exc:
        await session.rollback()
        return error_response(str(exc), code=exc.status_code)
    except Exception:
        await session.rollback()
        raise

    data = AiChatSendMessageResponse(
        session=AiChatSessionSchema.model_validate(chat),
        new_messages=[
            AiChatMessageSchema.model_validate(item) for item in new_messages
        ],
    )
    return success_response(data.model_dump())
