---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: FastAPI Scaffold & Pydantic Models

## Objective

Establish the core Python microservice structure using FastAPI and define the strict data models for structured logging using Pydantic.

## Context

- .gsd/SPEC.md
- .gsd/DECISIONS.md (ADR-001)

## Tasks

<task type="auto">
  <name>Scaffold FastAPI Project</name>
  <files>
    - logging_service/__init__.py
    - logging_service/main.py
    - logging_service/requirements.txt
    - logging_service/.env.example
  </files>
  <action>
    Initialize a standard FastAPI project structure inside `logging_service/` at repo root.

    Directory structure:
    ```
    logging_service/
    ├── __init__.py           # empty, makes it a package
    ├── main.py               # FastAPI app with GET /health and POST /log stub
    ├── requirements.txt      # all dependencies
    ├── .env.example           # credential template
    ├── models/
    │   ├── __init__.py
    │   ├── log_entry.py      # LogEntry, LogEntryCreate, enums
    │   └── responses.py      # API response schemas
    └── services/
        └── __init__.py
    ```

    - Create `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `pydantic`, `google-cloud-firestore`, `firebase-admin`, `python-dotenv`, `httpx`, `pytest`, `pytest-asyncio`, `pytest-cov`, `google-auth`.
    - Create `main.py` with `GET /health` and `POST /log` stub endpoints.
    - Create `.env.example` with `GOOGLE_APPLICATION_CREDENTIALS=path/to/sa-key.json`.
    - Do NOT initialize Firestore client yet (that's Plan 1.2).

  </action>
  <verify>
    cd logging_service &&
    pip install -r requirements.txt &&
    uvicorn main:app --port 8001 &
    sleep 2 &&
    curl -s http://localhost:8001/health | python -m json.tool &&
    kill %1
  </verify>
  <done>
    - [ ] `GET /health` returns 200 OK with `{"status": "ok"}`.
    - [ ] `requirements.txt` includes all 11 packages.
    - [ ] `logging_service/` has: `main.py`, `__init__.py`, `requirements.txt`, `.env.example`.
    - [ ] `logging_service/models/` exists with `__init__.py`, `log_entry.py`, `responses.py`.
    - [ ] `logging_service/services/` exists with `__init__.py`.
  </done>
</task>

<task type="auto">
  <name>Define LogEntry Pydantic Model</name>
  <files>
    - logging_service/models/log_entry.py
    - logging_service/models/responses.py
    - logging_service/tests/test_models.py
  </files>
  <action>
    Create Pydantic models matching the `unified_logs` schema.

    In `models/log_entry.py`:
    - Define `LogLayer` enum: `technical`, `methodological`, `ai_decision`.
    - Define `ActorRole` enum: `researcher`, `evaluator`, `participant`, `system`.
    - Define `RetentionPolicy` enum: `30d`, `90d`, `1y`, `permanent`.
    - Define `VALID_EVENT_TYPES` set with all events from ROADMAP (STUDY_CREATED, STUDY_UPDATED, etc.).
    - Define `LogEntry` model with all schema fields from implementation plan Section 3.
    - `log_id` auto-generates as UUID v4 when not provided.
    - `trace_id` auto-generates as UUID v4 when not provided.
    - `timestamp` auto-set to `datetime.utcnow()` when not provided.
    - `event_type` validates against `VALID_EVENT_TYPES` — raises ValueError on unknown types.
    - `payload` is `dict[str, Any]` (flexible, PII filtering deferred to middleware in Phase 5).

    In `models/responses.py`:
    - Define `HealthResponse`, `LogCreatedResponse`, `BatchLogResponse`.

    Write 10+ tests in `tests/test_models.py`.

  </action>
  <verify>cd logging_service && pytest tests/test_models.py -v</verify>
  <done>
    - [ ] pytest tests/test_models.py passes with 10+ tests.
    - [ ] Invalid event_type raises ValueError with "Unknown event_type" in message.
    - [ ] Missing required field (study_id, layer) raises ValidationError.
    - [ ] trace_id auto-generates as UUID when not provided.
    - [ ] timestamp defaults to UTC now when not provided.
    - [ ] LogLayer, ActorRole, RetentionPolicy enums enforce valid values.
  </done>
</task>

## Success Criteria

- [ ] FastAPI service runs locally and `/health` returns 200.
- [ ] Pydantic models are defined with strict validation and 10+ passing tests.
- [ ] Project structure supports growth to Phase 4+ without reorganization.
