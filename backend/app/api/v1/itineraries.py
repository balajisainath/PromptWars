from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.itinerary import Itinerary, ItineraryDay, Activity
from app.models.trip import Trip
from app.models.user import User

router = APIRouter(tags=["itineraries"])


class GenerateRequest(BaseModel):
    trip_id: str


class ActivityResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    location: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    start_time: Optional[str]
    end_time: Optional[str]
    duration_minutes: Optional[int]
    estimated_cost: Optional[float]
    activity_type: Optional[str]
    booking_url: Optional[str]
    sequence_order: int


class DayResponse(BaseModel):
    id: str
    day_number: int
    date: Optional[str]
    day_summary: Optional[str]
    activities: List[ActivityResponse]


class ItineraryResponse(BaseModel):
    id: str
    trip_id: str
    version: int
    total_cost: Optional[float]
    currency: str
    validation_status: Optional[str]
    days: List[DayResponse]


async def _get_db_user(request: Request, db: AsyncSession) -> User:
    firebase_uid = getattr(request.state, "user_id", None)
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _run_agent_pipeline(trip_id: str, user_id: str):
    """Background task that runs the LangGraph pipeline."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
        from agents.graph import run_travel_planner
        from app.core.database import AsyncSessionLocal
        from app.models.trip import Trip as TripModel

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(TripModel).where(TripModel.id == trip_id))
            trip = result.scalar_one_or_none()
            if not trip:
                return

            trip_params = {
                "destination": trip.destination,
                "start_date": str(trip.start_date) if trip.start_date else None,
                "end_date": str(trip.end_date) if trip.end_date else None,
                "budget": float(trip.budget) if trip.budget else None,
                "currency": trip.currency,
                "group_size": trip.group_size,
                "travel_style": trip.travel_style,
                "description": trip.description or trip.title,
            }

            result_state = run_travel_planner(user_id=user_id, trip_id=trip_id, trip_params=trip_params)
            final_itinerary = result_state.get("final_itinerary")
            if not final_itinerary:
                return

            itinerary = Itinerary(
                trip_id=trip_id,
                total_cost=final_itinerary.get("total_cost"),
                currency=final_itinerary.get("currency", "USD"),
                validation_status="valid",
                raw_llm_output=final_itinerary,
            )
            db.add(itinerary)
            await db.flush()

            for day_data in final_itinerary.get("days", []):
                day = ItineraryDay(
                    itinerary_id=itinerary.id,
                    day_number=day_data["day_number"],
                    date=day_data.get("date"),
                    day_summary=day_data.get("summary"),
                )
                db.add(day)
                await db.flush()

                for i, act_data in enumerate(day_data.get("activities", [])):
                    activity = Activity(
                        day_id=day.id,
                        sequence_order=i,
                        name=act_data.get("name", ""),
                        description=act_data.get("description"),
                        location=act_data.get("location"),
                        lat=act_data.get("lat"),
                        lng=act_data.get("lng"),
                        start_time=act_data.get("start_time"),
                        end_time=act_data.get("end_time"),
                        duration_minutes=act_data.get("duration_minutes"),
                        estimated_cost=act_data.get("estimated_cost"),
                        activity_type=act_data.get("activity_type"),
                        booking_url=act_data.get("booking_url"),
                    )
                    db.add(activity)

            await db.commit()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"Agent pipeline failed: {exc}")


@router.post("/itineraries/generate", status_code=202)
async def generate_itinerary(
    body: GenerateRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await _get_db_user(request, db)
    result = await db.execute(
        select(Trip).where(and_(Trip.id == body.trip_id, Trip.user_id == user.id))
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    background_tasks.add_task(_run_agent_pipeline, str(trip.id), str(user.firebase_uid))
    return {"trip_id": str(trip.id), "status": "processing"}


@router.get("/itineraries/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(itinerary_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    result = await db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    itinerary = result.scalar_one_or_none()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    trip_result = await db.execute(select(Trip).where(and_(Trip.id == itinerary.trip_id, Trip.user_id == user.id)))
    if not trip_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")

    days_result = await db.execute(select(ItineraryDay).where(ItineraryDay.itinerary_id == itinerary_id))
    days = []
    for day in days_result.scalars().all():
        acts_result = await db.execute(
            select(Activity).where(Activity.day_id == day.id).order_by(Activity.sequence_order)
        )
        activities = [
            ActivityResponse(
                id=str(a.id), name=a.name, description=a.description, location=a.location,
                lat=float(a.lat) if a.lat else None, lng=float(a.lng) if a.lng else None,
                start_time=str(a.start_time) if a.start_time else None,
                end_time=str(a.end_time) if a.end_time else None,
                duration_minutes=a.duration_minutes, estimated_cost=float(a.estimated_cost) if a.estimated_cost else None,
                activity_type=a.activity_type, booking_url=a.booking_url, sequence_order=a.sequence_order,
            )
            for a in acts_result.scalars().all()
        ]
        days.append(DayResponse(
            id=str(day.id), day_number=day.day_number,
            date=str(day.date) if day.date else None, day_summary=day.day_summary, activities=activities,
        ))

    return ItineraryResponse(
        id=str(itinerary.id), trip_id=str(itinerary.trip_id), version=itinerary.version,
        total_cost=float(itinerary.total_cost) if itinerary.total_cost else None,
        currency=itinerary.currency, validation_status=itinerary.validation_status, days=days,
    )


@router.get("/trips/{trip_id}/itineraries", response_model=List[ItineraryResponse])
async def list_trip_itineraries(trip_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    trip_result = await db.execute(select(Trip).where(and_(Trip.id == trip_id, Trip.user_id == user.id)))
    if not trip_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Trip not found")

    result = await db.execute(select(Itinerary).where(Itinerary.trip_id == trip_id))
    return [
        ItineraryResponse(
            id=str(it.id), trip_id=str(it.trip_id), version=it.version,
            total_cost=float(it.total_cost) if it.total_cost else None,
            currency=it.currency, validation_status=it.validation_status, days=[],
        )
        for it in result.scalars().all()
    ]
