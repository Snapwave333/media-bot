from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Music Video SaaS"
    debug: bool = False
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/musicvideo_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Storage
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    temp_dir: str = "./temp"
    max_file_size_mb: int = 100

    # AI Services
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Video Generation (optional integrations)
    runway_api_key: str = ""
    kaiber_api_key: str = ""
    replicate_api_token: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_single_video: str = ""  # Price ID for $50 single video
    stripe_price_subscription: str = ""   # Price ID for subscription

    # Video Settings
    default_video_width: int = 1920
    default_video_height: int = 1080
    default_fps: int = 30
    clip_duration_seconds: float = 2.0

    # JWT Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
