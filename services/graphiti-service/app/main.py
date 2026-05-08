from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import get_driver, close_driver
from app.routers import memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        driver = await get_driver()
        async with driver.session() as session:
            await session.run(
                "CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.user_id)"
            )
            await session.run(
                "CREATE INDEX place_name_idx IF NOT EXISTS FOR (p:Place) ON (p.name)"
            )
            await session.run(
                "CREATE INDEX activity_name_idx IF NOT EXISTS FOR (a:Activity) ON (a.name)"
            )
    except Exception:
        pass
    yield
    await close_driver()


app = FastAPI(title="Graphiti Memory Service", version="1.0.0", lifespan=lifespan)
app.include_router(memory.router, prefix="/memory")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "graphiti-service"}
