# DECISIONS.md — Architecture Decision Record

## ADR-001: Python Microservice on Cloud Run (vs Firebase Functions)

**Status**: Proposed
**Date**: 2026-03-05

### Decision

Use FastAPI on Cloud Run for the logging microservice.

### Rationale

| Factor           | Firebase Functions (Python)  | FastAPI on Cloud Run            |
| ---------------- | ---------------------------- | ------------------------------- |
| Cold start       | ~3-5s (critical for logging) | <500ms (min instances)          |
| Concurrency      | 1 request/instance           | Configurable (80+)              |
| Python ecosystem | Limited                      | Full (numpy, pandas for export) |
| Cost             | Per-invocation               | Per-container-second            |
| Team skill       | Harshit knows Python well    | Aligns with skill set           |

### Consequences

- Need Docker setup for Cloud Run deployment
- Firestore access via Firebase Admin SDK (same as Functions)
- CORS configuration needed between Vue app and Cloud Run (restricting `allow_origins` via the `ALLOWED_ORIGINS` environment variable in production)
- **Min instances**: Set `min-instances=1` to avoid cold starts (~$5-10/month on Blaze)
- **Frontend config**: Cloud Run URL must be in `.env` as `VUE_APP_LOG_API_URL`
- **Deployment dependency**: Marc must know Cloud Run URL is required before frontend can emit logs

---

## ADR-002: Firestore for Log Storage (vs PostgreSQL)

**Status**: Proposed

### Decision

Use Firestore only (no PostgreSQL).

### Rationale

- Already used for all RUXAILAB data
- Avoids adding another database to the stack
- Composite indexes support the query patterns needed
- TTL via scheduled cleanup function (already exists pattern)
- Firestore security rules can protect logs

### Risks

- Complex queries may hit Firestore limitations → mitigate with denormalization

### Key Detail

- `log_id` uses UUID (random) → ensures writes distribute across Firestore internal shards, avoids hotspots
- RUXAILAB is not at scale where collection-level write limits are a concern

---

## ADR-003: Async Fire-and-Forget Logging

**Status**: Proposed

### Decision

Log writes are async (non-blocking) from the frontend and Cloud Functions.

### Rationale

- <50ms latency requirement from SPEC
- Participant session UX must not be impacted
- Logging must never block or crash participant sessions
- Frontend: `emitLog()` returns immediately, POST happens in background
- Cloud Functions: `logger.info()` call doesn't await response from microservice

### Failure Strategy: Local Buffer Fallback

When `emitLog()` POST fails (Cloud Run down/slow):

1. Push failed `LogEntry` to `sessionStorage` array (`__log_buffer`)
2. On next successful `emitLog()` call, flush buffer first (FIFO)
3. On `beforeunload`, attempt one final flush
4. If buffer exceeds 100 entries, drop oldest (prevents memory leak)

Transforms silent data loss into eventual delivery (~20 lines of JS).

---
