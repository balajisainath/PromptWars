from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings


def add_cors_middleware(app) -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=600,
    )
