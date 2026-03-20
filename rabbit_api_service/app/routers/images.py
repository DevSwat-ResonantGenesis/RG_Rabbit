"""Rabbit image upload/download — stores images directly in the database."""
from __future__ import annotations

import re
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_user_id
from ..models import RabbitImage

router = APIRouter(prefix="/rabbit", tags=["rabbit-images"])

MAX_SIZE = 10 * 1024 * 1024  # 10 MB


def _safe_key(filename: str) -> str:
    ts = int(time.time() * 1000)
    clean = re.sub(r"[^a-zA-Z0-9._-]", "_", filename or "image.png")
    return f"rabbit/{ts}_{clean}"


@router.post("/images/upload")
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Image must be under 10 MB")

    key = _safe_key(file.filename or "image.png")

    img = RabbitImage(
        key=key,
        content_type=file.content_type or "image/png",
        data=data,
        size=len(data),
        uploaded_by=user_id,
    )
    db.add(img)
    await db.commit()

    return {"key": key, "url": f"/api/v1/rabbit/images/{key}", "size": len(data)}


@router.get("/images/{key:path}")
async def download_image(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(RabbitImage).where(RabbitImage.key == key))
    img = res.scalar_one_or_none()
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=img.data,
        media_type=img.content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )
