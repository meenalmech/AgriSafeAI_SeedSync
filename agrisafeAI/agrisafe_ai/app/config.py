from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgriSafe AI"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8011
    database_url: str = "sqlite:///./agrisafe.db"
    weather_provider: str = "open_meteo"
    request_timeout_seconds: int = 8
    demo_weather_enabled: bool = True
    llm_enabled: bool = False
    llm_provider: str = "none"
    llm_api_key: str = ""
    max_upload_mb: int = 10
    default_language: str = "ms"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
