from typing import TypedDict, Optional, List


class TravelPlannerState(TypedDict):
    user_id: str
    trip_id: str
    trip_params: dict
    user_context: Optional[str]
    similar_itineraries: Optional[List[dict]]
    ranked_destinations: Optional[List[dict]]
    draft_itinerary: Optional[dict]
    validation_result: Optional[dict]
    final_itinerary: Optional[dict]
    error: Optional[str]
    iteration_count: int
