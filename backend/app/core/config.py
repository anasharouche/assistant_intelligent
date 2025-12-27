from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # --- App ---
    app_name: str = Field(default="Assistant Scolarite API", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # --- Database ---
    database_url: str = Field(alias="DATABASE_URL")

    # --- CORS ---
    cors_allowed_origins: str = Field(
        default="http://localhost:19006,http://127.0.0.1:19006",
        alias="CORS_ALLOWED_ORIGINS",
    )

    # --- JWT ---
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=120, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")


    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Helpers ---
    def cors_origins_list(self) -> list[str]:
        return [
            o.strip()
            for o in self.cors_allowed_origins.split(",")
            if o.strip()
        ]

settings = Settings()
