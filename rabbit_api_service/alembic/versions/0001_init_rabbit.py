"""init rabbit

Revision ID: 0001_init_rabbit
Revises: 
Create Date: 2026-03-04

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_init_rabbit"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rabbit_communities",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_rabbit_communities_slug", "rabbit_communities", ["slug"], unique=True)

    op.create_table(
        "rabbit_posts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("community_id", sa.BigInteger(), sa.ForeignKey("rabbit_communities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("author_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_locked", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_rabbit_posts_community_id", "rabbit_posts", ["community_id"], unique=False)
    op.create_index("ix_rabbit_posts_author_user_id", "rabbit_posts", ["author_user_id"], unique=False)
    op.create_index("ix_rabbit_posts_created_at", "rabbit_posts", ["created_at"], unique=False)

    op.create_table(
        "rabbit_comments",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("post_id", sa.BigInteger(), sa.ForeignKey("rabbit_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_comment_id", sa.BigInteger(), sa.ForeignKey("rabbit_comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("author_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_removed_by_mod", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_rabbit_comments_post_id", "rabbit_comments", ["post_id"], unique=False)
    op.create_index("ix_rabbit_comments_parent_comment_id", "rabbit_comments", ["parent_comment_id"], unique=False)
    op.create_index("ix_rabbit_comments_author_user_id", "rabbit_comments", ["author_user_id"], unique=False)
    op.create_index("ix_rabbit_comments_created_at", "rabbit_comments", ["created_at"], unique=False)

    op.create_table(
        "rabbit_votes",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=16), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "target_type", "target_id", name="uq_rabbit_vote_user_target"),
    )
    op.create_index("ix_rabbit_votes_user_id", "rabbit_votes", ["user_id"], unique=False)
    op.create_index("ix_rabbit_votes_target_type", "rabbit_votes", ["target_type"], unique=False)
    op.create_index("ix_rabbit_votes_target_id", "rabbit_votes", ["target_id"], unique=False)
    op.create_index("ix_rabbit_votes_target", "rabbit_votes", ["target_type", "target_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rabbit_votes_target", table_name="rabbit_votes")
    op.drop_index("ix_rabbit_votes_target_id", table_name="rabbit_votes")
    op.drop_index("ix_rabbit_votes_target_type", table_name="rabbit_votes")
    op.drop_index("ix_rabbit_votes_user_id", table_name="rabbit_votes")
    op.drop_table("rabbit_votes")

    op.drop_index("ix_rabbit_comments_created_at", table_name="rabbit_comments")
    op.drop_index("ix_rabbit_comments_author_user_id", table_name="rabbit_comments")
    op.drop_index("ix_rabbit_comments_parent_comment_id", table_name="rabbit_comments")
    op.drop_index("ix_rabbit_comments_post_id", table_name="rabbit_comments")
    op.drop_table("rabbit_comments")

    op.drop_index("ix_rabbit_posts_created_at", table_name="rabbit_posts")
    op.drop_index("ix_rabbit_posts_author_user_id", table_name="rabbit_posts")
    op.drop_index("ix_rabbit_posts_community_id", table_name="rabbit_posts")
    op.drop_table("rabbit_posts")

    op.drop_index("ix_rabbit_communities_slug", table_name="rabbit_communities")
    op.drop_table("rabbit_communities")
