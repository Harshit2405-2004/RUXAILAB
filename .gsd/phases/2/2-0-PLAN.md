---
phase: 2
plan: 0
wave: 1
---

# Plan 2.0: Cloud Run Deployment & Env Setup

## Objective

FastAPI is running locally with full tests, but Phase 2 Cloud Functions and frontend code need a real REST endpoint to POST to. We must deploy the service to Cloud Run, restrict CORS appropriately, and update the environment files across the project before proceeding to event hooks.

## Context

- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/TODO.md

## Tasks

<task type="auto">
  <name>Restrict CORS for Production</name>
  <files>logging_service/main.py, logging_service/.env.example</files>
  <action>
    - Add `ALLOWED_ORIGINS` to the env configuration.
    - Change `allow_origins=["*"]` in `main.py` to securely read from `os.getenv("ALLOWED_ORIGINS", "*").split(",")`.
    - Document this config deeply as a production requirement.
  </action>
  <verify>
```bash
# Start with restricted origins and verify rejection
ALLOWED_ORIGINS="https://example.com" uvicorn main:app --port 8001 &
sleep 2
# This should return 200 (same origin)
curl -s -H "Origin: https://example.com" http://localhost:8001/health
# This should return 400 or missing CORS headers (different origin)
curl -s -v -H "Origin: https://evil.com" http://localhost:8001/health 2>&1 | grep -i "access-control"
kill %1
```
  </verify>
  <done>CORS origins are dynamically set via environment variables</done>
</task>

<task type="checkpoint:human-verify">
  <name>Deploy to Cloud Run</name>
  <files>logging_service/Dockerfile</files>
  <action>
    - This is a human/checkpoint step for the User since actual billing/GCP setup is required which is an external step.
    - Ask the user to run the `gcloud run deploy` command and return the `LOG_SERVICE_URL`.
    - Once the user confirms the URL, we add it to the `.env` variables across the repo.
    - Fallback: If Cloud Run deployment is blocked (billing, GCP access), run logging_service locally via Docker on port 8080 and set VUE_APP_LOG_API_URL=http://localhost:8080 for local development. Phase 2.1 and 2.2 can proceed against local service — deployment can happen in parallel without blocking event hook work.
  </action>
  <verify>A successful HTTP GET against the provisioned URL returning a health check</verify>
  <done>
- [ ] Cloud Run service URL confirmed and live
- [ ] GET /health returns 200 from Cloud Run URL (not localhost)
- [ ] min-instances=1 confirmed in Cloud Run console
- [ ] VUE_APP_LOG_API_URL set in .env.local and .env.production
- [ ] LOG_SERVICE_URL set in functions/.env
- [ ] ADR-001 updated with confirmed Cloud Run URL
- [ ] CORS verified — rejects requests from unknown origins
  </done>
</task>

<task type="auto">
  <name>Set Environment Configuration</name>
  <files>RUXAILAB/.env.local, RUXAILAB/.env.production, functions/.env, .gsd/DECISIONS.md</files>
  <action>
    - Inject the output of the Cloud Run URL as `VUE_APP_LOG_API_URL` into `.env.local` and `.env.production`.
    - Add `LOG_SERVICE_URL` to the Cloud Functions root `functions/.env`.
    - Inject the exact confirmed URL into `.gsd/DECISIONS.md` under ADR-001.
  </action>
  <verify>Check environment configuration references are correctly placed</verify>
  <done>Frontend and Cloud Functions point to the real log service</done>
</task>

## Success Criteria

- [ ] CORS is restricted for production safety.
- [ ] Service deployed and returning 200 OK from `/health`.
- [ ] `.env` configurations are populated with the production POST URL.
