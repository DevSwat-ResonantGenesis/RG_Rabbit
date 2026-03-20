from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_user_id
from ..models import Comment, Community, Post, Vote
from ..schemas import PostCreate, PostOut

router = APIRouter(prefix="/rabbit", tags=["rabbit-posts"])


async def _enrich_posts(posts: list[Post], db: AsyncSession) -> list[PostOut]:
    """Add vote_score, comment_count, and community_slug to a list of posts."""
    if not posts:
        return []

    post_ids = [p.id for p in posts]
    community_ids = list({p.community_id for p in posts})

    # Fetch community slugs
    cres = await db.execute(select(Community).where(Community.id.in_(community_ids)))
    cmap = {c.id: c.slug for c in cres.scalars().all()}

    # Aggregate vote scores
    vres = await db.execute(
        select(Vote.target_id, func.coalesce(func.sum(Vote.value), 0))
        .where(Vote.target_type == "post", Vote.target_id.in_(post_ids))
        .group_by(Vote.target_id)
    )
    vote_map = {row[0]: int(row[1]) for row in vres.all()}

    # Aggregate comment counts
    ccres = await db.execute(
        select(Comment.post_id, func.count(Comment.id))
        .where(Comment.post_id.in_(post_ids), Comment.is_deleted == 0)
        .group_by(Comment.post_id)
    )
    cc_map = {row[0]: int(row[1]) for row in ccres.all()}

    return [
        PostOut(
            id=p.id,
            community_id=p.community_id,
            community_slug=cmap.get(p.community_id),
            title=p.title,
            body=p.body,
            image_url=getattr(p, "image_url", None),
            author_user_id=p.author_user_id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            is_deleted=bool(p.is_deleted),
            is_locked=bool(p.is_locked),
            vote_score=vote_map.get(p.id, 0),
            comment_count=cc_map.get(p.id, 0),
        )
        for p in posts
    ]


@router.post("/posts", response_model=PostOut)
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    res = await db.execute(select(Community).where(Community.slug == payload.community_slug))
    community = res.scalar_one_or_none()
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    p = Post(
        community_id=community.id,
        title=payload.title,
        body=payload.body,
        image_url=payload.image_url,
        author_user_id=user_id,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    enriched = await _enrich_posts([p], db)
    return enriched[0]


@router.get("/posts", response_model=list[PostOut])
async def list_all_posts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Global feed — all posts across all communities, newest first."""
    pres = await db.execute(
        select(Post)
        .where(Post.is_deleted == 0)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return await _enrich_posts(list(pres.scalars().all()), db)


@router.get("/posts/search", response_model=list[PostOut])
async def search_posts(
    q: str = Query(min_length=1, max_length=200),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Search posts by title or body content."""
    pattern = f"%{q}%"
    pres = await db.execute(
        select(Post)
        .where(
            Post.is_deleted == 0,
            (Post.title.ilike(pattern)) | (Post.body.ilike(pattern)),
        )
        .order_by(Post.created_at.desc())
        .limit(limit)
    )
    return await _enrich_posts(list(pres.scalars().all()), db)


@router.get("/posts/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Post).where(Post.id == post_id))
    p = res.scalar_one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Post not found")
    enriched = await _enrich_posts([p], db)
    return enriched[0]


@router.get("/communities/{slug}/posts", response_model=list[PostOut])
async def list_posts_for_community(
    slug: str,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    cres = await db.execute(select(Community).where(Community.slug == slug))
    community = cres.scalar_one_or_none()
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    pres = await db.execute(
        select(Post)
        .where(Post.community_id == community.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return await _enrich_posts(list(pres.scalars().all()), db)


@router.get("/posts/{post_id}/og", response_class=HTMLResponse)
async def post_og_page(post_id: int, db: AsyncSession = Depends(get_db)):
    """Serve HTML with Open Graph meta tags for social media sharing."""
    res = await db.execute(select(Post).where(Post.id == post_id))
    p = res.scalar_one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get community slug
    cres = await db.execute(select(Community).where(Community.id == p.community_id))
    community = cres.scalar_one_or_none()
    c_name = community.name if community else "Rabbit"

    import html as html_mod
    title = html_mod.escape(p.title or "Rabbit Post")
    desc = html_mod.escape((p.body or "")[:200]) or f"Posted in {html_mod.escape(c_name)}"
    site_url = "https://resonantgenesis.xyz"
    post_url = f"{site_url}/rabbit?post={post_id}"
    image_url = ""
    if p.image_url:
        img = p.image_url if p.image_url.startswith("http") else f"{site_url}{p.image_url}"
        image_url = html_mod.escape(img)

    og_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title} - Rabbit Social</title>
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{post_url}">
<meta property="og:site_name" content="Rabbit Social – ResonantGenesis">
{f'<meta property="og:image" content="{image_url}">' if image_url else ''}
<meta name="twitter:card" content="{"summary_large_image" if image_url else "summary"}">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
{f'<meta name="twitter:image" content="{image_url}">' if image_url else ''}
<meta http-equiv="refresh" content="0;url={post_url}">
</head>
<body>
<p>Redirecting to <a href="{post_url}">{title}</a>...</p>
</body>
</html>"""
    return HTMLResponse(content=og_html)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    res = await db.execute(select(Post).where(Post.id == post_id))
    p = res.scalar_one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if p.author_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    p.is_deleted = 1
    p.updated_at = datetime.utcnow()
    await db.commit()
    return {"ok": True}
