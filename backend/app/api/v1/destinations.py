from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.maps import places_text_search

router = APIRouter(prefix="/destinations", tags=["destinations"])


class DestinationResult(BaseModel):
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    types: List[str]
    rating: Optional[float]


@router.get("/search", response_model=List[DestinationResult])
async def search_destinations(
    q: str = Query(..., min_length=2, max_length=200),
    lat: Optional[float] = None,
    lng: Optional[float] = None,
):
    results = await places_text_search(q, lat, lng)
    return [
        DestinationResult(
            place_id=r.get("place_id", ""),
            name=r.get("name", ""),
            address=r.get("formatted_address", ""),
            lat=r.get("geometry", {}).get("location", {}).get("lat", 0),
            lng=r.get("geometry", {}).get("location", {}).get("lng", 0),
            types=r.get("types", []),
            rating=r.get("rating"),
        )
        for r in results
    ]
