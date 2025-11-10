from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.word_story import (
    WordStoryGenerateRequest,
    WordStoryListResponse,
    WordStoryResponse,
)
from app.services import word_story as word_story_service
from app.services.word_story import WordStoryGenerationError
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/word-stories")


@router.get("/today")
async def get_today_story(
    auto_generate: bool = Query(True, description="若无记录是否自动生成"),
    force: bool = Query(False, description="是否强制重新生成"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    story_date = date.today()
    story = await word_story_service.get_story_by_date(session, current_user, story_date)

    if force or (not story and auto_generate):
        try:
            story = await word_story_service.generate_story(
                session,
                current_user,
                story_date=story_date,
                force=force,
            )
            await session.commit()
        except WordStoryGenerationError as exc:
            await session.rollback()
            return error_response(str(exc), code=502)
        except Exception:
            await session.rollback()
            raise
    elif not story:
        return error_response("今日尚未生成短文", code=404)

    return success_response(WordStoryResponse.model_validate(story).model_dump())


@router.post("/generate")
async def generate_story_endpoint(
    payload: WordStoryGenerateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        story = await word_story_service.generate_story(
            session,
            current_user,
            words=payload.words,
            story_date=payload.story_date,
            force=payload.force,
        )
        await session.commit()
    except WordStoryGenerationError as exc:
        await session.rollback()
        return error_response(str(exc), code=502)
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    return success_response(WordStoryResponse.model_validate(story).model_dump())


@router.get("/history")
async def list_word_stories(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stories = await word_story_service.list_recent_stories(
        session, current_user, limit=limit
    )
    data = WordStoryListResponse(
        items=[WordStoryResponse.model_validate(item) for item in stories]
    )
    return success_response(data.model_dump())
