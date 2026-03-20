from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, LargeBinary, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Community(Base):
    __tablename__ = "rabbit_communities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)

    posts: Mapped[list[Post]] = relationship("Post", back_populates="community")  # type: ignore[name-defined]


class Post(Base):
    __tablename__ = "rabbit_posts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("rabbit_communities.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    author_user_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Integer, default=0)

    community: Mapped[Community] = relationship("Community", back_populates="posts")  # type: ignore[name-defined]
    comments: Mapped[list[Comment]] = relationship("Comment", back_populates="post")  # type: ignore[name-defined]


class Comment(Base):
    __tablename__ = "rabbit_comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("rabbit_posts.id", ondelete="CASCADE"), index=True)
    parent_comment_id: Mapped[int | None] = mapped_column(ForeignKey("rabbit_comments.id", ondelete="CASCADE"), nullable=True, index=True)

    body: Mapped[str] = mapped_column(Text)

    author_user_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Integer, default=0)
    is_removed_by_mod: Mapped[bool] = mapped_column(Integer, default=0)

    post: Mapped[Post] = relationship("Post", back_populates="comments")  # type: ignore[name-defined]


class Vote(Base):
    __tablename__ = "rabbit_votes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(16), index=True)
    target_id: Mapped[int] = mapped_column(BigInteger, index=True)

    value: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_rabbit_vote_user_target"),
        Index("ix_rabbit_votes_target", "target_type", "target_id"),
    )


class RabbitImage(Base):
    __tablename__ = "rabbit_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(128), default="image/png")
    data: Mapped[bytes] = mapped_column(LargeBinary)
    size: Mapped[int] = mapped_column(BigInteger, default=0)
    uploaded_by: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
