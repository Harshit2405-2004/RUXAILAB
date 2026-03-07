# Meeting with Marc — Pitch Document

## Harshit Virmani | RUXAILAB GSoC 2026

## Unified Logging & Traceability System

> **GitHub:** github.com/Harshit2405-2004
> **Meeting Duration:** 30 minutes
> **Status:** Phase 1 Complete — POC Live

---

## Meeting Agenda

| Time          | Block                  | What Happens                                              |
| ------------- | ---------------------- | --------------------------------------------------------- |
| 00:00 – 02:00 | Intro & Vision         | Who I am, one-line pitch, what problem this solves        |
| 02:00 – 08:00 | POC Walkthrough        | Live screenshare — schema, writer, tests, Firestore rules |
| 08:00 – 14:00 | Architecture Decisions | 3 ADRs — why each choice, what each protects against      |
| 14:00 – 20:00 | Roadmap                | 6 phases, 175h, current position, demo-able end goal      |
| 20:00 – 25:00 | The 4 Questions        | Your input needed before Phase 2 execution                |
| 25:00 – 30:00 | Next Steps             | Proposal timeline, review cadence, follow-up              |

---

## Section 1 — Opening Statement

Hi Marc — I'm Harshit Virmani, a student-developer with a background in Python,
TypeScript, backend development, and security. Over the past few weeks I've done
a deep codebase scan of RUXAILAB, documented every finding in a structured GSD
planning system, and built a working Phase 1 POC for the Unified Logging &
Traceability System.

> **One-line pitch:**
> _"RUXAILAB currently has no way to answer: 'What exactly happened during
> participant 3's session, what did the AI compute, and can those results be
> reproduced?' This project answers that question."_

### 5 Goals

1. **Three-Layer Logging** — Technical (system ops), Methodological (study lifecycle), AI Decision (weight computation)
2. **Traceability** — Link every related event via `trace_id` across sessions and AI computations
3. **GDPR Compliance** — Anonymize participant data, record consent, support Right to Access and Right to Erasure
4. **Export & Visualization** — CSV / JSON / PDF / JSON-LD exports + D3.js session timeline
5. **Zero UX Impact** — Async fire-and-forget logging adding <50ms latency to any user action

### 4 Non-Goals — Explicitly Out of Scope

- Real-time log streaming dashboard
- Integration with external APM (Sentry, Datadog)
- Automated alerting on log patterns
- Historical data migration — only new sessions logged going forward

### The Demo-able Success Criterion

> _"A complete study session of 3+ participants generates a queryable audit trail
> retrievable via `GET /audit/{study_id}` within 5 seconds."_

This is what I'm building toward. Everything in the 175h roadmap exists to make
this one thing provably true at the final GSoC evaluation.

**Total Scope:** 175h | 13 Weeks | 20h Buffer reserved

---

## Section 2 — What I Built: POC Stats

Phase 1 of the logging microservice is **complete and verified.**
Every number below is checkable in the repo right now.

### Microservice — `logging_service/`

| Metric                                     | Value                                                                                                |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| **Total Python Files**                     | 15                                                                                                   |
| **Lines of Code** (excl. tests & comments) | 831                                                                                                  |
| **Python Version**                         | 3.11                                                                                                 |
| **Framework**                              | FastAPI                                                                                              |
| **Pydantic Models**                        | 5 — `LogEntry`, `LogEntryCreate`, `HealthResponse`, `LogCreatedResponse`, `BatchLogResponse`         |
| **Lines in `models/log_entry.py`**         | 182                                                                                                  |
| **Enums Defined**                          | 3 — `LogLayer`, `ActorRole`, `RetentionPolicy`                                                       |
| **Event Types Registered**                 | 28 in `VALID_EVENT_TYPES` — validated at API layer, rejected before any Firestore write              |
| **API Endpoints**                          | 4 — `GET /health`, `POST /log`, `POST /log/batch`, `GET /logs`                                       |
| **Firestore Collection**                   | `unified_logs`                                                                                       |
| **Composite Indexes**                      | 3 — `study_id+timestamp`, `study_id+layer+timestamp`, `trace_id+timestamp`                           |
| **Security Rules**                         | Write: `if false` (Admin SDK only) \| Read: authenticated researcher/admin via Firestore role lookup |
| **Docker Base Image**                      | `python:3.11-slim`                                                                                   |
| **Exposed Port**                           | `8080` (Cloud Run standard)                                                                          |
| **Credentials Protected**                  | `.dockerignore` blocks `.env`, `__pycache__`, `.git`, `tests/`                                       |

