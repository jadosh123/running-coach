import sqlite3
from typing import Any
from running_coach.paths import get_data_dir
from importlib import resources

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


# Activity fetching methods
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


def update_note(conn: sqlite3.Connection, note_id: int, content: str) -> bool:
    cursor = conn.execute(
        "UPDATE notes SET content = ? WHERE id = ?",
        (content, note_id),
    )
    return cursor.rowcount > 0


def delete_notes(conn: sqlite3.Connection, note_ids: list[int]) -> int:
    if not note_ids:
        return 0
    placeholders = ", ".join("?" * len(note_ids))
    cursor = conn.execute(
        f"DELETE FROM notes WHERE id IN ({placeholders})",
        note_ids,
    )
    return cursor.rowcount


def get_recent_notes(conn: sqlite3.Connection, limit: int = 5):
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


if __name__ == "__main__":
    conn = get_connection()

    activities = get_activities(conn, limit=3)
    print(f"Latest activity date: {get_latest_activity_date(conn)}")
    print(f"Last {len(activities)} activities:")
    for activity in activities:
        print(f"  {activity['activity_id']} - {activity['activity_name']} ({activity['start_time_local']})")

    if activities:
        sample_activity_id = activities[0]["activity_id"]

        splits = get_activity_splits(conn, sample_activity_id)
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

    print("\n--- note insert / update / delete ---")
    first_id = store_note(conn, "temp note one")
    second_id = store_note(conn, "temp note two")
    conn.commit()
    print(f"Inserted notes {first_id}, {second_id}")
    print(f"Recent notes (newest first): {[n['content'] for n in get_recent_notes(conn, limit=2)]}")

    print(f"Update existing note: {update_note(conn, first_id, 'temp note one (edited)')}")
    print(f"Update missing note: {update_note(conn, -1, 'nope')}")
    conn.commit()
    print(f"After update: {[n['content'] for n in get_recent_notes(conn, limit=2)]}")

    print(f"Delete both: {delete_notes(conn, [first_id, second_id])} row(s) removed")
    print(f"Delete empty list: {delete_notes(conn, [])}")
    conn.commit()
    remaining = [n["id"] for n in get_recent_notes(conn, limit=50)]
    print(f"Temp notes gone: {first_id not in remaining and second_id not in remaining}")

    conn.close()
