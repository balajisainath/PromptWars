import hashlib
import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.firebase import verify_firebase_token
from app.core.redis import get_redis_client

EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/api/v1/auth/verify"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        from app.core.config import get_settings
        from app.core.firebase import DEV_CLAIMS, _firebase_configured
        settings = get_settings()

        auth_header = request.headers.get("Authorization", "")

        # In dev mode with no token, inject the demo user automatically
        if (settings.DEV_MODE or not _firebase_configured) and not auth_header:
            request.state.user_id = DEV_CLAIMS["uid"]
            request.state.user_email = DEV_CLAIMS["email"]
            return await call_next(request)

        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing authentication token"}, status_code=401)

        token = auth_header[len("Bearer "):]
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        cache_key = f"token:{token_hash}"

        client = get_redis_client()
        cached_raw = await client.get(cache_key)

        if cached_raw:
            claims = json.loads(cached_raw)
        else:
            try:
                claims = verify_firebase_token(token)
            except Exception as exc:
                return JSONResponse({"detail": str(exc)}, status_code=401)

            ttl = max(int(claims.get("exp", time.time() + 3600) - time.time()), 60)
            await client.setex(cache_key, ttl, json.dumps(claims))

        request.state.user_id = claims.get("uid", "")
        request.state.user_email = claims.get("email", "")
        return await call_next(request)
