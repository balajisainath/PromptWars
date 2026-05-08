import hashlib
from typing import Optional
import httpx
from app.core.config import get_settings
from app.core.redis import get_cached_json, set_cached_json

OWM_BASE = "https://api.openweathermap.org/data/2.5"
CACHE_TTL = 21600  # 6 hours


def _cache_key(lat: float, lng: float, date: str) -> str:
    return "weather:" + hashlib.sha256(f"{lat:.4f}:{lng:.4f}:{date}".encode()).hexdigest()


async def get_forecast(lat: float, lng: float, date: str) -> Optional[dict]:
    settings = get_settings()
    if not settings.OPENWEATHER_API_KEY:
        return None

    key = _cache_key(lat, lng, date)
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{OWM_BASE}/forecast",
            params={"lat": lat, "lon": lng, "appid": settings.OPENWEATHER_API_KEY, "units": "metric", "cnt": 8},
        )
        resp.raise_for_status()
        data = resp.json()

    forecasts = data.get("list", [])
    if not forecasts:
        return None

    temps = [f["main"]["temp"] for f in forecasts]
    descriptions = [f["weather"][0]["description"] for f in forecasts if f.get("weather")]
    rain = sum(f.get("rain", {}).get("3h", 0) for f in forecasts)

    result = {
        "temp_min": min(temps),
        "temp_max": max(temps),
        "description": descriptions[0] if descriptions else "unknown",
        "precipitation_chance": min(round(rain * 10), 100),
    }
    await set_cached_json(key, result, CACHE_TTL)
    return result
