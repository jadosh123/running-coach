from mcp.server import MCPServer
from running_coach import db
from running_coach.models import Activity, ActivitySplit
from running_coach import sync

mcp = MCPServer("Demo")


@mcp.tool()
def get_activities(limit: int) -> list[Activity]:
    """Fetch most recent N activities with the limit argument. Use this to find activity IDs to fetch splits for."""
    conn = db.get_connection()
    try:
        res = [Activity(**row) for row in db.get_activities(conn, limit)]
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


# @mcp.resource("greeting://{name}")
# def greeting(name: str) -> str:
#     """Greet someone by name."""
#     return f"Hello, {name}!"