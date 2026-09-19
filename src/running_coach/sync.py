import os
import time
from getpass import getpass
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectTooManyRequestsError
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



def main():
    client = login()
    conn = get_connection()

    start_date = get_latest_activity_date(conn) or DEFAULT_START_DATE
    activities = client.get_activities_by_date(startdate=start_date, enddate=date.today().isoformat(), activitytype="running")

    for activity in activities:
        store_activity(conn, activity)
        splits = fetch_splits(client, activity["activityId"])
        store_splits(conn, activity["activityId"], splits)
        conn.commit()
        time.sleep(REQUEST_DELAY_SECONDS)
    conn.close()


if __name__ == "__main__":
    main()