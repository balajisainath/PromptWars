import json
from agents.state import TravelPlannerState
from agents.cache import get_cached_llm, set_cached_llm
from app.core.config import get_settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


def intent_extraction_node(state: TravelPlannerState) -> TravelPlannerState:
    settings = get_settings()
    params = state["trip_params"]

    prompt = (
        f"Extract structured travel intent from this trip description.\n"
        f"Trip: destination={params.get('destination')}, description={params.get('description')},\n"
        f"budget={params.get('budget')} {params.get('currency', 'USD')},\n"
        f"group_size={params.get('group_size')}, travel_style={params.get('travel_style')},\n"
        f"dates: {params.get('start_date')} to {params.get('end_date')}\n\n"
        f"Return ONLY valid JSON with keys: destination_type, activities (list), "
        f"budget_level (budget/mid/luxury), travel_style, duration_days (int), special_requirements (list)"
    )

    cached = get_cached_llm(prompt)
    if cached:
        state["trip_params"] = {**state["trip_params"], **cached}
        return state

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        intent = json.loads(text)
        set_cached_llm(prompt, intent)
        state["trip_params"] = {**state["trip_params"], **intent}
    except Exception as e:
        state["error"] = f"Intent extraction failed: {e}"

    return state
