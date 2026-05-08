import httpx
from agents.state import TravelPlannerState
from app.core.config import get_settings


def graphiti_context_node(state: TravelPlannerState) -> TravelPlannerState:
    settings = get_settings()
    user_id = state["user_id"]
    destination = state["trip_params"].get("destination", "")

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"{settings.GRAPHITI_SERVICE_URL}/memory/context",
                params={"user_id": user_id, "query": f"travel preferences for {destination}"},
            )
            if resp.status_code == 200:
                state["user_context"] = resp.json().get("context", "")
            else:
                state["user_context"] = ""
    except Exception:
        state["user_context"] = ""

    return state
