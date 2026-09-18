-- SQLite enforces FK constraints only when this is set per connection.
PRAGMA foreign_keys = ON;

-- Activity summary, one row per Garmin activity.
CREATE TABLE IF NOT EXISTS activities (
    activity_id INTEGER PRIMARY KEY,
    activity_name TEXT,
    activity_type TEXT NOT NULL,
    start_time_local TEXT NOT NULL,
    start_time_gmt TEXT NOT NULL,
    distance_meters REAL,
    duration_seconds REAL,
    moving_duration_seconds REAL,
    elevation_gain_meters REAL,
    elevation_loss_meters REAL,
    average_speed_mps REAL,
    max_speed_mps REAL,
    calories REAL,
    average_hr REAL,
    max_hr REAL,
    average_cadence REAL,
    max_cadence REAL,
    steps INTEGER
);

-- 1km (or device auto-lap) splits within an activity.
CREATE TABLE IF NOT EXISTS activity_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL REFERENCES activities (activity_id) ON DELETE CASCADE,
    lap_index INTEGER NOT NULL,
    start_time_gmt TEXT NOT NULL,
    distance_meters REAL,
    duration_seconds REAL,
    moving_duration_seconds REAL,
    elevation_gain_meters REAL,
    elevation_loss_meters REAL,
    average_speed_mps REAL,
    max_speed_mps REAL,
    calories REAL,
    average_hr REAL,
    max_hr REAL,
    average_cadence REAL,
    max_cadence REAL,
    stride_length_cm REAL,
    start_latitude REAL,
    start_longitude REAL,
    end_latitude REAL,
    end_longitude REAL,
    UNIQUE (activity_id, lap_index)
);

CREATE INDEX IF NOT EXISTS idx_activity_splits_activity_id ON activity_splits (activity_id);

-- Free-form notes/conversation context for the coaching agent,
-- optionally tied to a specific activity (e.g. "knee felt tight").
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER REFERENCES activities (activity_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
