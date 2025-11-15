from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.word_card import (
    WordCardActionRequest,
    WordCardActionResponse,
    WordCardListResponse,
)
from app.services import word_card as word_card_service
from app.services.word_card import WordCardError
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/word-cards")


@router.get("/learning")
async def list_learning_cards(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cards = await word_card_service.list_learning_cards(
        session, current_user, limit=limit
    )
    return success_response(WordCardListResponse(items=cards).model_dump())


@router.post("/{card_id}/actions")
async def apply_word_card_action(
    payload: WordCardActionRequest,
    card_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        item = await word_card_service.apply_action(
            session,
            current_user,
            entry_id=card_id,
            action=payload.action,
        )
        await session.commit()
    except WordCardError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response(WordCardActionResponse(item=item).model_dump())
