from __future__ import annotations

import os
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool


class Base(DeclarativeBase):
    pass


def create_engine(database_url: str) -> AsyncEngine:
    pool_class = (os.getenv("RABBIT_DB_POOL_CLASS", "queue").strip().lower() or "queue")
    kwargs: dict = {"pool_pre_ping": True}
    if pool_class in ("null", "none"):
        kwargs["poolclass"] = NullPool
    return create_async_engine(database_url, **kwargs)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