### Test Suite — 32 Tests, 90%+ Coverage, 0 Failures

| Tier             | File             | Purpose                                                   |
| ---------------- | ---------------- | --------------------------------------------------------- |
| Unit             | `test_models.py` | Schema validation, enum enforcement, UUID auto-generation |
| Mocked (CI-safe) | `test_api.py`    | HTTP layer — no Firestore, no cloud costs in CI           |
| Emulator         | `test_writer.py` | Real write/read cycle against local Firestore emulator    |

### What the test suite actually proves

- An unknown `event_type` is **rejected with 422** at the API layer — Firestore never sees bad data
- `trace_id` **auto-generates as UUID v4** when not provided — callers don't manage it
- Batch writes are **atomic** — either all 500 succeed or none do
- The Firestore client is a **singleton** — initialized once via `@lru_cache`, never re-instantiated
- FastAPI's event loop is **never blocked** — all Firestore writes go through `run_in_executor`

---

## Section 3 — Architecture Decisions

Three decisions made, each documented in `.gsd/DECISIONS.md` as an ADR.
I want to confirm alignment on all three before Phase 2 execution begins.

### ADR-001 — FastAPI on Cloud Run

| Factor           | Firebase Functions (Python) | FastAPI on Cloud Run ✅                         |
| ---------------- | --------------------------- | ----------------------------------------------- |
| Cold start       | ~3–5 seconds                | <500ms with `min-instances=1`                   |
| Concurrency      | 1 request / instance        | 80+ configurable                                |
| Python ecosystem | Restricted                  | Full — numpy, pandas needed for Phase 6 exports |
| Cost             | Per invocation              | Per container-second (~$5–10/month warm)        |

A logging system that adds 3–5s latency to participant sessions defeats its own
purpose. Cloud Run with one warm instance eliminates cold starts permanently.

**What this means practically:** Cloud Run URL must be in `VUE_APP_LOG_API_URL`
(frontend `.env`) and `LOG_SERVICE_URL` (Cloud Functions env). The Dockerfile is
ready — deployment is waiting on which GCP project to use.

---

### ADR-002 — Firestore Only

No new database added to the stack. All logs write into one `unified_logs`
collection — same Firebase project, same Admin SDK, same security rule pattern
the team already knows.

**Non-obvious detail worth noting:** `log_id` is a **UUID v4**, not Firestore's
auto-ID. Random UUIDs distribute writes across Firestore's internal shards
automatically, preventing write hotspots as log volume grows. The three composite
indexes cover every query pattern needed without any denormalization.

---

### ADR-003 — Async Fire-and-Forget + Buffer Fallback

Every `emitLog()` call from the frontend returns immediately — the POST to Cloud
Run happens in the background. Participant sessions are never blocked.

**The buffer fallback (the non-obvious part):**
When Cloud Run is temporarily unreachable, failed log entries push to a
`sessionStorage` array (`__log_buffer`). On the next successful emit, the buffer
flushes first (FIFO). On `beforeunload`, one final flush attempt fires. Buffer
cap is 100 entries to prevent memory leaks.

About 20 lines of JavaScript. Transforms **silent data loss** into
**eventual delivery** — a critical difference for scientific-grade research
where losing 10 minutes of logs mid-session invalidates a study.

---

### Two Technical Details Worth Calling Out

**`run_in_executor` wrapping:** The `firebase-admin` Python SDK is synchronous
only — there is no async Firestore client. Calling it directly inside a FastAPI
`async def` endpoint would block the event loop for every request. Wrapping it
with `asyncio.get_event_loop().run_in_executor(None, sync_write_fn)` — `None`
uses the default `ThreadPoolExecutor`, correct for I/O-bound Firestore calls —
keeps FastAPI fully non-blocking. Most Python developers building on Firebase
miss this entirely.

**Client write prohibition:** `allow write: if false` in Firestore security
rules means no browser client can ever write to `unified_logs` directly. The
Admin SDK bypasses rules — so only the Cloud Run microservice, running under its
service account, can write logs. The frontend can never corrupt or forge the
audit trail.

