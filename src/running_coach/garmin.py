import os
import time
from getpass import getpass
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectTooManyRequestsError
import json
from running_coach.utils import get_project_root
from pathlib import Path

REQUEST_DELAY_SECONDS = 1
RATE_LIMIT_BACKOFF_SECONDS = 60

load_dotenv()

# First run: logs in and saves tokens to ~/.garminconnect
# Subsequent runs: loads saved tokens and auto-refreshes
def login() -> Garmin:
    client = Garmin(
        os.getenv("GARMIN_EMAIL"),
        getpass("Garmin password: "),
        prompt_mfa=lambda: input("MFA code: "),
    )
    client.login("~/.garminconnect")
    return client


def fetch_splits(client: Garmin, activity_id: int) -> dict:
    try:
        return client.get_activity_splits(activity_id)
    except GarminConnectTooManyRequestsError:
        time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
        return client.get_activity_splits(activity_id)


def main():
    client = login()
    activities = client.get_activities_by_date(startdate="2026-08-01", enddate="2026-09-15", activitytype="running")
    data_path = get_project_root() / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    with open(data_path / "dump.json", "w") as f:
        json.dump(activities, f, indent=2)

    splits = {}
    for activity in activities:
        splits[activity["activityId"]] = fetch_splits(client, activity["activityId"])
        time.sleep(REQUEST_DELAY_SECONDS)
    with open(data_path / "splits.json", "w") as f:
        json.dump(splits, f, indent=2)


if __name__ == "__main__":
    main()