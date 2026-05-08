from langgraph.graph import StateGraph, END
from agents.state import TravelPlannerState
from agents.nodes.intent_extraction import intent_extraction_node
from agents.nodes.graphiti_context import graphiti_context_node
from agents.nodes.qdrant_search import qdrant_search_node
from agents.nodes.planner import planner_node
from agents.nodes.budget_agent import budget_agent_node
from agents.nodes.validation import validation_node


def _should_retry(state: TravelPlannerState) -> str:
    if state.get("error"):
        return "end"
    validation = state.get("validation_result", {})
    if validation.get("valid", True):
        return "end"
    if state.get("iteration_count", 0) >= 3:
        return "end"
    return "retry"


def _increment_iteration(state: TravelPlannerState) -> TravelPlannerState:
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    return state


def _finalize(state: TravelPlannerState) -> TravelPlannerState:
    if not state.get("error"):
        state["final_itinerary"] = state.get("draft_itinerary")
    return state


def build_graph():
    graph = StateGraph(TravelPlannerState)

    graph.add_node("intent_extraction", intent_extraction_node)
    graph.add_node("graphiti_context", graphiti_context_node)
    graph.add_node("qdrant_search", qdrant_search_node)
    graph.add_node("planner", planner_node)
    graph.add_node("budget_agent", budget_agent_node)
    graph.add_node("validation", validation_node)
    graph.add_node("increment_iteration", _increment_iteration)
    graph.add_node("finalize", _finalize)

    graph.set_entry_point("intent_extraction")
    graph.add_edge("intent_extraction", "graphiti_context")
    graph.add_edge("graphiti_context", "qdrant_search")
    graph.add_edge("qdrant_search", "planner")
    graph.add_edge("planner", "budget_agent")
    graph.add_edge("budget_agent", "validation")
    graph.add_conditional_edges(
        "validation",
        _should_retry,
        {"retry": "increment_iteration", "end": "finalize"},
    )
    graph.add_edge("increment_iteration", "planner")
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = None


def run_travel_planner(user_id: str, trip_id: str, trip_params: dict) -> dict:
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()

    initial_state: TravelPlannerState = {
        "user_id": user_id,
        "trip_id": trip_id,
        "trip_params": trip_params,
        "user_context": None,
        "similar_itineraries": None,
        "ranked_destinations": None,
        "draft_itinerary": None,
        "validation_result": None,
        "final_itinerary": None,
        "error": None,
        "iteration_count": 0,
    }

    return _compiled_graph.invoke(initial_state)
