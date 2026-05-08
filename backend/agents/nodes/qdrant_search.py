from agents.state import TravelPlannerState
from agents.cache import get_cached_embedding, set_cached_embedding
from app.core.config import get_settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def _get_embedding(text: str, settings) -> list:
    cached = get_cached_embedding(text)
    if cached:
        return cached
    embedder = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GEMINI_API_KEY,
    )
    vector = embedder.embed_query(text)
    set_cached_embedding(text, vector)
    return vector


def qdrant_search_node(state: TravelPlannerState) -> TravelPlannerState:
    settings = get_settings()
    params = state["trip_params"]
    activities = params.get("activities", [])
    if isinstance(activities, list):
        activities_str = " ".join(activities)
    else:
        activities_str = str(activities)
    query = f"{params.get('destination', '')} {params.get('travel_style', '')} {activities_str}"

    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        vector = _get_embedding(query, settings)
        existing = {c.name for c in client.get_collections().collections}

        results = []
        for collection in ["destinations", "itineraries"]:
            if collection not in existing:
                client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                continue
            hits = client.search(collection_name=collection, query_vector=vector, limit=5)
            results.extend([
                {"score": h.score, "payload": h.payload, "collection": collection}
                for h in hits
            ])

        results.sort(key=lambda x: x["score"], reverse=True)
        state["similar_itineraries"] = results[:10]
    except Exception:
        state["similar_itineraries"] = []

    return state
