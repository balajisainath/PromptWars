from .config import get_settings

REQUIRED_SECRETS = [
    "GEMINI_API_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "SECRET_KEY",
]


def check_required_secrets() -> None:
    settings = get_settings()
    missing = [key for key in REQUIRED_SECRETS if not getattr(settings, key, None)]
    if missing:
        raise RuntimeError(f"Missing required secrets: {', '.join(missing)}")
