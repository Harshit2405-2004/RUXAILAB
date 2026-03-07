# TODO.md — Pending Items

## Pre-GSoC

- [x] Create POC: minimal FastAPI + POST /log → Firestore write
- [ ] Submit GSoC proposal with architecture diagram
- [ ] Introduce self to Marc on Discord

## Phase 2 Prep (Next Actions)

- [ ] Task 2.0: Deploy logging service to Cloud Run
  - [ ] Build and push Docker image to Google Artifact Registry
  - [ ] Deploy to Cloud Run with min-instances=1
  - [ ] Set `VUE_APP_LOG_API_URL` in RUXAILAB `.env`
  - [ ] Set `LOG_SERVICE_URL` in Cloud Functions environment
  - [ ] Verify `GET /health` returns 200 from Cloud Run URL
  - [ ] Add Cloud Run URL to ADR-001 as a confirmed deployment detail
- [ ] Create POC: `logger.js` in frontend emitting `SESSION_STARTED` (Task 2.2)
- [x] Verify all 10 Phase 2 technical event types are in `VALID_EVENT_TYPES` before writing hooks
- [ ] Restrict CORS `allow_origins=["*"]` in `main.py` for production via env var

## During GSoC

- [ ] Phase 1: Foundation (Weeks 1-2)
- [ ] Phase 2: Technical Layer (Weeks 3-4)
- [ ] Phase 3: Methodological Layer (Weeks 5-6)
- [ ] Phase 4: AI Decision Layer (Weeks 7-8)
- [ ] Phase 5: Traceability + GDPR (Weeks 9-10)
- [ ] Phase 6: Export + Viz + Polish (Weeks 11-13)
