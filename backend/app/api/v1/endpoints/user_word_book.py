from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.word_book import (
    CurrentLearningPlanResponse,
    LearningPlanRequest,
    LearningPlanResponse,
    WordBookResponse,
)
from app.services import user_word_book as user_word_book_service
from app.services.user_word_book import UserWordBookError
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/user-word-books")


@router.post("")
async def create_learning_plan(
    payload: LearningPlanRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = await user_word_book_service.create_learning_plan(
            session,
            user=current_user,
            word_book_id=payload.word_book_id,
            daily_quota=payload.daily_quota,
            course_code=payload.course_code,
            start_date=payload.start_date,
            reset=payload.reset,
        )
        await session.commit()
    except UserWordBookError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    data = LearningPlanResponse(
        id=record.id,
        word_book_id=record.word_book_id,
        daily_quota=record.daily_quota,
        course_code=record.course_code,
        start_date=record.start_date,
        total_days=record.total_days,
    ).model_dump()
    return success_response(data)


@router.get("/current")
async def get_current_learning_plan(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = await user_word_book_service.get_current_plan(
        session,
        user=current_user,
    )
    if not record:
        return success_response(None)

    data = CurrentLearningPlanResponse(
        id=record.id,
        word_book=WordBookResponse.model_validate(record.book),
        daily_quota=record.daily_quota,
        course_code=record.course_code,
        start_date=record.start_date,
        total_days=record.total_days,
    ).model_dump()
    return success_response(data)
