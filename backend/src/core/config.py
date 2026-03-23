from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development")
    app_secret_key: str = Field(default="change-me-in-production-32chars-min")
    log_level: str = Field(default="info")

    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_database: str = Field(default="rift")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Temporal
    temporal_host: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default")
    temporal_task_queue: str = Field(default="rift-main")

    # Auth
    jwt_secret: str = Field(default="change-me-jwt-secret-32chars-minimum")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=1440)

    # KMS
    kms_key_ref: str = Field(default="local-dev-key")
    kms_provider: str = Field(default="local")

    # Object Storage
    object_store_endpoint: str = Field(default="http://localhost:9000")
    object_store_bucket: str = Field(default="rift-artifacts")
    object_store_access_key: str = Field(default="minioadmin")
    object_store_secret_key: str = Field(default="minioadmin")
    object_store_region: str = Field(default="us-east-1")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_cors_origins: list[str] = Field(default=["http://localhost:5173"])


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
