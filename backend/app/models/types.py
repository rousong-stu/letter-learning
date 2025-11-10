from __future__ import annotations

from sqlalchemy import BigInteger, Integer
from sqlalchemy.dialects import mysql


def bigint() -> BigInteger:
    """返回兼容 SQLite 的 BigInteger 类型。"""
    base = BigInteger()
    base = base.with_variant(Integer, "sqlite")
    base = base.with_variant(mysql.BIGINT(unsigned=True), "mysql")
    return base
