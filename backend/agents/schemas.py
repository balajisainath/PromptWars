from typing import Optional, List
from pydantic import BaseModel


class Activity(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    estimated_cost: Optional[float] = None
    activity_type: Optional[str] = None
    booking_url: Optional[str] = None


class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = None
    summary: str
    activities: List[Activity]


class ItinerarySchema(BaseModel):
    destination: str
    total_cost: Optional[float] = None
    currency: str = "USD"
    days: List[DayPlan]


class ValidationResult(BaseModel):
    valid: bool
    issues: List[str] = []
    suggestions: List[str] = []
