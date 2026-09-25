from running_coach import db
import pytest
import sqlite3


def test_get_activity_missing_returns_none(conn):
    assert db.get_activity(conn, 999) is None


def test_latest_activity_date_empty_db(conn):
    assert db.get_latest_activity_date(conn) is None


def test_latest_activity_date_returns_date_of_newest(conn, make_activity):
    db.store_activity(conn, make_activity(1, start="2026-09-18 15:36:37"))
    db.store_activity(conn, make_activity(2, start="2026-09-24 17:14:18"))

    assert db.get_latest_activity_date(conn) == "2026-09-24"


def test_store_activity_upserts(conn, make_activity):
    db.store_activity(conn, make_activity(1, distance=5000.0))
    db.store_activity(conn, make_activity(1, distance=6000.0))

    rows = db.get_recent_activities(conn)
    assert len(rows) == 1
    assert rows[0]["distance_meters"] == 6000.0


def test_store_splits_upserts(conn, make_activity, make_splits):
    db.store_activity(conn, make_activity(1))
    db.store_splits(conn, 1, make_splits(3, distance=1000.0))
    db.store_splits(conn, 1, make_splits(3, distance=1005.0))

    splits = db.get_activity_splits(conn, 1)
    assert [s["lap_index"] for s in splits] == [1, 2, 3]
    assert all(s["distance_meters"] == 1005.0 for s in splits)


def test_general_notes_exclude_activity_notes(conn, make_activity):
    db.store_activity(conn, make_activity(1))
    db.store_note(conn, "general")
    db.store_note(conn, "run note", activity_id=1)

    assert [n["content"] for n in db.get_activity_notes(conn, None)] == ["general"]


def test_add_activity_note_and_delete(conn, make_activity):
    db.store_activity(conn, make_activity(1))
    note_id = db.store_note(conn, "Test note", activity_id=1)
    keep_id = db.store_note(conn, "Keep me", activity_id=1)
    assert [n["content"] for n in db.get_activity_notes(conn, 1)] == ["Test note", "Keep me"]

    assert db.delete_notes(conn, [note_id]) == 1
    assert [n["id"] for n in db.get_activity_notes(conn, 1)] == [keep_id]


def test_get_recent_notes_negative_limit_returns_all(conn):
    for i in range(7):
        db.store_note(conn, f"note {i}")
    assert len(db.get_recent_notes(conn, limit=-1)) == 7


def test_store_note_on_missing_activity(conn):
    with pytest.raises(sqlite3.IntegrityError):
        db.store_note(conn, "orphan", activity_id=999)

    assert db.get_recent_notes(conn) == []


def test_deleting_activity_cascades_splits_and_keeps_notes(conn, make_activity, make_splits):
    db.store_activity(conn, make_activity(1))
    db.store_splits(conn, 1, make_splits(3))
    note_id = db.store_note(conn, "knee felt tight", activity_id=1)

    conn.execute("DELETE FROM activities WHERE activity_id = ?", (1,))

    assert db.get_activity_splits(conn, 1) == []
    general = db.get_activity_notes(conn, None)
    assert [(n["id"], n["content"]) for n in general] == [(note_id, "knee felt tight")]


def test_foreign_keys_enforced_on_existing_db():
    with db.connection():
        pass                      # first connection: creates + migrates the DB

    with db.connection() as conn: # second connection: no migration runs
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
            db.store_note(conn, "orphan", activity_id=999)
