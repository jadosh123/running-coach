import os
from getpass import getpass
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

# First run: logs in and saves tokens to ~/.garminconnect
# Subsequent runs: loads saved tokens and auto-refreshes
client = Garmin(
    os.getenv("GARMIN_EMAIL"),
    getpass("Garmin password: "),
    prompt_mfa=lambda: input("MFA code: "),
)
client.login("~/.garminconnect")

# Get today's stats
today = date.today().isoformat()
stats = client.get_stats(today)

# Get heart rate data
hr_data = client.get_heart_rates(today)
print(f"Resting HR: {hr_data.get('restingHeartRate', 'n/a')}")