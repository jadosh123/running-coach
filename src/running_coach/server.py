from mcp.server import MCPServer
from running_coach import db
from running_coach.models import Activity, ActivitySplit
from running_coach import sync
from typing import Any

mcp = MCPServer("Running Coach")


@mcp.tool()
def get_recent_activities(limit: int = 5) -> list[Activity]:
    """Fetch most recent N activities with the limit argument."""
    conn = db.get_connection()
    try:
        res = [Activity(**row) for row in db.get_recent_activities(conn, limit)]
    finally:
        conn.close()

    if not res:
        raise ValueError("No activities in the database yet. Run the sync tool first to populate it.")
    return res


@mcp.tool()
def sync_activities(start_date: str | None = None) -> int:
    """Sync running activities from Garmin into the local database.
    If start_date (YYYY-MM-DD) is omitted, syncs incrementally from the
    last stored activity, or from a default lookback window on first run.
    Returns the number of activities synced."""
    return sync.sync_activities(start_date)


@mcp.tool()
def get_activity(activity_id: int) -> dict[str, Any]:
    conn = db.get_connection()
    try:
        res = db.get_activity(conn, activity_id)
    finally:
        conn.close()

    if not res:
        raise ValueError(f"No activity found for activity_id={activity_id}.")
    return Activity(**res)


@mcp.tool()
def get_activity_splits(activity_id: int) -> list[ActivitySplit]:
    """Fetch activity splits by activity ID."""
    conn = db.get_connection()
    try:
        res = [ActivitySplit(**row) for row in db.get_activity_splits(conn, activity_id)]
    finally:
        conn.close()

    if not res:
        raise ValueError(f"No splits were found for activity_id={activity_id}. Verify the ID via get_activities, or this activity may not have lap data.")
    return res

# @mcp.resource("greeting://{name}")
# def greeting(name: str) -> str:
#     """Greet someone by name."""
#     return f"Hello, {name}!"