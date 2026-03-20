# Contributing to RG Rabbit

Thank you for your interest in contributing to RG Rabbit! We welcome pull requests, bug reports, feature suggestions, and documentation improvements from the community.

## Getting Started

1. **Fork** this repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RG_Rabbit.git
   cd RG_Rabbit
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up the development environment**:
   ```bash
   cd rabbit_api_service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Run locally** (requires PostgreSQL):
   ```bash
   export RABBIT_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/rabbit"
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Development Guidelines

### Code Style

- **Python 3.11+** — use modern type hints (`str | None` instead of `Optional[str]`)
- **FastAPI** — async endpoints, Pydantic models for request/response validation
- **SQLAlchemy 2.0** — mapped columns, async sessions
- Follow existing patterns in the codebase for consistency
- Keep functions focused and small
- Use descriptive variable and function names

### Project Structure

```
RG_Rabbit/
├── rabbit_api_service/        # Main API (this is where most work happens)
│   ├── app/
│   │   ├── main.py            # FastAPI app + router registration
│   │   ├── config.py          # Settings (env vars)
│   │   ├── db.py              # SQLAlchemy engine + session
│   │   ├── deps.py            # FastAPI dependencies (auth, DB)
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   └── routers/           # API route handlers
│   ├── alembic/               # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── rabbit_content_service/    # Stub — content processing (open for implementation!)
├── rabbit_community_service/  # Stub — community management (open for implementation!)
├── rabbit_vote_service/       # Stub — vote aggregation (open for implementation!)
└── rabbit_moderation_service/ # Stub — moderation tools (open for implementation!)
```

### Adding New Endpoints

1. Add your Pydantic schema to `app/schemas.py`
2. Add any new ORM models to `app/models.py`
3. Create or extend a router in `app/routers/`
4. Register the router in `app/main.py` if it's new
5. Create an Alembic migration if you changed models:
   ```bash
   cd rabbit_api_service
   alembic revision --autogenerate -m "description of change"
   ```

### Implementing a Stub Service

The 4 stub services (`content`, `community`, `vote`, `moderation`) are ready for community implementation. To implement one:

1. Add `app/models.py`, `app/config.py`, `app/db.py`, `app/deps.py` (copy patterns from `rabbit_api_service`)
2. Add routers in `app/routers/`
3. Update `requirements.txt` if new dependencies are needed
4. Add Alembic migrations if the service needs its own database tables
5. Document your changes in the PR

### Database Migrations

We use Alembic for schema changes:

```bash
cd rabbit_api_service

# Create a new migration
alembic revision --autogenerate -m "add user_profiles table"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Pull Request Process

1. **Test your changes** locally before submitting
2. **Keep PRs focused** — one feature or fix per PR
3. **Write clear commit messages** — describe what and why
4. **Update documentation** if your change affects the API or configuration
5. **Don't break existing endpoints** — backward compatibility is important
6. **Add yourself** to the contributors list in your PR if you'd like

### PR Title Format

```
feat: add user profiles endpoint
fix: correct vote score aggregation
docs: update API endpoint documentation
refactor: extract comment enrichment logic
```

### What We Look For in Reviews

- Does it follow existing code patterns?
- Is it properly typed with Pydantic models?
- Are database queries efficient (proper indexes, joins)?
- Does it handle errors gracefully?
- Is it backward-compatible?

## Reporting Bugs

Open an issue on GitHub with:

1. **Description** — What happened vs. what you expected
2. **Steps to reproduce** — How to trigger the bug
3. **Environment** — Python version, OS, Docker version if applicable
4. **Logs** — Any relevant error messages or stack traces

## Feature Requests

Open an issue with the `enhancement` label. Describe:

1. **The problem** you're trying to solve
2. **Your proposed solution**
3. **Alternatives** you've considered

## Areas Open for Contribution

These are high-impact areas where community help is especially welcome:

- **Moderation System** — Auto-mod rules, user reports, mod queue, ban system
- **Vote Aggregation** — Real-time score computation, hot/top/new sorting algorithms
- **Community Features** — Roles, rules, flairs, custom themes
- **Content Processing** — Markdown rendering, link previews, embed cards
- **Full-Text Search** — PostgreSQL tsvector indexing or Elasticsearch integration
- **Notifications** — Real-time notifications for replies, votes, mentions
- **User Profiles** — Karma tracking, post/comment history, saved posts
- **Rate Limiting** — Per-user rate limits for posts, comments, votes
- **WebSocket Updates** — Real-time feed updates without polling
- **Testing** — Unit tests, integration tests, API test suite

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on the code, not the person
- Welcome newcomers and help them get started
- No harassment, discrimination, or toxic behavior

## License

By contributing to RG Rabbit, you agree that your contributions will be licensed under the [RG Source Available License](LICENSE.txt). See Section 5 of the license for contribution terms.

## Questions?

- Open an issue on GitHub
- Visit [dev-swat.com](https://dev-swat.com)
- Email: contact@dev-swat.com

Thank you for helping make Rabbit better!
