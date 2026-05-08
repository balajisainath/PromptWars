from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AI
    GEMINI_API_KEY: str = ""

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""

    # Firebase
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_WEB_API_KEY: str = ""

    # Weather
    OPENWEATHER_API_KEY: str = ""

    # Amadeus
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://travelai:travelai_secret@localhost:5432/travelai"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: str = "http://localhost:6333"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "graphiti_secret"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://travelai:rabbitmq_secret@localhost:5672/"

    # Backend
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEV_MODE: bool = False

    # Internal services
    GEO_SERVICE_URL: str = "http://geo-service:8080"
    GRAPHITI_SERVICE_URL: str = "http://graphiti-service:8001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
