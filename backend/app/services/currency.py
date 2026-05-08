import hashlib
from typing import Optional
import httpx
from app.core.redis import get_cached_json, set_cached_json

RATES_BASE = "https://api.exchangerate.host/latest"
CACHE_TTL = 3600  # 1 hour


async def get_rates(base_currency: str = "USD") -> dict:
    key = f"currency:rates:{base_currency}"
    cached = await get_cached_json(key)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(RATES_BASE, params={"base": base_currency})
        resp.raise_for_status()
        data = resp.json()

    rates = data.get("rates", {})
    await set_cached_json(key, rates, CACHE_TTL)
    return rates


async def convert(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return amount
    rates = await get_rates(from_currency)
    rate = rates.get(to_currency)
    if rate is None:
        raise ValueError(f"No exchange rate for {to_currency}")
    return round(amount * rate, 2)
