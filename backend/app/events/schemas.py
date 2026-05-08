from pydantic import BaseModel
from datetime import datetime


class TripCreatedEvent(BaseModel):
    event_type: str = "trip.created"
    trip_id: str
    user_id: str
    destination: str | None
    created_at: datetime


class ItineraryGeneratedEvent(BaseModel):
    event_type: str = "itinerary.generated"
    itinerary_id: str
    trip_id: str
    user_id: str
    total_cost: float | None
    generated_at: datetime


class ItineraryValidatedEvent(BaseModel):
    event_type: str = "itinerary.validated"
    itinerary_id: str
    trip_id: str
    validation_status: str
    validated_at: datetime
