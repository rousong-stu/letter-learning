from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.dictionary import (
    DefinitionTranslationRequest,
    DefinitionTranslationResponse,
)
from app.services import dictionary as dictionary_service
from app.services import dictionary_translation as dictionary_translation_service
from app.services.dictionary import DictionaryEntryNotFound, DictionaryLookupError
from app.services.dictionary_translation import (
    DictionaryDefinitionTranslationError,
)
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/dictionary")


@router.get("/lookup")
async def lookup_word(
    word: str = Query(..., min_length=1, description="要查询的英文单词"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user  # 仅校验权限
    try:
        entry = await dictionary_service.get_or_fetch_entry(session, word)
        await session.commit()
    except ValueError as exc:
        await session.rollback()
        return error_response(str(exc), code=400)
    except DictionaryEntryNotFound as exc:
        await session.rollback()
        return error_response(str(exc), code=404)
    except DictionaryLookupError as exc:
        await session.rollback()
        return error_response(str(exc), code=502)
    except Exception:
        await session.rollback()
        raise

    return success_response(dictionary_service.build_entry_response(entry).model_dump())


@router.post(
    "/{entry_id}/definitions/{definition_index}/translation",
)
async def translate_definition(
    entry_id: int,
    definition_index: int,
    payload: DefinitionTranslationRequest = Body(
        DefinitionTranslationRequest(), embed=True
    ),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = await dictionary_translation_service.translate_definition(
            session,
            entry_id=entry_id,
            definition_index=definition_index,
            user=current_user,
            force=payload.force,
        )
        await session.commit()
    except DictionaryDefinitionTranslationError as exc:
        await session.rollback()
        return error_response(str(exc), code=exc.status_code)
    except Exception:
        await session.rollback()
        raise

    data = DefinitionTranslationResponse(
        dictionary_entry_id=record.dictionary_entry_id,
        definition_index=record.definition_index,
        translation=record.translation,
    ).model_dump()
    return success_response(data)
