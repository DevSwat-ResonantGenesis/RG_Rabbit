from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_user_id
from ..models import Comment, Post
from ..schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/rabbit", tags=["rabbit-comments"])


@router.post("/posts/{post_id}/comments", response_model=CommentOut)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    pres = await db.execute(select(Post).where(Post.id == post_id))
    post = pres.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.is_locked:
        raise HTTPException(status_code=409, detail="Post is locked")

    if payload.parent_comment_id is not None:
        cres = await db.execute(select(Comment).where(Comment.id == payload.parent_comment_id))
        parent = cres.scalar_one_or_none()
        if parent is None or parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Invalid parent_comment_id")

    c = Comment(
        post_id=post_id,
        parent_comment_id=payload.parent_comment_id,
        body=payload.body,
        author_user_id=user_id,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)

    return CommentOut(
        id=c.id,
        post_id=c.post_id,
        parent_comment_id=c.parent_comment_id,
        body=c.body,
        author_user_id=c.author_user_id,
        created_at=c.created_at,
        updated_at=c.updated_at,
        is_deleted=bool(c.is_deleted),
        is_removed_by_mod=bool(c.is_removed_by_mod),
    )


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=200, ge=1, le=500),
):
    res = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .limit(limit)
    )
    items = res.scalars().all()
    return [
        CommentOut(
            id=c.id,
            post_id=c.post_id,
            parent_comment_id=c.parent_comment_id,
            body=c.body,
            author_user_id=c.author_user_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
            is_deleted=bool(c.is_deleted),
            is_removed_by_mod=bool(c.is_removed_by_mod),
        )
        for c in items
    ]


@router.get("/comments", response_model=list[CommentOut])
async def list_all_comments(
    db: AsyncSession = Depends(get_db),
    author_user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    """List comments, optionally filtered by author."""
    q = select(Comment).where(Comment.is_deleted == 0)
    if author_user_id:
        q = q.where(Comment.author_user_id == author_user_id)
    q = q.order_by(Comment.created_at.desc()).limit(limit)
    res = await db.execute(q)
    items = res.scalars().all()
    return [
        CommentOut(
            id=c.id,
            post_id=c.post_id,
            parent_comment_id=c.parent_comment_id,
            body=c.body,
            author_user_id=c.author_user_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
            is_deleted=bool(c.is_deleted),
            is_removed_by_mod=bool(c.is_removed_by_mod),
        )
        for c in items
    ]


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    res = await db.execute(select(Comment).where(Comment.id == comment_id))
    c = res.scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    c.is_deleted = 1
    c.updated_at = datetime.utcnow()
    await db.commit()
    return {"ok": True}
