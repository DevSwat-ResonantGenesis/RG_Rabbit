from fastapi import FastAPI

from .config import settings
from .db import create_engine, create_sessionmaker
from .routers.communities import router as communities_router
from .routers.posts import router as posts_router
from .routers.comments import router as comments_router
from .routers.votes import router as votes_router
from .routers.images import router as images_router

app = FastAPI(title="Rabbit API")


@app.on_event("startup")
async def _startup() -> None:
    engine = create_engine(settings.RABBIT_DATABASE_URL)
    app.state.engine = engine
    app.state.sessionmaker = create_sessionmaker(engine)
    # Auto-create rabbit_images table if it doesn't exist
    from .db import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def _shutdown() -> None:
    engine = getattr(app.state, "engine", None)
    if engine is not None:
        await engine.dispose()


app.include_router(communities_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(votes_router)
app.include_router(images_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rabbit_api", "env": settings.ENV}


@app.get("/rabbit/health")
async def rabbit_health():
    return {"status": "healthy", "service": "rabbit_api", "env": settings.ENV}
