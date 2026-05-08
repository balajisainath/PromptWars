import httpx
from agents.state import TravelPlannerState
from app.core.config import get_settings


def validation_node(state: TravelPlannerState) -> TravelPlannerState:
    draft = state.get("draft_itinerary")
    if not draft:
        state["validation_result"] = {"valid": False, "issues": ["No itinerary generated"], "suggestions": []}
        return state

    settings = get_settings()
    issues = []

    days = draft.get("days", [])
    if not days:
        issues.append("No days in itinerary")

    for day in days:
        activities = day.get("activities", [])
        if not activities:
            issues.append(f"Day {day.get('day_number')} has no activities")
            continue

        times = [
            (a.get("start_time"), a.get("end_time"), a.get("name"))
            for a in activities
            if a.get("start_time") and a.get("end_time")
        ]
        for i in range(len(times) - 1):
            if times[i][1] > times[i + 1][0]:
                issues.append(
                    f"Day {day.get('day_number')}: Time overlap between "
                    f"'{times[i][2]}' and '{times[i+1][2]}'"
                )

    try:
        first_day = days[0] if days else None
        if first_day:
            acts_with_coords = [
                {
                    "name": a.get("name"),
                    "lat": a.get("lat"),
                    "lng": a.get("lng"),
                    "start_time": a.get("start_time"),
                    "end_time": a.get("end_time"),
                }
                for a in first_day.get("activities", [])
                if a.get("lat") and a.get("lng")
            ]
            if len(acts_with_coords) >= 2:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.post(
                        f"{settings.GEO_SERVICE_URL}/geo/route-feasibility",
                        json={"activities": acts_with_coords},
                    )
                    if resp.status_code == 200:
                        geo_result = resp.json()
                        if not geo_result.get("feasible", True):
                            issues.extend(geo_result.get("issues", []))
    except Exception:
        pass

    state["validation_result"] = {
        "valid": len(issues) == 0,
        "issues": issues,
        "suggestions": [],
    }
    return state
