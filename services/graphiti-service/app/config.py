from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "graphiti_secret"
    GEMINI_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
