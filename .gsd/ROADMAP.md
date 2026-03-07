# ROADMAP.md

> **Current Phase**: Phase 2 — Technical Log Layer (Weeks 3–4)
> **Last Completed**: Phase 1 — Foundation ✅ (25h)
> **Hours Spent**: ~25h | **Hours Remaining**: ~130h planned + 20h buffer

## Must-Haves (from SPEC)

- [ ] Three-layer log model (technical + methodological + AI decision)
- [ ] Python microservice with POST/GET/export endpoints
- [ ] Vue.js logger utility + Vuex integration
- [ ] Anonymization middleware
- [ ] GDPR export/erasure
- [ ] Study session timeline visualization
- [ ] 90%+ test coverage

## Phases

### Phase 1: Foundation — Schema & Microservice Scaffold

**Status**: ✅ Complete
**Objective**: Design Firestore `unified_logs` schema, scaffold FastAPI microservice, implement health check and base log writer
**Hours**: 25h (Weeks 1–2)
**Requirements**: REQ-01 (schema), REQ-02 (base writer)
**Deliverables**:

- [x] `unified_logs` Firestore collection schema + composite indexes (`firestore.indexes.json` updated)
- [x] FastAPI project scaffold with `POST /log`, `POST /log/batch`, `GET /logs`, `GET /health`
- [x] Pydantic `LogEntry` model with full validation (28 event types registered)
- [x] Firestore security rules for `unified_logs` (role-based)
- [x] 32 Pytest tests for API and log writer (mocked + emulator tiers)
- [x] Production Dockerfile and `.dockerignore` set up

---

### Phase 2: Technical Log Layer

**Status**: 🔄 Ready for Execution
**Objective**: Implement technical event logging for system operations — Cloud Function triggers, HTTPS handlers, Firestore CRUD, auth events
**Hours**: 25h (Weeks 3–4)
**Requirements**: REQ-03 (technical events)
**Deliverables**:

- Event taxonomy: `STUDY_CREATED`, `STUDY_UPDATED`, `STUDY_DELETED`, `USER_SIGNED_IN`, `USER_SIGNED_OUT`, `SESSION_STARTED`, `SESSION_ENDED`, `API_CALLED`, `API_ERROR`, `FUNCTION_TRIGGERED`
- Cloud Functions emit logs via HTTP to microservice
- `GET /logs?layer=technical&study_id=` endpoint
- Tests for each event type

---

### Phase 3: Methodological Log Layer

**Status**: ⬜ Not Started
**Objective**: Log study lifecycle events — task presentation, participant responses, heuristic evaluations, card sorting interactions
**Hours**: 20h (Weeks 5–6) — reduced from 25h, Vuex hooks are repetitive once pattern is established
**Requirements**: REQ-04 (methodological events)
**Deliverables**:

- Event taxonomy: `TASK_PRESENTED`, `TASK_COMPLETED`, `HEURISTIC_SCORED`, `CARD_SORTED`, `CALIBRATION_STARTED`, `CALIBRATION_COMPLETED`, `ANSWER_SUBMITTED`
- Vue.js `emitLog()` utility in `src/utils/logger.js`
- Vuex action hooks for study lifecycle events
- Tests for each event type

---

### Phase 4: AI Decision Log Layer

**Status**: ⬜ Not Started
**Objective**: Log AI computation events — AHP weight calculation, sentiment analysis, eye tracking analysis
**Hours**: 25h (Weeks 7–8) — increased from 20h, AHP logic needs 5-6h for proper understanding
**Requirements**: REQ-05 (AI decision events)
**Deliverables**:

- Event taxonomy: `AI_WEIGHT_COMPUTED`, `AI_CONSISTENCY_CHECK`, `SENTIMENT_ANALYZED`, `EYE_TRACKING_PROCESSED`, `FACIAL_SENTIMENT_ANALYZED`
- `weight_function/main.py` emits decision logs with input parameters, output weights, consistency ratio
- External API calls (sentiment, eye tracking) log request/response metadata
- Tests for each event type

---

### Phase 5: Traceability Engine & GDPR

**Status**: ⬜ Not Started
**Objective**: Implement trace_id propagation, anonymization middleware, consent recording, and GDPR endpoints
**Hours**: 25h (Weeks 9–10)
**Requirements**: REQ-06 (traceability), REQ-07 (GDPR)
**Deliverables**:

- `trace_id` generation and propagation across session events
- Anonymization middleware (SHA-256 hash + salt for participant IDs)
- Consent collection UI component + Firestore `consents` collection
- `POST /gdpr/export`, `DELETE /gdpr/erase` endpoints
- Retention policy enforcement (TTL-based cleanup)
- Tests for anonymizer, consent flow, GDPR endpoints

---

### Phase 6: Export, Visualization & Polish

**Status**: ⬜ Not Started
**Objective**: Build export (CSV/JSON/PDF/JSON-LD), study session timeline visualization, documentation, and final review
**Hours**: 35h (Weeks 11–13) — increased from 30h, D3.js timeline + weasyprint PDF always expands
**Requirements**: REQ-08 (export), REQ-09 (visualization)
**Deliverables**:

- `GET /export/{study_id}?format=csv|json|pdf|jsonld` endpoint
- `GET /audit/{study_id}` — full audit trail report
- `GET /snapshot/{study_id}` — study lifecycle snapshot
- Vue.js timeline component (D3.js or Chart.js)
- Integration with existing report views
- API documentation (FastAPI auto-docs + README)
- Performance optimization and final testing pass

---

## Hour Summary

```
Phase 1:  25h  (Foundation)
Phase 2:  25h  (Technical — flag if API hooks take longer)
Phase 3:  20h  (Methodological — reduced, repetitive pattern)
Phase 4:  25h  (AI Decision — increased, AHP complexity)
Phase 5:  25h  (Traceability + GDPR)
Phase 6:  35h  (Export + Viz + Docs — increased, D3+PDF risk)
──────────────
Planned: 155h
Buffer:   20h  (mentor review, unexpected bugs, weeks 8-10 friction)
Total:   175h
```

## Phase Dependencies

```
Phase 1 (Foundation) → Phase 2 (Technical)
                     → Phase 3 (Methodological)
                     → Phase 4 (AI Decision)
Phase 2 + 3 + 4     → Phase 5 (Traceability + GDPR)
Phase 5              → Phase 6 (Export + Viz + Polish)
```
