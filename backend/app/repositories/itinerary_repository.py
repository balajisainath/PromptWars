from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.itinerary import Itinerary, ItineraryDay, Activity


class ItineraryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, itinerary_id: UUID) -> Optional[Itinerary]:
        result = await self.db.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
        return result.scalar_one_or_none()

    async def list_for_trip(self, trip_id: UUID) -> List[Itinerary]:
        result = await self.db.execute(
            select(Itinerary).where(Itinerary.trip_id == trip_id).order_by(Itinerary.version.desc())
        )
        return list(result.scalars().all())

    async def create_full(self, trip_id: UUID, data: dict) -> Itinerary:
        itinerary = Itinerary(
            trip_id=trip_id,
            total_cost=data.get("total_cost"),
            currency=data.get("currency", "USD"),
            validation_status=data.get("validation_status", "valid"),
            raw_llm_output=data,
        )
        self.db.add(itinerary)
        await self.db.flush()

        for day_data in data.get("days", []):
            day = ItineraryDay(
                itinerary_id=itinerary.id,
                day_number=day_data["day_number"],
                date=day_data.get("date"),
                day_summary=day_data.get("summary"),
            )
            self.db.add(day)
            await self.db.flush()

            for i, act in enumerate(day_data.get("activities", [])):
                self.db.add(Activity(
                    day_id=day.id,
                    sequence_order=i,
                    name=act.get("name", ""),
                    description=act.get("description"),
                    location=act.get("location"),
                    lat=act.get("lat"),
                    lng=act.get("lng"),
                    start_time=act.get("start_time"),
                    end_time=act.get("end_time"),
                    duration_minutes=act.get("duration_minutes"),
                    estimated_cost=act.get("estimated_cost"),
                    activity_type=act.get("activity_type"),
                    booking_url=act.get("booking_url"),
                ))

        await self.db.commit()
        await self.db.refresh(itinerary)
        return itinerary
