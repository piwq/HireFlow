from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://hr:hr_pass@localhost:5432/hrdb"
    secret_key: str = "super-secret-key-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "resumes"
    minio_public_url: str = "http://localhost:9000"

    livekit_api_key: str = "devkey"
    livekit_api_secret: str = "secret"

    gemini_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_bot_username: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
