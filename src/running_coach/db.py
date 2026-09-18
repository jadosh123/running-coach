import sqlite3
from typing import Any
from running_coach.utils import get_project_root

DB_PATH = get_project_root() / "data" / "running_coach.db"
SCHEMA_PATH = get_project_root() / "database" / "init.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


def get_latest_activity_date(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT MAX(start_time_local) FROM activities").fetchone()
    latest = row[0]
    return latest[:10] if latest else None


def get_activities(conn: sqlite3.Connection, limit: int = 10) -> list[dict[str, Any]]:
    return [
        dict(row) 
        for row in conn.execute(
            "SELECT * FROM activities ORDER BY start_time_local DESC LIMIT ?",
            (limit,)).fetchall()
    ]


def get_activity_split(conn: sqlite3.Connection, activity_id: int) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM activity_splits WHERE activity_id = ? ORDER BY lap_index",
            (activity_id,),
        ).fetchall()
    ]


def get_activity_notes(conn: sqlite3.Connection, activity_id: int | None) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM notes WHERE activity_id IS ? ORDER BY created_at",
            (activity_id,),
        ).fetchall()
    ]


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


def store_note(conn: sqlite3.Connection, content: str, activity_id: int | None = None) -> int:
    cursor = conn.execute(
        "INSERT INTO notes (activity_id, content) VALUES (?, ?)",
        (activity_id, content),
    )
    return cursor.lastrowid


if __name__ == "__main__":
    conn = get_connection()

    activities = get_activities(conn, limit=3)
    print(f"Latest activity date: {get_latest_activity_date(conn)}")
    print(f"Last {len(activities)} activities:")
    for activity in activities:
        print(f"  {activity['activity_id']} - {activity['activity_name']} ({activity['start_time_local']})")

    if activities:
        sample_activity_id = activities[0]["activity_id"]

        splits = get_activity_split(conn, sample_activity_id)
        print(f"\n{len(splits)} splits for activity {sample_activity_id}:")
        for split in splits:
            print(f"  lap {split['lap_index']}: {split['distance_meters']}m in {split['duration_seconds']}s")

        note_id = store_note(conn, "test note from db.py main block", activity_id=sample_activity_id)
        conn.commit()
        print(f"\nInserted note {note_id} for activity {sample_activity_id}")

        notes = get_activity_notes(conn, sample_activity_id)
        print(f"Notes for activity {sample_activity_id}: {notes}")

    general_notes = get_activity_notes(conn, None)
    print(f"\nGeneral notes (no activity_id): {general_notes}")

    conn.close()
