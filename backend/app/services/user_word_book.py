from __future__ import annotations

import math
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import word_book as word_book_repo
from app.repositories import user_word_book as user_word_book_repo
from app.models.word_book import UserWordBook, UserWordBookWord


class UserWordBookError(RuntimeError):
    pass


async def create_learning_plan(
    session: AsyncSession,
    *,
    user: User,
    word_book_id: int,
    daily_quota: int,
    course_code: str | None,
    start_date: date,
    reset: bool = False,
) -> UserWordBook:
    book = await word_book_repo.get_book_with_words(session, word_book_id)
    if not book:
        raise UserWordBookError("单词书不存在或未发布")

    existing_plan = await user_word_book_repo.get_latest_by_user(session, user.id)
    if existing_plan:
        if not reset:
            raise UserWordBookError("您当前已有学习计划，如需修改请点击重置")
        await user_word_book_repo.delete_by_user(session, user.id)

    total_days = math.ceil((book.total_words or 0) / daily_quota) or 1

    user_plan = await user_word_book_repo.create_user_word_book(
        session,
        user_id=user.id,
        word_book_id=book.id,
        daily_quota=daily_quota,
        course_code=course_code,
        start_date=start_date,
        total_days=total_days,
    )

    plan_items: list[UserWordBookWord] = []
    day_index = 1
    sequence = 0
    for word in sorted(book.words, key=lambda w: w.order_index):
        plan_items.append(
            UserWordBookWord(
                user_word_book_id=user_plan.id,
                word_book_word_id=word.id,
                day_index=day_index,
                sequence_in_day=sequence,
            )
        )
        sequence += 1
        if sequence >= daily_quota:
            day_index += 1
            sequence = 0

    session.add_all(plan_items)
    await session.flush()
    return user_plan


async def get_current_plan(
    session: AsyncSession,
    *,
    user: User,
) -> UserWordBook | None:
    return await user_word_book_repo.get_latest_by_user(session, user.id)
