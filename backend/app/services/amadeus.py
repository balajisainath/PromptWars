import hashlib
from typing import Optional, List
import httpx
from app.core.config import get_settings
from app.core.redis import get_cached, set_cached, get_cached_json, set_cached_json

AMADEUS_BASE = "https://test.api.amadeus.com"


async def _get_access_token() -> str:
    settings = get_settings()
    if not settings.AMADEUS_CLIENT_ID:
        return ""

    cached = await get_cached("amadeus:token")
    if cached:
        return cached

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{AMADEUS_BASE}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_CLIENT_ID,
                "client_secret": settings.AMADEUS_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    token = data["access_token"]
    await set_cached("amadeus:token", token, ttl=1799)
    return token


async def search_flights(origin: str, destination: str, date: str, adults: int = 1) -> List[dict]:
    key = "amadeus:flights:" + hashlib.sha256(f"{origin}:{destination}:{date}:{adults}".encode()).hexdigest()
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    token = await _get_access_token()
    if not token:
        return []

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{AMADEUS_BASE}/v2/shopping/flight-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={"originLocationCode": origin, "destinationLocationCode": destination,
                    "departureDate": date, "adults": adults, "max": 5},
        )
        if resp.status_code != 200:
            return []
        data = resp.json()

    results = data.get("data", [])
    await set_cached_json(key, results, ttl=3600)
    return results
