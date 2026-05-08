from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.cors import add_cors_middleware
from app.api.v1 import auth, trips, itineraries, destinations
import structlog
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))
    yield


settings = get_settings()

app = FastAPI(
    title="AI Travel Planning Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)
add_cors_middleware(app)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(itineraries.router, prefix="/api/v1")
app.include_router(destinations.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "travel-ai-backend"}
