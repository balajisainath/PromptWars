import json
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.database import get_driver

router = APIRouter(tags=["memory"])

TRAVEL_ENTITIES = {
    "beach": "activity", "mountain": "destination_type", "city": "destination_type",
    "museum": "activity", "food": "preference", "hiking": "activity",
    "luxury": "preference", "budget": "preference", "adventure": "style",
    "relaxation": "style", "culture": "style", "shopping": "activity",
    "nightlife": "activity", "family": "preference", "solo": "preference",
    "resort": "accommodation", "hostel": "accommodation", "hotel": "accommodation",
    "nature": "destination_type", "urban": "destination_type", "rural": "destination_type",
}


class StoreRequest(BaseModel):
    user_id: str
    text: str
    memory_type: str = "preference"
    metadata: Optional[dict] = None


class ContextResponse(BaseModel):
    context: str
    nodes: list


@router.post("/store", status_code=201)
async def store_memory(req: StoreRequest):
    driver = await get_driver()
    entities = _extract_entities(req.text)

    async with driver.session() as session:
        await session.run(
            "MERGE (u:User {user_id: $user_id}) SET u.updated_at = datetime()",
            user_id=req.user_id,
        )
        await session.run(
            """
            MATCH (u:User {user_id: $user_id})
            CREATE (m:Memory {text: $text, type: $type, created_at: datetime(), metadata: $metadata})
            CREATE (u)-[:HAS_MEMORY]->(m)
            """,
            user_id=req.user_id,
            text=req.text,
            type=req.memory_type,
            metadata=json.dumps(req.metadata or {}),
        )
        for entity in entities:
            await session.run(
                """
                MERGE (e:Entity {name: $name, type: $etype})
                WITH e
                MATCH (u:User {user_id: $user_id})
                MERGE (u)-[:INTERESTED_IN]->(e)
                """,
                name=entity["name"],
                etype=entity["type"],
                user_id=req.user_id,
            )

    return {"status": "stored", "entities_extracted": len(entities)}


@router.get("/context", response_model=ContextResponse)
async def get_context(user_id: str, query: str):
    driver = await get_driver()

    async with driver.session() as session:
        mem_result = await session.run(
            """
            MATCH (u:User {user_id: $user_id})-[:HAS_MEMORY]->(m:Memory)
            RETURN m.text as text, m.type as type
            ORDER BY m.created_at DESC LIMIT 20
            """,
            user_id=user_id,
        )
        memories = [r.data() async for r in mem_result]

        ent_result = await session.run(
            """
            MATCH (u:User {user_id: $user_id})-[:INTERESTED_IN]->(e:Entity)
            RETURN e.name as name, e.type as type LIMIT 20
            """,
            user_id=user_id,
        )
        entities = [r.data() async for r in ent_result]

    context_parts = []
    if entities:
        interests = [f"{e['name']} ({e['type']})" for e in entities]
        context_parts.append(f"User interests: {', '.join(interests)}")
    if memories:
        recent = [m["text"] for m in memories[:5]]
        context_parts.append(f"Recent travel memories: {' | '.join(recent)}")

    context = "\n".join(context_parts) if context_parts else "No prior travel history found."
    nodes = [{"type": "entity", **e} for e in entities]
    nodes += [{"type": "memory", "text": m["text"]} for m in memories[:5]]

    return ContextResponse(context=context, nodes=nodes)


def _extract_entities(text: str) -> list:
    text_lower = text.lower()
    return [
        {"name": kw, "type": etype}
        for kw, etype in TRAVEL_ENTITIES.items()
        if kw in text_lower
    ]
