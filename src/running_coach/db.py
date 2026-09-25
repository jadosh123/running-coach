import sqlite3
from typing import Any
from collections.abc import Generator
from running_coach.paths import get_data_dir
from importlib import resources
from running_coach.models import Activity, ActivitySplit
from contextlib import contextmanager

SCHEMA_PATH = resources.files("running_coach.database") / "init.sql"


MIGRATIONS = [
    lambda conn: conn.executescript(SCHEMA_PATH.read_text()),
]


# Database methods
def migrate(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    for target, step in enumerate(MIGRATIONS[version:], start=version + 1):
        step(conn)
        conn.execute(f"PRAGMA user_version = {target}")
        conn.commit()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_data_dir() / "running_coach.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


@contextmanager
def connection() -> Generator[sqlite3.Connection]:
    conn = get_connection()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


# Activity fetching methods
def get_latest_activity_date(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT MAX(start_time_local) FROM activities").fetchone()
    latest = row[0]
    return latest[:10] if latest else None


def get_recent_activities(conn: sqlite3.Connection, limit: int = 10) -> list[dict[str, Any]]:
    return [
        dict(row) 
        for row in conn.execute(
            "SELECT * FROM activities ORDER BY start_time_local DESC LIMIT ?",
            (limit,)).fetchall()
    ]


def get_activity(conn: sqlite3.Connection, activity_id: int) -> dict[str, Any] | None:
    res = conn.execute(
        "SELECT * FROM activities WHERE activity_id = ?",
        (activity_id,)
    ).fetchone()
    return dict(res) if res else None


def get_activity_splits(conn: sqlite3.Connection, activity_id: int) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM activity_splits WHERE activity_id = ? ORDER BY lap_index",
            (activity_id,),
        ).fetchall()
    ]


# Note methods
def get_activity_notes(conn: sqlite3.Connection, activity_id: int | None) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM notes WHERE activity_id IS ? ORDER BY created_at, id",
            (activity_id,),
        ).fetchall()
    ]


def store_note(conn: sqlite3.Connection, content: str, activity_id: int | None = None) -> int:
    cursor = conn.execute(
        "INSERT INTO notes (activity_id, content) VALUES (?, ?)",
        (activity_id, content),
    )
    return cursor.lastrowid


def delete_notes(conn: sqlite3.Connection, note_ids: list[int]) -> int:
    if not note_ids:
        return 0
    placeholders = ", ".join("?" * len(note_ids))
    cursor = conn.execute(
        f"DELETE FROM notes WHERE id IN ({placeholders})",
        note_ids,
    )
    return cursor.rowcount


def get_recent_notes(conn: sqlite3.Connection, limit: int = 5) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM notes ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    ]


# Data writing
def store_activity(conn: sqlite3.Connection, activity: dict) -> None:
    conn.execute(
        """
        INSERT INTO activities (
            activity_id, activity_name, activity_type,
            start_time_local, start_time_gmt,
            distance_meters, duration_seconds, moving_duration_seconds,
            elevation_gain_meters, elevation_loss_meters,
            average_speed_mps, max_speed_mps,
            calories, average_hr, max_hr,
            average_cadence, max_cadence, steps
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (activity_id) DO UPDATE SET
            activity_name = excluded.activity_name,
            activity_type = excluded.activity_type,
            start_time_local = excluded.start_time_local,
            start_time_gmt = excluded.start_time_gmt,
            distance_meters = excluded.distance_meters,
            duration_seconds = excluded.duration_seconds,
            moving_duration_seconds = excluded.moving_duration_seconds,
            elevation_gain_meters = excluded.elevation_gain_meters,
            elevation_loss_meters = excluded.elevation_loss_meters,
            average_speed_mps = excluded.average_speed_mps,
            max_speed_mps = excluded.max_speed_mps,
            calories = excluded.calories,
            average_hr = excluded.average_hr,
            max_hr = excluded.max_hr,
            average_cadence = excluded.average_cadence,
            max_cadence = excluded.max_cadence,
            steps = excluded.steps
        """,
        (
            activity["activityId"],
            activity.get("activityName"),
            activity["activityType"]["typeKey"],
            activity["startTimeLocal"],
            activity["startTimeGMT"],
            activity.get("distance"),
            activity.get("duration"),
            activity.get("movingDuration"),
            activity.get("elevationGain"),
            activity.get("elevationLoss"),
            activity.get("averageSpeed"),
            activity.get("maxSpeed"),
            activity.get("calories"),
            activity.get("averageHR"),
            activity.get("maxHR"),
            activity.get("averageRunningCadenceInStepsPerMinute"),
            activity.get("maxRunningCadenceInStepsPerMinute"),
            activity.get("steps"),
        ),
    )


def store_splits(conn: sqlite3.Connection, activity_id: int, splits: dict) -> None:
    for lap in splits.get("lapDTOs", []):
        conn.execute(
            """
            INSERT INTO activity_splits (
                activity_id, lap_index, start_time_gmt,
                distance_meters, duration_seconds, moving_duration_seconds,
                elevation_gain_meters, elevation_loss_meters,
                average_speed_mps, max_speed_mps,
                calories, average_hr, max_hr,
                average_cadence, max_cadence, stride_length_cm,
                start_latitude, start_longitude, end_latitude, end_longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (activity_id, lap_index) DO UPDATE SET
                start_time_gmt = excluded.start_time_gmt,
                distance_meters = excluded.distance_meters,
                duration_seconds = excluded.duration_seconds,
                moving_duration_seconds = excluded.moving_duration_seconds,
                elevation_gain_meters = excluded.elevation_gain_meters,
                elevation_loss_meters = excluded.elevation_loss_meters,
                average_speed_mps = excluded.average_speed_mps,
                max_speed_mps = excluded.max_speed_mps,
                calories = excluded.calories,
                average_hr = excluded.average_hr,
                max_hr = excluded.max_hr,
                average_cadence = excluded.average_cadence,
                max_cadence = excluded.max_cadence,
                stride_length_cm = excluded.stride_length_cm,
                start_latitude = excluded.start_latitude,
                start_longitude = excluded.start_longitude,
                end_latitude = excluded.end_latitude,
                end_longitude = excluded.end_longitude
            """,
            (
                activity_id,
                lap["lapIndex"],
                lap["startTimeGMT"],
                lap.get("distance"),
                lap.get("duration"),
                lap.get("movingDuration"),
                lap.get("elevationGain"),
                lap.get("elevationLoss"),
                lap.get("averageSpeed"),
                lap.get("maxSpeed"),
                lap.get("calories"),
                lap.get("averageHR"),
                lap.get("maxHR"),
                lap.get("averageRunCadence"),
                lap.get("maxRunCadence"),
                lap.get("strideLength"),
                lap.get("startLatitude"),
                lap.get("startLongitude"),
                lap.get("endLatitude"),
                lap.get("endLongitude"),
            ),
        )
