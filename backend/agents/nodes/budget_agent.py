import json
from agents.state import TravelPlannerState
from agents.cache import get_cached_llm, set_cached_llm
from app.core.config import get_settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


def budget_agent_node(state: TravelPlannerState) -> TravelPlannerState:
    draft = state.get("draft_itinerary")
    if not draft:
        return state

    budget = state["trip_params"].get("budget")
    if not budget:
        return state

    total = draft.get("total_cost", 0) or 0
    if total <= float(budget) * 1.1:
        return state

    settings = get_settings()
    prompt = (
        f"This itinerary costs {total} but the budget is {budget} {draft.get('currency', 'USD')}. "
        f"Replace expensive activities (>10% over budget) with budget alternatives. "
        f"Current itinerary: {json.dumps(draft)}\n"
        f"Return ONLY the revised JSON itinerary with the same structure but lower costs."
    )

    cached = get_cached_llm(prompt)
    if cached:
        state["draft_itinerary"] = cached
        return state

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.5,
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        revised = json.loads(text)
        set_cached_llm(prompt, revised)
        state["draft_itinerary"] = revised
    except Exception:
        pass

    return state
