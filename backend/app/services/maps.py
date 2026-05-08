import hashlib
import json
import asyncio
from typing import Optional, List
import httpx
from app.core.config import get_settings
from app.core.redis import get_cached_json, set_cached_json

MAPS_BASE = "https://maps.googleapis.com/maps/api"
CACHE_TTL = 86400  # 24 hours


def _cache_key(*parts) -> str:
    return "maps:" + hashlib.sha256(":".join(str(p) for p in parts).encode()).hexdigest()


async def _get_with_backoff(url: str, params: dict) -> dict:
    settings = get_settings()
    params["key"] = settings.GOOGLE_MAPS_API_KEY

    for attempt in range(4):
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 429:
                await asyncio.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
    raise RuntimeError("Google Maps API quota exceeded after retries")


async def places_text_search(query: str, lat: Optional[float] = None, lng: Optional[float] = None) -> List[dict]:
    key = _cache_key("places_text", query, lat, lng)
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    params: dict = {"query": query}
    if lat and lng:
        params["location"] = f"{lat},{lng}"
        params["radius"] = 50000

    data = await _get_with_backoff(f"{MAPS_BASE}/place/textsearch/json", params)
    results = data.get("results", [])
    await set_cached_json(key, results, CACHE_TTL)
    return results


async def place_details(place_id: str) -> dict:
    key = _cache_key("place_details", place_id)
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    data = await _get_with_backoff(
        f"{MAPS_BASE}/place/details/json",
        {"place_id": place_id, "fields": "name,formatted_address,geometry,types,rating,price_level"},
    )
    result = data.get("result", {})
    await set_cached_json(key, result, CACHE_TTL)
    return result


async def geocode(address: str) -> dict:
    key = _cache_key("geocode", address)
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    data = await _get_with_backoff(f"{MAPS_BASE}/geocode/json", {"address": address})
    results = data.get("results", [])
    result = results[0] if results else {}
    await set_cached_json(key, result, CACHE_TTL)
    return result
