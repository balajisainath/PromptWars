from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import uuid


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_place_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    formatted_address: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    types: Mapped[list | None] = mapped_column(JSONB)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    price_level: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict | None] = mapped_column(JSONB, name="metadata")
    cached_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
