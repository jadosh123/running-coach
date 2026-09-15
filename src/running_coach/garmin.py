import os
from getpass import getpass
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin
import json
from running_coach.utils import get_project_root
from pathlib import Path

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


def main():
    client = login()
    activities = client.get_activities_by_date("2026-08-01", "2026-09-15")
    data_path = get_project_root() / "data" 
    data_path.mkdir(parents=True, exist_ok=True)
    with open(data_path / "dump.json", "w") as f:
        json.dump(activities, f, indent=2)


if __name__ == "__main__":
    main()