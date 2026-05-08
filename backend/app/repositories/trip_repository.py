from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.trip import Trip


class TripRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, data: dict) -> Trip:
        trip = Trip(user_id=user_id, **data)
        self.db.add(trip)
        await self.db.commit()
        await self.db.refresh(trip)
        return trip

    async def get(self, trip_id: UUID) -> Optional[Trip]:
        result = await self.db.execute(select(Trip).where(Trip.id == trip_id))
        return result.scalar_one_or_none()

    async def get_for_user(self, trip_id: UUID, user_id: UUID) -> Optional[Trip]:
        result = await self.db.execute(
            select(Trip).where(and_(Trip.id == trip_id, Trip.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> List[Trip]:
        result = await self.db.execute(
            select(Trip).where(Trip.user_id == user_id).order_by(Trip.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, trip: Trip, data: dict) -> Trip:
        for key, value in data.items():
            setattr(trip, key, value)
        await self.db.commit()
        await self.db.refresh(trip)
        return trip

    async def delete(self, trip: Trip) -> None:
        await self.db.delete(trip)
        await self.db.commit()
