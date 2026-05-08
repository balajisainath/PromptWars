from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, Time, Numeric, Integer, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import uuid


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    validation_status: Mapped[str | None] = mapped_column(String(50))
    raw_llm_output: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped["Trip"] = relationship("Trip", back_populates="itineraries")
    days: Mapped[list] = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date | None] = mapped_column(Date)
    day_summary: Mapped[str | None] = mapped_column(Text)

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="days")
    activities: Mapped[list] = relationship("Activity", back_populates="day", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(500))
    lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    activity_type: Mapped[str | None] = mapped_column(String(100))
    booking_url: Mapped[str | None] = mapped_column(Text)

    day: Mapped["ItineraryDay"] = relationship("ItineraryDay", back_populates="activities")