---

## Section 4 — Roadmap

### Current Position

```
Phase 1 ✅ COMPLETE     Foundation — FastAPI, Pydantic models, Firestore, 32 tests
Phase 2 🔄 IN PROGRESS  Technical Layer — Cloud Functions + Vuex auth/study hooks
Phase 3 ⬜ NOT STARTED  Methodological Layer — task/session/heuristic events
Phase 4 ⬜ NOT STARTED  AI Decision Layer — AHP weights, sentiment, eye tracking
Phase 5 ⬜ NOT STARTED  Traceability Engine + GDPR
Phase 6 ⬜ NOT STARTED  Export + Visualization + Polish + Docs
```

### Hour Allocation

| Phase      | Focus                | Hours    | Key Deliverable                                  |
| ---------- | -------------------- | -------- | ------------------------------------------------ |
| 1          | Foundation           | 25h ✅   | Microservice + 32 tests + Firestore schema       |
| 2          | Technical Layer      | 25h      | 10 event types across Cloud Functions + Vuex     |
| 3          | Methodological Layer | 20h      | Task / session / consent events in Vue.js        |
| 4          | AI Decision Layer    | 25h      | AHP weight logs + sentiment + eye tracking audit |
| 5          | Traceability + GDPR  | 25h      | trace_id engine + anonymizer + GDPR endpoints    |
| 6          | Export + Viz + Docs  | 35h      | CSV/JSON/PDF/JSON-LD + D3 timeline + full docs   |
| **Buffer** | Mentor review + bugs | **20h**  | Reserved — not planned against                   |
| **Total**  |                      | **175h** |                                                  |

### Why Phase 4 received more hours than originally scoped

`weight_function/main.py` is a **450-line AHP service** with pairwise comparison
matrices, eigenvector calculations, and consistency ratio checks. Logging it
incorrectly — capturing the wrong intermediate values — produces an audit trail
that appears to document reproducibility but actually cannot reproduce the AI's
decisions. That's worse than no logging at all.

Phase 4 starts with 5–6h annotating the AHP code before writing a single log
hook. The 25h allocation (up from original 20h) exists specifically for this.

---

## Section 5 — Codebase Reconnaissance

Before writing the microservice, I scanned the entire RUXAILAB codebase to map
every injection point. Here is exactly what I found:

| Area Scanned          | Finding                                                              | Phase Where This Gets Hooked                        |
| --------------------- | -------------------------------------------------------------------- | --------------------------------------------------- |
| Vuex Modules          | **13 total**                                                         | Phase 2 (auth, study) + Phase 3 (tasks, heuristics) |
| Cloud Functions       | **10 total** (triggers, HTTPS, scheduled)                            | Phase 2                                             |
| Firestore Controllers | **11 files** with CRUD operations                                    | Phase 2 write event mapping                         |
| External Axios Calls  | **25+ calls** (eye tracker, sentiment, facial, transcription, email) | Phase 2 `API_CALLED`/`API_ERROR`                    |
| AHP Service           | **450-line** `weight_function/main.py`                               | Phase 4 AI decision logs                            |
| Frontend Logging      | **Zero** structured logging anywhere in `src/`                       | Clean slate — no conflicts                          |
| Functions Logging     | `utils/logger.js` exists — Google Cloud Logging only                 | Not queryable, not centralized                      |
| Error Tracking        | None — no Sentry, no Crashlytics                                     | No conflicts                                        |

**The headline finding:** There is no structured, queryable logging anywhere in
RUXAILAB today. Every event type in the system is genuinely new infrastructure —
not a reimplementation of anything existing.

---

## Section 6 — The 4 Questions

These are the only 4 things I cannot move forward without your input on.
Everything else is already decided and documented.

---

**Q1 — Cloud Run or Firebase Functions?**

_"I've implemented FastAPI on Cloud Run — the rationale is in ADR-001, primarily
the cold start problem for a latency-sensitive logging layer. If there's a reason
Cloud Run doesn't work for RUXAILAB's infrastructure — billing constraints, GCP
project access, a team preference for staying fully Firebase-native — I can
restructure. What's your preference?"_

