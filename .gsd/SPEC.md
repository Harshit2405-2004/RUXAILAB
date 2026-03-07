# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision

Build a **Unified Logging and Traceability System** for RUXAILAB that captures every meaningful event across three layers — technical (system ops), methodological (study lifecycle), and AI decisions (weight computation) — into a single queryable Firestore collection with anonymization, GDPR compliance, and export capabilities.

## Goals

1. **Three-Layer Logging** — Capture technical, methodological, and AI decision events with structured schemas
2. **Traceability** — Link related events via `trace_id` across participant sessions, study lifecycles, and AI computations
3. **GDPR Compliance** — Anonymize participant data, record consent, support Right to Access and Right to Erasure
4. **Export & Visualization** — Export logs in CSV/JSON/PDF/JSON-LD; provide timeline visualization of study sessions
5. **Zero Impact on UX** — Async fire-and-forget logging that adds <50ms latency to any user action

## Non-Goals (Out of Scope)

- Real-time log streaming dashboard (post-GSoC)
- Integration with external APM (Sentry, Datadog)
- Automated alerting on log patterns
- Historical data migration (only new sessions logged)

## Users

| Role             | Usage                                                           |
| ---------------- | --------------------------------------------------------------- |
| **Researcher**   | Audit study sessions, export for papers, verify reproducibility |
| **Evaluator**    | View personal session timeline, understand AI scoring           |
| **Participant**  | GDPR: request data export or erasure                            |
| **System Admin** | Monitor Cloud Function health, debug errors                     |

## Constraints

- **Stack**: Must integrate with existing Vue 3 + Vuex + Firebase
- **Python**: Backend microservice in Python (FastAPI on Cloud Run)
- **Timeline**: 175 hours over 13 weeks (GSoC 2026)
- **Budget**: Firebase Spark/Blaze plan — minimize Firestore writes
- **Team**: Solo contributor (Harshit) with mentor review (Marc)

## Success Criteria

- [ ] All Vuex store actions emit structured log events
- [ ] All Cloud Functions emit structured log events
- [ ] `weight_function/main.py` AHP computation emits AI decision logs
- [ ] Participant data is anonymized before write
- [ ] GDPR export and erasure endpoints functional
- [ ] Study session timeline visualization renders in UI
- [ ] 90%+ test coverage on log writer and anonymizer
- [ ] <50ms latency overhead per logged action
- [ ] A complete study session of 3+ participants generates a queryable audit trail retrievable via `GET /audit/{study_id}` within 5 seconds
