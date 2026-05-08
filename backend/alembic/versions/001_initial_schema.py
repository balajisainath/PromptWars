"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-08

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("firebase_uid", sa.String(128), nullable=False),
        sa.Column("email", sa.String(500), nullable=False),
        sa.Column("display_name", sa.String(500), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "destinations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("place_id", sa.String(500), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("place_types", postgresql.JSONB(), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("photo_reference", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_destinations_place_id", "destinations", ["place_id"], unique=True)

    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("destination", sa.String(500), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("group_size", sa.Integer(), nullable=False),
        sa.Column("travel_style", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trips_user_id", "trips", ["user_id"])
    op.create_index("ix_trips_status", "trips", ["status"])

    op.create_table(
        "itineraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("validation_status", sa.String(50), nullable=True),
        sa.Column("raw_llm_output", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_itineraries_trip_id", "itineraries", ["trip_id"])

    op.create_table(
        "itinerary_days",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("itinerary_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("day_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_itinerary_days_itinerary_id", "itinerary_days", ["itinerary_id"])

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("activity_type", sa.String(100), nullable=True),
        sa.Column("booking_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["day_id"], ["itinerary_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_day_id", "activities", ["day_id"])


def downgrade() -> None:
    op.drop_table("activities")
    op.drop_table("itinerary_days")
    op.drop_table("itineraries")
    op.drop_table("trips")
    op.drop_table("destinations")
    op.drop_table("users")
