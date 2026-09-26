from running_coach import server, db
from mcp.server.mcpserver.exceptions import ToolError
import pytest


def test_recent_activities_empty_db_points_to_sync():
    with pytest.raises(ToolError, match="Run the sync tool"):
        server.get_recent_activities()


def test_get_activity_missing_points_to_recent_activity():
    with pytest.raises(ToolError, match="Use get_recent_activities"):
        server.get_activity(999)


def test_get_activity_splits_missing_activity_and_splits(conn, make_activity):
    with conn:
        db.store_activity(conn, make_activity(1, distance=5000.0))
    
    with pytest.raises(ToolError, match="get_recent_activities"):
        server.get_activity_splits(999)

    with pytest.raises(ToolError, match="get_activity"):
        server.get_activity_splits(1)


def test_write_note_missing_activity_id_points_to_get_recent_activities():
    with pytest.raises(ToolError, match="get_recent_activities"):
        server.write_note("test", 999)
