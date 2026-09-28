from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    demo_mode: bool = True
    database_url: str = "sqlite:///./sev.db"
    redis_url: str = "redis://localhost:6379/0"
    faa_notam_base_url: str = "https://aviationweather.gov"
    awc_base_url: str = "https://aviationweather.gov/api/data"
    request_timeout_seconds: float = 10
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()
