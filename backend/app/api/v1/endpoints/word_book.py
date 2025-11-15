from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin_user
from app.models import User
from app.schemas.word_book import WordBookListResponse, WordBookResponse
from app.services import word_book as word_book_service
from app.services.word_book import WordBookUploadError
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/word-books")


@router.post("")
async def create_word_book_endpoint(
    title: str = Form(...),
    description: str = Form(""),
    language: str = Form("en"),
    level: str = Form(""),
    tags: str = Form("[]"),
    cover: UploadFile | None = File(None),
    word_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_user),
):
    try:
        book = await word_book_service.create_word_book(
            session,
            title=title,
            description=description,
            language=language,
            level=level,
            tags_raw=tags,
            cover_file=cover,
            word_file=word_file,
            operator=current_user,
        )
        await session.commit()
    except WordBookUploadError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except Exception:
        await session.rollback()
        raise

    data = WordBookResponse.model_validate(book).model_dump()
    return success_response(data)


@router.get("")
async def list_word_books(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    books = await word_book_service.list_word_books(session)
    data = WordBookListResponse(
        items=[WordBookResponse.model_validate(book) for book in books]
    ).model_dump()
    return success_response(data)
