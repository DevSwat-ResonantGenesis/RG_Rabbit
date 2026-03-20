from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_user_id
from ..models import Community
from ..schemas import CommunityCreate, CommunityOut

router = APIRouter(prefix="/rabbit/communities", tags=["rabbit-communities"])


@router.post("", response_model=CommunityOut)
async def create_community(
    payload: CommunityCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    existing = await db.execute(select(Community).where(Community.slug == payload.slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Community slug already exists")

    c = Community(
        slug=payload.slug,
        name=payload.name,
        description=payload.description,
        created_by_user_id=user_id,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return CommunityOut(
        id=c.id,
        slug=c.slug,
        name=c.name,
        description=c.description,
        created_by_user_id=c.created_by_user_id,
        created_at=c.created_at,
    )


@router.get("", response_model=list[CommunityOut])
async def list_communities(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Community).order_by(Community.created_at.desc()).limit(200))
    items = res.scalars().all()
    return [
        CommunityOut(
            id=c.id,
            slug=c.slug,
            name=c.name,
            description=c.description,
            created_by_user_id=c.created_by_user_id,
            created_at=c.created_at,
        )
        for c in items
    ]


@router.get("/{slug}", response_model=CommunityOut)
async def get_community(slug: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Community).where(Community.slug == slug))
    c = res.scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Community not found")
    return CommunityOut(
        id=c.id,
        slug=c.slug,
        name=c.name,
        description=c.description,
        created_by_user_id=c.created_by_user_id,
        created_at=c.created_at,
    )
