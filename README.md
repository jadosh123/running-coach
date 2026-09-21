# running-coach

An MCP server that gives Claude (or any MCP client) access to your Garmin running data.

## Status

The data layer is complete: Garmin login, sync, and local storage all work. The MCP server currently exposes only demo tools; the real tools are in progress.

## What it does

Syncs your Garmin running activities into a local SQLite database, including per-activity summaries and per-lap splits (1 km by default, depending on your watch's auto-lap setting). It also has a notes table for free-text observations, such as pains or how a run felt. The MCP server will expose tools so an LLM can look up runs, read and write notes, analyze trends over time and eventually plan and upload workouts to your Garmin account.

Everything runs locally. Your data stays on your machine, and your Garmin password is never stored.

## Architecture

```
Garmin Connect
      |
      v
sync (garminconnect)  ->  local SQLite DB  <-  MCP server  <-  Claude
      ^
      |
garmin-auth (one-time login, caches tokens)
```

- `garmin.py`: interactive login (`garmin-auth`) and `get_client()`, which loads the cached tokens without prompting.
- `sync.py`: fetches new activities and splits since the last stored run and writes them to the DB.
- `db.py`: SQLite access. Schema versioning uses `PRAGMA user_version`, and migrations run automatically on connect.
- `paths.py`: where the data lives.
- `server.py`: the MCP server.

## Tools

| Tool | Status | Description |
| --- | --- | --- |
| `sync_activities` | Planned | Fetch new runs from Garmin into the local DB |
| `get_recent_activities` | Planned | List the most recent runs |
| `get_activity_splits` | Planned | Per-lap splits for one run |
| `get_activity_notes` / `get_recent_notes` | Planned | Read notes for a run, or the newest notes overall |
| `add_note` / `update_note` | Planned | Write and edit notes |
| Trend analysis | Planned | Compare pace, heart rate, and cadence over time |

The database functions behind these (`get_activities`, `get_activity_splits`, `get_activity_notes`, `get_recent_notes`, `store_note`, `update_note`, `delete_notes`) are implemented in `db.py`. What remains is exposing them as MCP tools.

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync

# 1. Log in once (prompts for email, password, and MFA code if enabled).
#    Tokens are cached in ~/.garminconnect; the password is not stored.
uv run garmin-auth

# 2. Pull your runs into the local database.
uv run python -m running_coach.sync
```

After the first login, syncing needs no credentials. You only need to log in again if the cached tokens expire.

The database lives in your OS's per-user app-data folder (for example `~/.local/share/running-coach/` on Linux). Set `RUNNING_COACH_DATA_DIR` to use a different folder.


## Roadmap

- Implement the MCP tools listed above and test them from Claude
- Package as an `.mcpb` bundle for one-click install in Claude Desktop
- Write-back: create a structured workout and upload it to Garmin
- Consolidate old notes into summaries for long-term context
- Fallback ingestion from Garmin's manual data export (`.FIT` files)
