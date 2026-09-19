# Running Coach: Roadmap

Goal: a local, shareable MCP server (SQLite + Garmin) that Claude or any MCP client uses as the frontend. Not a commercial product.

## Done

- [x] SQLite schema: `activities`, `activity_splits`, `notes` (`database/init.sql`)
- [x] `db.py`: `get_connection`, `get_activities`, `get_activity_split`, `get_activity_notes`, `get_latest_activity_date`
- [x] `db.py`: upserts `store_activity`, `store_splits`, plus `store_note`
- [x] `garmin.py`: incremental fetch (starts from the latest stored run date), rate-limit backoff
- [x] MCP server scaffold registered in Claude Code (demo tools only)

## 1. Finish the DB layer

- [x] `get_recent_notes(conn, limit)`: newest notes regardless of activity
- [x] `update_note(conn, note_id, content)`
- [x] `delete_notes(conn, note_ids)` (for consolidation)
- [x] Rename `get_activity_split` to `get_activity_splits` (consistency)

## 2. Shared data location (do before packaging)

- [x] One module defining the data dir: `platformdirs.user_data_dir("running-coach")`, with `RUNNING_COACH_DATA_DIR` env override
- [x] `DB_PATH` uses it instead of `get_project_root()`
- [ ] Ship `init.sql` as package data (or embed it), otherwise `SCHEMA_PATH.read_text()` fails in an installed copy

## 3. Garmin auth and sync

- [ ] Split `login()` (interactive, setup only) from `get_client()` (cached tokens only, never prompts)
- [ ] Verify `Garmin` can load tokens without email/password
- [ ] Setup CLI entry point (e.g. `running-coach-login`) in `[project.scripts]`
- [ ] Extract the `main()` loop into `sync_activities(client, conn)`; `main()` and the tool both call it
- [ ] Clear error when tokens are missing or expired ("re-run login command"), not a traceback
- [ ] MFA: one-time terminal login seeds the token cache. Never accept a password as a tool argument
- [ ] Bundle `user_config` (sensitive email/password to env vars): check the MCPB spec for exact fields

## 4. MCP tools (`server.py`)

Thin `@mcp.tool()` wrappers that open and close the connection per call; the model never sees `conn` or paths.

- [ ] `get_recent_activities(limit)`
- [ ] `get_activity_splits(activity_id)`
- [ ] `get_activity_notes(activity_id | None)`
- [ ] `add_note(content, activity_id | None)`: docstring must say "look up activity_id via get_recent_activities first"
- [ ] `update_note`, `get_recent_notes`
- [ ] `sync_activities()`: incremental only, cap activities per call (long calls can time out)
- [ ] Remove the demo `add` / `greeting`
- [ ] Return short, model-friendly error messages (12-Factor #9)

## 5. Later: write-back

- [ ] `create_workout` / `upload_to_garmin` as separate narrow tools
- [ ] Confirmation step before uploading (12-Factor #7)
- [ ] Separate "compose workout" from "deliver to Garmin" so a `.FIT` workout file + manual import is a fallback if `garminconnect` breaks

## 6. Later: notes consolidation and memory

- [ ] Consolidation flow: fetch old notes, summarize with the LLM, `delete_notes(old_ids)`, `store_note(summary)`
- [ ] Decide: delete originals, or keep them with a `consolidated_into_id` marker (auditability)
- [ ] Semantic recall: `sqlite-vec` or in-Python cosine similarity; needs an embedding model (and its own API key)

## 7. Manual data fallback

- [ ] Garmin account data export requested (email link can take 24h to 30 days). When it arrives, inspect the structure (`DI-Connect-Fitness` FIT files + JSON)
- [ ] Ingest from `.FIT` via `fitparse` into the same tables
- [ ] `compute_splits_from_samples(records, split_distance_m=1000)` for sources with no laps (GPX, or other devices)

## 8. Packaging and distribution

- [ ] Test in Claude Desktop (Windows) using the `wsl.exe` wrapper config
- [ ] `manifest.json` + `mcpb pack` for one-click install
- [ ] README: setup command, MFA note, what tools exist, client support (Claude and Gemini CLI run local stdio servers; ChatGPT needs a remote HTTPS server)

## Notes to remember

- Garmin API values are always metric (meters, m/s), regardless of display units
- `store_note` is additive; `store_activity` / `store_splits` are upserts
- Split sizes vary by device auto-lap setting; compare using `distance_meters`, not `lap_index`
- Tests: `python -m running_coach.db` writes a test note each run. Delete `content = 'test note from db.py main block'` rows
- Strava now has an official read-only MCP connector; this project's edge is Garmin, persistent notes, and write-back
