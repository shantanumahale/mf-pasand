"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    ES_HOST: str = "localhost:9200"
    ES_INDEX: str = "mf-recommendations"
    OPENAI_API_KEY: str = ""
    EMBEDDING_PROVIDER: str = "local"  # "local" or "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMS: int = 384

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
