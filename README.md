# RG Rabbit

> **Part of the [ResonantGenesis](https://dev-swat.com) platform** — a private Reddit-like social platform for communities, posts, comments, voting, and image sharing.

[![Status: Production](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()
[![Docker: 5 Services](https://img.shields.io/badge/Docker-5%20Services-blue.svg)]()
[![Port: 8000](https://img.shields.io/badge/Port-8000-orange.svg)]()
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)]()
[![License: RG Source Available](https://img.shields.io/badge/License-RG%20Source%20Available-blue.svg)](LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Community-driven social platform built as a microservice suite. Communities (subreddits), threaded posts with image uploads, nested comments, upvote/downvote system, moderation tools, and Open Graph meta tags for social sharing. Deployed as 5 Docker containers on the Resonant Genesis platform.

**We welcome contributions!** See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## Architecture

```
Frontend (React)
  └── gateway (Nginx → FastAPI)
        ├── /rabbit/*          ──→ rabbit_api_service:8000
        └── /api/v1/rabbit/*   ──→ rabbit_api_service:8000

rabbit_api_service (main)
  ├── Communities  — create, list, get by slug
  ├── Posts        — CRUD, search, global feed, community feed, OG meta
  ├── Comments     — threaded/nested, per-post, per-author
  ├── Votes        — upvote/downvote on posts & comments
  ├── Images       — upload/download stored in DB (up to 10 MB)
  └── Alembic      — database migrations

rabbit_content_service     (stub — future content processing)
rabbit_community_service   (stub — future community management)
rabbit_vote_service        (stub — future vote aggregation)
rabbit_moderation_service  (stub — future moderation tools)
```

## Features

- **Communities** — Create communities with slugs, names, descriptions (like subreddits)
- **Posts** — Create, list, search, delete posts with text and/or images
- **Nested Comments** — Threaded comment system with parent references
- **Voting** — Upvote/downvote (+1, 0, -1) on posts and comments with score aggregation
- **Image Uploads** — Direct image upload to PostgreSQL (up to 10 MB), served with cache headers
- **Post Search** — Full-text search on post titles and bodies
- **Open Graph** — `/posts/{id}/og` serves HTML with OG meta tags for social sharing (Twitter, Discord, etc.)
- **Soft Deletes** — Posts and comments are soft-deleted, preserving data integrity
- **Post Locking** — Locked posts prevent new comments
- **Moderation Flags** — Comments can be marked as removed by moderators
- **Alembic Migrations** — Automatic schema migration on container startup

## Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| `rabbit_api_service` | 8000 | Main API — all CRUD, voting, images, OG | ✅ Production |
| `rabbit_content_service` | 8000 | Content processing (future) | Stub |
| `rabbit_community_service` | 8000 | Community management (future) | Stub |
| `rabbit_vote_service` | 8000 | Vote aggregation (future) | Stub |
| `rabbit_moderation_service` | 8000 | Moderation tools (future) | Stub |

## Source Files (rabbit_api_service)

| File | Size | Purpose |
|------|------|---------|
| `app/main.py` | 1.4KB | FastAPI app, router registration, DB init |
| `app/config.py` | 0.5KB | Settings — database URL, internal service URLs |
| `app/db.py` | 0.7KB | SQLAlchemy async engine + session factory |
| `app/deps.py` | 0.7KB | FastAPI dependencies — DB session, user auth |
| `app/models.py` | 4.3KB | SQLAlchemy models — Community, Post, Comment, Vote, RabbitImage |
| `app/schemas.py` | 1.6KB | Pydantic schemas — create/response models |
| `app/routers/posts.py` | 7.6KB | Post CRUD, search, OG meta, enrichment (scores, counts) |
| `app/routers/communities.py` | 2.3KB | Community CRUD |
| `app/routers/comments.py` | 4.2KB | Comment CRUD, nested threading |
| `app/routers/votes.py` | 2.0KB | Vote upsert (upvote/downvote/remove) |
| `app/routers/images.py` | 2.0KB | Image upload/download |

## Quick Start

```bash
# Clone
git clone git@github-devswat:DevSwat-ResonantGenesis/RG_Rabbit.git
cd RG_Rabbit

# Run locally (requires PostgreSQL with asyncpg)
cd rabbit_api_service
pip install -r requirements.txt
export RABBIT_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/rabbit"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

All 5 services are defined in the platform's `docker-compose.unified.yml`:

```bash
# Build all rabbit services
docker compose -f docker-compose.unified.yml build rabbit_api_service rabbit_content_service rabbit_community_service rabbit_vote_service rabbit_moderation_service

# Start
docker compose -f docker-compose.unified.yml up -d rabbit_api_service rabbit_content_service rabbit_community_service rabbit_vote_service rabbit_moderation_service
```

## Database

- **Engine**: PostgreSQL + asyncpg (async)
- **ORM**: SQLAlchemy 2.0 (mapped columns)
- **Migrations**: Alembic (auto-runs on container startup)
- **Tables**: `rabbit_communities`, `rabbit_posts`, `rabbit_comments`, `rabbit_votes`, `rabbit_images`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RABBIT_DATABASE_URL` | `postgresql+asyncpg://rabbit:rabbit@rabbit_db:5432/rabbit` | PostgreSQL connection string |
| `RABBIT_DB_POOL_CLASS` | `queue` | Set to `null` for NullPool (useful in Docker) |
| `RABBIT_CONTENT_URL` | `http://rabbit_content_service:8000` | Content service URL |
| `RABBIT_COMMUNITY_URL` | `http://rabbit_community_service:8000` | Community service URL |
| `RABBIT_VOTE_URL` | `http://rabbit_vote_service:8000` | Vote service URL |
| `RABBIT_MODERATION_URL` | `http://rabbit_moderation_service:8000` | Moderation service URL |
| `REDIS_URL` | `redis://shared_redis:6379/0` | Redis for caching |

## API Endpoints

### Communities (`/rabbit/communities`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/rabbit/communities` | Required | Create community |
| `GET` | `/rabbit/communities` | Optional | List all communities |
| `GET` | `/rabbit/communities/{slug}` | Optional | Get community by slug |

### Posts (`/rabbit/posts`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/rabbit/posts` | Required | Create post |
| `GET` | `/rabbit/posts` | Optional | Global feed (newest first) |
| `GET` | `/rabbit/posts/search?q=` | Optional | Search posts by title/body |
| `GET` | `/rabbit/posts/{id}` | Optional | Get single post |
| `GET` | `/rabbit/communities/{slug}/posts` | Optional | Posts in community |
| `GET` | `/rabbit/posts/{id}/og` | Public | Open Graph HTML for social sharing |
| `DELETE` | `/rabbit/posts/{id}` | Required | Soft-delete post (author only) |

### Comments (`/rabbit/posts/{id}/comments`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/rabbit/posts/{id}/comments` | Required | Create comment (supports nesting) |
| `GET` | `/rabbit/posts/{id}/comments` | Optional | List comments for post |
| `GET` | `/rabbit/comments` | Optional | List all comments (filter by author) |
| `DELETE` | `/rabbit/comments/{id}` | Required | Soft-delete comment (author only) |

### Votes (`/rabbit/votes`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `PUT` | `/rabbit/votes` | Required | Upsert vote (+1, 0, -1) on post or comment |

### Images (`/rabbit/images`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/rabbit/images/upload` | Required | Upload image (max 10 MB) |
| `GET` | `/rabbit/images/{key}` | Public | Download image |

### Health
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/rabbit/health` | Rabbit-specific health check |

## Authentication

Rabbit uses header-based auth via the gateway:
- **`X-User-Id`** header is injected by the gateway after JWT validation
- GET endpoints work without auth (public reads)
- POST/PUT/DELETE endpoints require a valid `X-User-Id`

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ideas for Contribution

- **Content Moderation** — Implement the `rabbit_moderation_service` with auto-mod rules, report system
- **Vote Aggregation** — Move vote score computation to `rabbit_vote_service` for real-time leaderboards
- **Community Management** — Add roles (admin, moderator, member), community rules, ban lists
- **Content Processing** — Markdown rendering, link previews, embed support
- **Search** — Full-text search with PostgreSQL tsvector or Elasticsearch
- **Notifications** — New comment, vote, reply notifications
- **User Profiles** — Karma, post history, saved posts
- **Flair & Tags** — Post flair, user flair, community tags
- **Pagination** — Cursor-based pagination for feeds
- **WebSocket** — Real-time updates for new posts/comments/votes

## Related Modules

| Module | Repo | Relationship |
|--------|------|-------------|
| Gateway | `genesis2026_production_backend/gateway` | Proxies `/rabbit/*` and `/api/v1/rabbit/*` to this service |
| Auth Service | `genesis2026_production_backend/auth_service` | JWT validation, provides `X-User-Id` header |
| Frontend | `genesis2026_frontend` | React UI for Rabbit (community pages, post feeds, comment threads) |

## Deployment Status

- **Status**: ✅ **Production** — deployed as 5 Docker containers
- **Extracted from**: `genesis2026_production_backend/rabbit_*_service/` (directories removed from monolith)
- **Server path**: `/home/deploy/RG_Rabbit` (cloned from DevSwat GitHub)
- **Docker services**: `rabbit_api_service`, `rabbit_content_service`, `rabbit_community_service`, `rabbit_vote_service`, `rabbit_moderation_service`
- **Port**: 8000 (internal Docker network)
- **Database**: PostgreSQL (shared platform DB or dedicated `rabbit` DB)

---

**Organization**: [DevSwat-ResonantGenesis](https://github.com/DevSwat-ResonantGenesis)
**Platform**: [dev-swat.com](https://dev-swat.com)
