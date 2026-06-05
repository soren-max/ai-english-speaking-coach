from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Project
    project_name: str = "InterviewGPT"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interviewgpt"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/interviewgpt"

    # Auth
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # CORS
    cors_origins: str = '["http://localhost:3000"]'

    @property
    def cors_origin_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
