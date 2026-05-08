from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.trip import Trip
from app.models.user import User

router = APIRouter(prefix="/trips", tags=["trips"])


class TripCreate(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    destination: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    currency: str = Field("USD", max_length=3)
    group_size: int = Field(1, ge=1, le=50)
    travel_style: Optional[str] = Field(None, max_length=50)


class TripUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    destination: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    currency: Optional[str] = Field(None, max_length=3)
    group_size: Optional[int] = Field(None, ge=1, le=50)
    travel_style: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None


class TripResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    destination: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    budget: Optional[Decimal]
    currency: str
    group_size: int
    travel_style: Optional[str]
    status: str

    model_config = {"from_attributes": True}


async def _get_db_user(request: Request, db: AsyncSession) -> User:
    firebase_uid = getattr(request.state, "user_id", None)
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=TripResponse, status_code=201)
async def create_trip(body: TripCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    trip = Trip(user_id=user.id, **body.model_dump())
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return _trip_to_response(trip)


@router.get("", response_model=List[TripResponse])
async def list_trips(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    user = await _get_db_user(request, db)
    result = await db.execute(
        select(Trip)
        .where(and_(Trip.user_id == user.id, Trip.status != "deleted"))
        .offset(skip)
        .limit(limit)
    )
    return [_trip_to_response(t) for t in result.scalars().all()]


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    result = await db.execute(select(Trip).where(and_(Trip.id == trip_id, Trip.user_id == user.id)))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return _trip_to_response(trip)


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: UUID, body: TripUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    result = await db.execute(select(Trip).where(and_(Trip.id == trip_id, Trip.user_id == user.id)))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(trip, field, value)
    await db.commit()
    await db.refresh(trip)
    return _trip_to_response(trip)


@router.delete("/{trip_id}", status_code=204)
async def delete_trip(trip_id: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    user = await _get_db_user(request, db)
    result = await db.execute(select(Trip).where(and_(Trip.id == trip_id, Trip.user_id == user.id)))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip.status = "deleted"
    await db.commit()


def _trip_to_response(trip: Trip) -> TripResponse:
    return TripResponse(
        id=str(trip.id),
        user_id=str(trip.user_id),
        title=trip.title,
        description=trip.description,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        currency=trip.currency,
        group_size=trip.group_size,
        travel_style=trip.travel_style,
        status=trip.status,
    )
