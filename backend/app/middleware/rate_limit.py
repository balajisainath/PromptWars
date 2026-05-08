import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.redis import get_redis_client

RATE_LIMIT = 100
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        client = get_redis_client()
        key = f"ratelimit:{user_id}"
        now = time.time()
        window_start = now - WINDOW_SECONDS

        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(uuid.uuid4()): now})
        pipe.zcard(key)
        pipe.expire(key, WINDOW_SECONDS + 1)
        results = await pipe.execute()

        request_count = results[2]
        remaining = max(0, RATE_LIMIT - request_count)
        reset_at = int(now + WINDOW_SECONDS)

        if request_count > RATE_LIMIT:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(WINDOW_SECONDS),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response
