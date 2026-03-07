---
phase: 1
plan: 2
wave: 1
---

# Plan 1.2: Firestore Log Writer Integration

## Objective

Implement the core logic to write validated logs to Firestore and wire up the POST endpoints.

## Context

- .gsd/SPEC.md
- .gsd/DECISIONS.md (ADR-002, ADR-003)
- logging_service/main.py
- logging_service/models/log_entry.py

## Important Note — Firestore SDK is Synchronous

The `firebase-admin` Python SDK's Firestore client is **synchronous only**. There is no async Firestore client. To avoid blocking FastAPI's event loop, wrap synchronous Firestore writes with `asyncio.get_event_loop().run_in_executor(None, sync_write_fn)`. The async fire-and-forget pattern (ADR-003) happens at the HTTP layer (Vue.js doesn't await the response), not at the Python write level.

## Tasks

<task type="auto">
  <name>Implement Firestore Log Writer</name>
  <files>
    - logging_service/db/__init__.py
    - logging_service/db/firestore_client.py
    - logging_service/services/log_writer.py
    - logging_service/main.py
  </files>
  <action>
    - Create `db/firestore_client.py` to initialize and export the Firestore client singleton.
    - Create `services/log_writer.py` with:
      - `write(entry: LogEntry) -> str` — writes a single log to `unified_logs` collection, returns `log_id`.
      - Uses `run_in_executor` to wrap synchronous `db.collection(...).document(...).set(...)` call.
    - Update `POST /log` endpoint in `main.py` to accept `LogEntry`, call `writer.write(entry)`, return `LogCreatedResponse`.
    - Handle Firestore exceptions and return appropriate HTTP 500 errors with structured error response.
  </action>
  <verify>
    curl -s -X POST http://localhost:8000/log \
      -H "Content-Type: application/json" \
      -d '{"study_id": "test-001", "layer": "technical", "event_type": "STUDY_CREATED", "actor_id": "system", "actor_role": "system"}' \
      | python -m json.tool
  </verify>
  <done>
    - [ ] Valid POST request results in a new document in `unified_logs` Firestore collection.
    - [ ] Response contains `log_id` (UUID string).
    - [ ] Invalid payload returns 422 with validation error details.
  </done>
</task>

<task type="auto">
  <name>Implement Batch Log Endpoint</name>
  <files>
    - logging_service/services/log_writer.py
    - logging_service/main.py
  </files>
  <action>
    - Add `write_batch(entries: list[LogEntry]) -> list[str]` to `services/log_writer.py`.
    - Uses Firestore **batched writes** (`db.batch()`) — NOT transactions. Batched writes are atomic and don't have read-then-write overhead.
    - Implement `POST /log/batch` in `main.py` to accept `list[LogEntry]`, call `writer.write_batch(entries)`, return `BatchLogResponse`.
    - Limit batch size to 500 (Firestore batch limit).
  </action>
  <verify>
    curl -s -X POST http://localhost:8000/log/batch \
      -H "Content-Type: application/json" \
      -d '[
        {"study_id": "test-001", "layer": "technical", "event_type": "STUDY_CREATED", "actor_id": "system", "actor_role": "system"},
        {"study_id": "test-001", "layer": "technical", "event_type": "STUDY_UPDATED", "actor_id": "system", "actor_role": "system"}
      ]' \
      | python -m json.tool
  </verify>
  <done>
    - [ ] Batch endpoint writes multiple logs in one atomic batch write.
    - [ ] Response contains list of `log_id` strings.
    - [ ] Batch size > 500 returns 400 with descriptive error.
  </done>
</task>

## Success Criteria

- [ ] `POST /log` writes a single validated log to Firestore and returns `log_id`.
- [ ] `POST /log/batch` writes multiple logs atomically and returns list of `log_id`s.
- [ ] Firestore writes are non-blocking (wrapped in `run_in_executor`).
