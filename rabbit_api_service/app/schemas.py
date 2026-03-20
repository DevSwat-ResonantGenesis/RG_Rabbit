from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CommunityCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=128)
    description: str | None = None


class CommunityOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None
    created_by_user_id: str
    created_at: datetime


class PostCreate(BaseModel):
    community_slug: str
    title: str = Field(min_length=1, max_length=300)
    body: str | None = None
    image_url: str | None = None


class PostOut(BaseModel):
    id: int
    community_id: int
    community_slug: str | None = None
    title: str
    body: str | None
    image_url: str | None = None
    author_user_id: str
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool
    is_locked: bool
    vote_score: int = 0
    comment_count: int = 0


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)
    parent_comment_id: int | None = None


class CommentOut(BaseModel):
    id: int
    post_id: int
    parent_comment_id: int | None
    body: str
    author_user_id: str
    created_at: datetime
    updated_at: datetime | None
    is_deleted: bool
    is_removed_by_mod: bool


VoteTargetType = Literal["post", "comment"]


class VoteUpsert(BaseModel):
    target_type: VoteTargetType
    target_id: int
    value: int


class VoteOut(BaseModel):
    user_id: str
    target_type: VoteTargetType
    target_id: int
    value: int
    created_at: datetime
    updated_at: datetime | None
