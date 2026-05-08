import json
from agents.state import TravelPlannerState
from agents.cache import get_cached_llm, set_cached_llm
from app.core.config import get_settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

SYSTEM_PROMPT = (
    "You are an expert travel planner. Generate detailed, realistic day-by-day itineraries. "
    "Always respond with valid JSON matching this schema exactly:\n"
    '{"destination": str, "total_cost": float, "currency": str, "days": ['
    '{"day_number": int, "date": str|null, "summary": str, "activities": ['
    '{"name": str, "description": str, "location": str, "lat": float|null, "lng": float|null, '
    '"start_time": "HH:MM", "end_time": "HH:MM", "duration_minutes": int, '
    '"estimated_cost": float, "activity_type": str, "booking_url": str|null}]}]}'
)


def planner_node(state: TravelPlannerState) -> TravelPlannerState:
    settings = get_settings()
    params = state["trip_params"]

    context_parts = []
    if state.get("user_context"):
        context_parts.append(f"User preferences: {state['user_context']}")
    if state.get("similar_itineraries"):
        context_parts.append(f"Similar trips found: {len(state['similar_itineraries'])} references")
    if state.get("validation_result") and state.get("iteration_count", 0) > 0:
        issues = state["validation_result"].get("issues", [])
        if issues:
            context_parts.append(f"Fix these issues from previous attempt: {', '.join(issues)}")

    activities = params.get("activities", ["sightseeing"])
    if isinstance(activities, list):
        activities_str = ", ".join(activities)
    else:
        activities_str = str(activities)

    user_msg = (
        f"Plan a trip to {params.get('destination')}.\n"
        f"Duration: {params.get('start_date')} to {params.get('end_date')} "
        f"({params.get('duration_days', 3)} days)\n"
        f"Budget: {params.get('budget', 'flexible')} {params.get('currency', 'USD')} "
        f"for {params.get('group_size', 1)} people\n"
        f"Style: {params.get('travel_style', 'balanced')}\n"
        f"Activities: {activities_str}\n"
        + ("\n".join(context_parts) + "\n" if context_parts else "")
        + "Return ONLY the JSON itinerary, no markdown."
    )

    cached = get_cached_llm(user_msg)
    if cached:
        state["draft_itinerary"] = cached
        return state

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
        )
        response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_msg)])
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        itinerary = json.loads(text)
        set_cached_llm(user_msg, itinerary)
        state["draft_itinerary"] = itinerary
    except Exception as e:
        state["error"] = f"Planning failed: {e}"

    return state
