---
phase: 1
plan: 3
wave: 2
---

# Plan 1.3: Tests, Security Rules & Deployment Prep

## Objective

Finalize the foundation with two-tier testing (mocked + emulator), Firestore security rules, Docker configuration, and the GET /logs read endpoint.

> Note: 4 tasks (exceeds GSD 2-3 max, but all are tightly related to deployment readiness and small in scope).

## Context

- .gsd/SPEC.md
- .gsd/DECISIONS.md (ADR-001)
- logging_service/main.py
- logging_service/services/log_writer.py

## Tasks

<task type="auto">
  <name>Implement GET /logs Query Endpoint</name>
  <files>
    - logging_service/main.py
    - logging_service/services/log_reader.py
  </files>
  <action>
    - Create `services/log_reader.py` with `query(study_id: str, layer: str | None, limit: int = 100) -> list[dict]`.
    - Query Firestore `unified_logs` collection with filters on `study_id` (required), `layer` (optional).
    - Add `GET /logs` endpoint to `main.py` with query params: `study_id` (required), `layer` (optional), `limit` (default 100, max 1000).
    - Return 422 if `study_id` is missing.
  </action>
  <verify>
    curl -s "http://localhost:8000/logs?study_id=test-001&layer=technical" | python -m json.tool
  </verify>
  <done>
    - [ ] GET /logs?study_id=test-001 returns list of matching logs.
    - [ ] GET /logs?study_id=test-001&layer=technical filters correctly.
    - [ ] GET /logs with no study_id returns 422.
  </done>
</task>

<task type="auto">
  <name>Create Two-Tier Test Suite</name>
  <files>
    - logging_service/tests/__init__.py
    - logging_service/tests/test_api.py
    - logging_service/tests/test_writer.py
    - logging_service/tests/conftest.py
  </files>
  <action>
    Two test tiers:

    **Tier 1 — `test_api.py`** (mocked Firestore, runs in CI without emulator):
    - Use `httpx.AsyncClient` with `TestClient` for all HTTP endpoint tests.
    - Mock `services/log_writer.py` and `services/log_reader.py` to avoid Firestore calls.
    - Test: health, POST /log valid, POST /log invalid, POST /log/batch, GET /logs, error responses.

    **Tier 2 — `test_writer.py`** (Firestore emulator, runs locally + CI with emulator):
    - Set `FIRESTORE_EMULATOR_HOST=localhost:8081` in conftest.py.
    - Test actual write/read to emulator: single write, batch write, query by study_id, query by layer.
    - Verify documents exist after write.

    Target: 90%+ coverage across both tiers (use `pytest-cov`).

  </action>
  <verify>
    cd logging_service &&
    pytest tests/ -v --cov=. --cov-report=term-missing
  </verify>
  <done>
    - [ ] `pytest tests/test_api.py` passes (mocked, no emulator needed).
    - [ ] `pytest tests/test_writer.py` passes when emulator is running.
    - [ ] Combined coverage >= 90%.
  </done>
</task>

<task type="auto">
  <name>Dockerize for Cloud Run</name>
  <files>
    - logging_service/Dockerfile
    - logging_service/.dockerignore
  </files>
  <action>
    - Create multi-stage Dockerfile optimized for Cloud Run:
      - Base: `python:3.11-slim`
      - Install only production dependencies (not test deps).
      - Expose port 8080 (Cloud Run requirement).
      - CMD: `uvicorn main:app --host 0.0.0.0 --port 8080`

    - Create `.dockerignore` with:
      ```
      __pycache__/
      *.pyc
      .env
      .env.*
      !.env.example
      tests/
      *.md
      .git/
      .pytest_cache/
      ```

  </action>
  <verify>docker build -t logging-service logging_service/</verify>
  <done>
    - [ ] Docker image builds successfully.
    - [ ] Image size < 200MB (python-slim + deps only).
    - [ ] `.dockerignore` excludes tests, .env, __pycache__, .git.
  </done>
</task>

<task type="auto">
  <name>Define Firestore Security Rules</name>
  <files>
    - firestore.rules (update)
  </files>
  <action>
    - Add a `match /unified_logs/{logId}` block to `firestore.rules`.
    - Write access: deny to ALL client users. Only Cloud Run service account writes via Admin SDK, which bypasses security rules entirely.
    - Read access: allow if authenticated AND user has admin/researcher role in Firestore:
      ```javascript
      allow read: if request.auth != null
        && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role
           in ["admin", "researcher"];
      ```
    - Do NOT deploy rules — just define them. Deployment is a separate step after mentor review.
  </action>
  <verify>grep -c "unified_logs" firestore.rules</verify>
  <done>
    - [ ] `firestore.rules` contains a `unified_logs` match block.
    - [ ] Write access is denied to all client users.
    - [ ] Read access requires authentication + admin/researcher role via Firestore lookup.
  </done>
</task>

## Success Criteria

- [ ] GET /logs endpoint is functional with study_id + layer filtering.
- [ ] 90%+ test coverage across mocked + emulator test tiers.
- [ ] Docker image builds and is < 200MB.
- [ ] Security rules protect log data using RUXAILAB's actual role-based access pattern.
