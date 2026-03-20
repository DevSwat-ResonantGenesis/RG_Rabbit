from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "production"

    RABBIT_DATABASE_URL: str = "postgresql+asyncpg://rabbit:rabbit@rabbit_db:5432/rabbit"

    RABBIT_CONTENT_URL: str = "http://rabbit_content_service:8000"
    RABBIT_COMMUNITY_URL: str = "http://rabbit_community_service:8000"
    RABBIT_VOTE_URL: str = "http://rabbit_vote_service:8000"
    RABBIT_MODERATION_URL: str = "http://rabbit_moderation_service:8000"


settings = Settings()
