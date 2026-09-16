-- Activity summary, one row per Garmin activity.
CREATE TABLE activities (
    activity_id BIGINT PRIMARY KEY,
    activity_name TEXT,
    activity_type TEXT NOT NULL,
    start_time_local TIMESTAMP NOT NULL,
    start_time_gmt TIMESTAMP NOT NULL,
    distance_meters DOUBLE PRECISION,
    duration_seconds DOUBLE PRECISION,
    moving_duration_seconds DOUBLE PRECISION,
    elevation_gain_meters DOUBLE PRECISION,
    elevation_loss_meters DOUBLE PRECISION,
    average_speed_mps DOUBLE PRECISION,
    max_speed_mps DOUBLE PRECISION,
    calories DOUBLE PRECISION,
    average_hr DOUBLE PRECISION,
    max_hr DOUBLE PRECISION,
    average_cadence DOUBLE PRECISION,
    max_cadence DOUBLE PRECISION,
    steps INTEGER
);

-- 1km (or device auto-lap) splits within an activity.
CREATE TABLE activity_splits (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities (activity_id) ON DELETE CASCADE,
    lap_index INTEGER NOT NULL,
    start_time_gmt TIMESTAMP NOT NULL,
    distance_meters DOUBLE PRECISION,
    duration_seconds DOUBLE PRECISION,
    moving_duration_seconds DOUBLE PRECISION,
    elevation_gain_meters DOUBLE PRECISION,
    elevation_loss_meters DOUBLE PRECISION,
    average_speed_mps DOUBLE PRECISION,
    max_speed_mps DOUBLE PRECISION,
    calories DOUBLE PRECISION,
    average_hr DOUBLE PRECISION,
    max_hr DOUBLE PRECISION,
    average_cadence DOUBLE PRECISION,
    max_cadence DOUBLE PRECISION,
    stride_length_cm DOUBLE PRECISION,
    start_latitude DOUBLE PRECISION,
    start_longitude DOUBLE PRECISION,
    end_latitude DOUBLE PRECISION,
    end_longitude DOUBLE PRECISION,
    UNIQUE (activity_id, lap_index)
);

CREATE INDEX idx_activity_splits_activity_id ON activity_splits (activity_id);

-- Free-form notes/conversation context for the coaching agent,
-- optionally tied to a specific activity (e.g. "knee felt tight").
CREATE TABLE notes (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT REFERENCES activities (activity_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
