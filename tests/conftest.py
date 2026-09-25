import pytest
from running_coach import db


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("RUNNING_COACH_DATA_DIR", str(tmp_path))
    return tmp_path

@pytest.fixture
def conn():
    with db.connection() as conn:
        yield conn

@pytest.fixture
def make_activity():
    def _make(activity_id=1, start="2026-09-24 17:14:18", **overrides):
        """Minimal Garmin-shaped activity dict for store_activity."""
        return {
            "activityId": activity_id,
            "activityType": {"typeKey": "running"},
            "startTimeLocal": start,
            "startTimeGMT": start,
            "distance": 5000.0,
            "averageRunningCadenceInStepsPerMinute": 145.0,
            **overrides,
        }
    return _make


@pytest.fixture
def make_splits():
    def _make(n=3, **overrides):
        """Garmin-shaped splits payload with n laps for store_splits."""
        return {
            "lapDTOs": [
                {
                    "lapIndex": i,
                    "startTimeGMT": f"2026-09-24T14:{i:02d}:00.0",
                    "distance": 1000.0,
                    **overrides,
                }
                for i in range(1, n + 1)
            ]
        }
    return _make
