-- AI Travel Planning Platform - PostgreSQL Initial Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users ─────────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid    VARCHAR(128) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    display_name    VARCHAR(255),
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_firebase_uid ON users (firebase_uid);
CREATE INDEX idx_users_email ON users (email);

-- ── Trips ─────────────────────────────────────────────────────────
CREATE TABLE trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    destination     VARCHAR(500),
    start_date      DATE,
    end_date        DATE,
    budget          DECIMAL(12,2),
    currency        CHAR(3) NOT NULL DEFAULT 'USD',
    group_size      INT NOT NULL DEFAULT 1,
    travel_style    VARCHAR(50),
    status          VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT trips_group_size_positive CHECK (group_size > 0),
    CONSTRAINT trips_budget_positive CHECK (budget IS NULL OR budget >= 0),
    CONSTRAINT trips_dates_valid CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_trips_user_id ON trips (user_id);
CREATE INDEX idx_trips_status ON trips (status);
CREATE INDEX idx_trips_user_status ON trips (user_id, status);

-- ── Itineraries ───────────────────────────────────────────────────
CREATE TABLE itineraries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id             UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version             INT NOT NULL DEFAULT 1,
    total_cost          DECIMAL(12,2),
    currency            CHAR(3) NOT NULL DEFAULT 'USD',
    validation_status   VARCHAR(50),
    raw_llm_output      JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_itineraries_trip_id ON itineraries (trip_id);

-- ── Itinerary Days ────────────────────────────────────────────────
CREATE TABLE itinerary_days (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    itinerary_id    UUID NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
    day_number      INT NOT NULL,
    date            DATE,
    day_summary     TEXT,
    CONSTRAINT unique_day_per_itinerary UNIQUE (itinerary_id, day_number)
);

CREATE INDEX idx_itinerary_days_itinerary_id ON itinerary_days (itinerary_id);

-- ── Activities ────────────────────────────────────────────────────
CREATE TABLE activities (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    day_id              UUID NOT NULL REFERENCES itinerary_days(id) ON DELETE CASCADE,
    sequence_order      INT NOT NULL DEFAULT 0,
    name                VARCHAR(500) NOT NULL,
    description         TEXT,
    location            VARCHAR(500),
    lat                 DECIMAL(10,7),
    lng                 DECIMAL(10,7),
    start_time          TIME,
    end_time            TIME,
    duration_minutes    INT,
    estimated_cost      DECIMAL(10,2),
    activity_type       VARCHAR(100),
    booking_url         TEXT,
    CONSTRAINT activities_duration_positive CHECK (duration_minutes IS NULL OR duration_minutes > 0),
    CONSTRAINT activities_cost_non_negative CHECK (estimated_cost IS NULL OR estimated_cost >= 0)
);

CREATE INDEX idx_activities_day_id ON activities (day_id);
CREATE INDEX idx_activities_sequence ON activities (day_id, sequence_order);

-- ── Destinations Cache ────────────────────────────────────────────
CREATE TABLE destinations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_place_id VARCHAR(255) UNIQUE,
    name            VARCHAR(500) NOT NULL,
    formatted_address TEXT,
    lat             DECIMAL(10,7),
    lng             DECIMAL(10,7),
    types           JSONB,
    rating          DECIMAL(3,2),
    price_level     INT,
    metadata        JSONB,
    cached_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_destinations_place_id ON destinations (google_place_id);
CREATE INDEX idx_destinations_name ON destinations USING gin (to_tsvector('english', name));

-- ── Auto-update updated_at trigger ────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trips_updated_at
    BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