> If Cloud Run → proceed with current implementation, need GCP project confirmation
> If Firebase Functions → ~4h restructure, cold start mitigation needs discussion

---

**Q2 — Same Firebase project or separate project for `unified_logs`?**

_"My default is same Firebase project — one `firestore.rules` file, no additional
credential chains, same Admin SDK setup the team already uses. But if RUXAILAB
has a reason to isolate research log data separately — compliance, billing
separation, data governance — I can build for that. The code change is contained
to one credential swap in `db/firestore_client.py`. Do you have a preference?"_

> Default assumption used after 48h if no response: same Firebase project

---

**Q3 — Any existing logging or observability I should know about?**

_"During the codebase scan I found zero structured logging in the frontend and a
`logger` utility in Cloud Functions that writes to Google Cloud Logging — but
nothing queryable or centralized. Before I start adding hooks in Phase 2, is
there anything I've missed? Any Firebase Extension, any APM trial, any logging
attempt in a branch or external tool that I should know about before I build
on top of it?"_

---

**Q4 — Would you review the POC before the proposal deadline?**

_"The POC is live right now — 15 Python files, 831 lines of code, 32 passing
tests, Dockerfile ready. I'd love 15 minutes of your time to look at three
specific things:_

1. _Is `LogEntry` missing any fields you'd want for research reproducibility?_
2. _Are the 28 event types covering the right study lifecycle moments?_
3. _Any concerns about the Firestore schema before I deploy it?_

_A schema fix now is 30 minutes. After Phase 2 hooks are wired to the schema,
a field change touches 25+ integration points across Cloud Functions and Vuex.
The earlier the review, the cheaper any correction."_

---

## Section 7 — Risks I'm Already Aware Of

Raising these proactively — I'd rather you hear them from me first.

**Risk 1 — AHP Complexity in Phase 4**
The 450-line AHP service is mathematically dense. Logging it incorrectly gives
false confidence in reproducibility — an audit trail that looks complete but
cannot actually replay the AI's decisions. Mitigation: 5–6h of annotation before
any Phase 4 log hooks. Hours already allocated.

**Risk 2 — Phase 6 Scope Expansion**
D3.js timeline visualization and PDF generation with `weasyprint` both reliably
surface edge cases. Mitigation: Phase 6 budget is 35h (up from original 30h).
If D3.js becomes a time sink, fall back to Chart.js — simpler, faster, still
delivers the visualization requirement. The 20h buffer is separate and untouched
by this.

**Risk 3 — Firestore Write Pressure Under Concurrent Sessions**
High-frequency concurrent sessions could create write pressure on `unified_logs`.
Two mitigations already built in: `log_id` UUID v4 distributes writes across
Firestore shards automatically, and `POST /log/batch` handles up to 500 writes
per atomic batch. At RUXAILAB's current scale this is not an active concern —
but the architecture is ready if it ever becomes one.

---

## Section 8 — What I Need From You

| #   | Question                          | Urgency   | What It Unblocks                              |
| --- | --------------------------------- | --------- | --------------------------------------------- |
| Q1  | Cloud Run vs Firebase Functions   | 🔴 High   | Phase 2.0 — deployment                        |
| Q2  | Same vs separate Firebase project | 🔴 High   | Phase 2.0 — deployment                        |
| Q3  | Any existing logging I've missed  | 🟡 Medium | Phase 2.1 — hook placement                    |
| Q4  | 15-min POC schema review          | 🟡 Medium | Schema correctness before 25+ hooks are wired |

**My commitment:**
Every architecture decision is in `.gsd/DECISIONS.md` as an ADR — you can always
see why a choice was made, not just what was chosen. `JOURNAL.md` and `STATE.md`
update every session — you always know exactly where I am. I will not start
Phase 2.1 hooks until Q1 and Q2 are answered.

---

## Closing

> _"RUXAILAB currently has no way to answer: 'What exactly happened during
> participant 3's session, what did the AI compute, and can those results be
> reproduced?' This project answers that question. Phase 1 is done, the
> architecture is documented, and I'm ready to build the rest —
> I just need your input on these 4 decisions."_

---

_Harshit Virmani | github.com/Harshit2405-2004_
_RUXAILAB GSoC 2026 — Unified Logging & Traceability System_
