from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = getattr(request.app.state, "sessionmaker", None)
    if sessionmaker is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async with sessionmaker() as session:
        yield session


def get_user_id(x_user_id: str | None = Header(default=None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing x-user-id")
    return x_user_id
