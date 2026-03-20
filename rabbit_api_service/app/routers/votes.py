from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_user_id
from ..models import Comment, Post, Vote
from ..schemas import VoteOut, VoteUpsert

router = APIRouter(prefix="/rabbit", tags=["rabbit-votes"])


@router.put("/votes", response_model=VoteOut)
async def upsert_vote(
    payload: VoteUpsert,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    if payload.value not in (-1, 0, 1):
        raise HTTPException(status_code=400, detail="value must be -1, 0, or 1")

    if payload.target_type == "post":
        exists = await db.execute(select(Post.id).where(Post.id == payload.target_id))
        if exists.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Post not found")
    else:
        exists = await db.execute(select(Comment.id).where(Comment.id == payload.target_id))
        if exists.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Comment not found")

    res = await db.execute(
        select(Vote).where(
            Vote.user_id == user_id,
            Vote.target_type == payload.target_type,
            Vote.target_id == payload.target_id,
        )
    )
    v = res.scalar_one_or_none()

    if v is None:
        v = Vote(
            user_id=user_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
            value=payload.value,
        )
        db.add(v)
        await db.commit()
        await db.refresh(v)
    else:
        v.value = payload.value
        v.updated_at = datetime.utcnow()
        await db.commit()

    return VoteOut(
        user_id=v.user_id,
        target_type=v.target_type,  # type: ignore[arg-type]
        target_id=v.target_id,
        value=v.value,
        created_at=v.created_at,
        updated_at=v.updated_at,
    )
