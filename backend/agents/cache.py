import hashlib
import json
import redis as redis_lib
from app.core.config import get_settings


def _get_client():
    settings = get_settings()
    return redis_lib.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def get_cached_llm(prompt: str) -> dict | None:
    try:
        raw = _get_client().get(f"llm:{_hash(prompt)}")
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set_cached_llm(prompt: str, result: dict, ttl: int = 3600) -> None:
    try:
        _get_client().setex(f"llm:{_hash(prompt)}", ttl, json.dumps(result))
    except Exception:
        pass


def get_cached_embedding(text: str) -> list | None:
    try:
        raw = _get_client().get(f"emb:{_hash(text)}")
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set_cached_embedding(text: str, vector: list, ttl: int = 604800) -> None:
    try:
        _get_client().setex(f"emb:{_hash(text)}", ttl, json.dumps(vector))
    except Exception:
        pass
