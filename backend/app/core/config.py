from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MyAloca"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "myaloca-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    # Default to local SQLite via aiosqlite, override with postgresql+asyncpg:// in production
    DATABASE_URL: str = "sqlite+aiosqlite:///./myaloca.db"

    # Business Rules
    CHECKIN_TOLERANCE_MINUTES: int = 30  # Auto-release if no check-in after start_time + 30 min
    CHECKIN_EARLY_MINUTES: int = 15     # Allow check-in up to 15 min before start_time

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
