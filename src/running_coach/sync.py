import time
from datetime import date
from garminconnect import Garmin, GarminConnectTooManyRequestsError
from running_coach.garmin import get_client
from running_coach.db import get_connection, get_latest_activity_date, store_activity, store_splits

REQUEST_DELAY_SECONDS = 1
RATE_LIMIT_BACKOFF_SECONDS = 60
DEFAULT_START_DATE = "2026-01-01"


def fetch_splits(client: Garmin, activity_id: int) -> dict:
    try:
        return client.get_activity_splits(activity_id)
    except GarminConnectTooManyRequestsError:
        time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
        return client.get_activity_splits(activity_id)


def sync_activities(start_date: str | None = None) -> int:
    """Sync running activities with local database from garmin."""
    client = get_client()
    conn = get_connection()

    try:
        if not start_date:
            start_date = get_latest_activity_date(conn) or DEFAULT_START_DATE
        activities = client.get_activities_by_date(
            startdate=start_date,
            enddate=date.today().isoformat(),
            activitytype="running"
        )

        for activity in activities:
            splits = fetch_splits(client, activity["activityId"])
            with conn:
                store_activity(conn, activity)
                store_splits(conn, activity["activityId"], splits)
            time.sleep(REQUEST_DELAY_SECONDS)
        return len(activities)
    finally:
        conn.close()


if __name__ == "__main__":
    res = sync_activities()
    print(f"{res} Activities were synced.")