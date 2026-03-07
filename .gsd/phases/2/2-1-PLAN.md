---
phase: 2
plan: 1
wave: 2
---

# Plan 2.1: Cloud Function Technical Event Hooks

## Objective

Update the existing Cloud Functions in `functions/src` to emit structured technical logs. This involves retrofitting `utils/logger.js` to dispatch async HTTP POST requests to our `LOG_SERVICE_URL` whenever triggers fire or API calls are made.

**Event coverage across Phase 2 plans**:

- 2.1 → FUNCTION_TRIGGERED (triggers), API_CALLED, API_ERROR (HTTPS) ← 3 events
- 2.2 → STUDY_CREATED, STUDY_UPDATED, STUDY_DELETED (Study.js) ← 3 events
- 2.2 → USER_SIGNED_IN, USER_SIGNED_OUT (Auth.js) ← 2 events
- 2.2 → SESSION_STARTED, SESSION_ENDED (UserStudy store) ← 2 events

## Context

- .gsd/SPEC.md
- functions/src/utils/logger.js
- functions/src/triggers/
- functions/src/https/

## Tasks

<task type="auto">
  <name>Retrofit Cloud Function Logger</name>
  <files>functions/src/utils/logger.js, functions/package.json</files>
  <action>
    - Install `axios` in functions if not present.
    - Update the internal `logger.js` (or create `logEmitter.js`) to expose an async function `emitTechnicalLog({ eventType, studyId, sessionId = "system", actorId = "system", payload = {} })`.
    - This function must dispatch a non-blocking `axios.post` to `process.env.LOG_SERVICE_URL`.
    - Conform to the `LogEntry` Pydantic model contract (`layer="technical"`, `actor_role="system"`).
  </action>
  <verify>View updated logger logic emitting HTTP REST payload</verify>
  <done>Logger exposes `emitTechnicalLog` configured correctly</done>
</task>

<task type="auto">
  <name>Hook Trigger Functions</name>
  <files>functions/src/triggers/onTestCreate.js, functions/src/triggers/onTestUpdate.js</files>
  <action>
    - Inject the new `emitTechnicalLog` function.
    - Emit `FUNCTION_TRIGGERED` logging the exact test/study ID and context during Firestore triggers.
  </action>
  <verify>Review trigger functions for new emission statements</verify>
  <done>Trigger functions emit structured trace logs to microservice</done>
</task>

<task type="auto">
  <name>Hook HTTPS Functions (API Calls)</name>
  <files>functions/src/https/eyeTracking.js, functions/src/https/email.js</files>
  <action>
    - Wire `API_CALLED` and `API_ERROR` into the HTTPS endpoints.
    - Catch block operations should emit error log async (fire-and-forget), then re-throw or return the original error.
  </action>
  <verify>Review API call functions for new emission statements</verify>
  <done>External API calls from Cloud Functions trace successful/failed remote operations</done>
</task>

<task type="auto">
  <name>Write Jest Unit Tests for Log Emitter</name>
  <files>functions/test/utils/logEmitter.test.js</files>
  <action>
    - Write Jest unit tests for `logEmitter.js`.
    - Mock axios POST.
    - Test `emitTechnicalLog` sends correct payload shape (including default `sessionId`).
    - Test failure is swallowed (doesn't throw).
    - Ensure verification commands are fully passing.
  </action>
  <verify>npm test</verify>
  <done>Log emission layer has valid test coverage</done>
</task>

## Success Criteria

- [ ] `functions/src/utils/logger.js` performs async HTTP payload drops to Cloud Run.
- [ ] Native Firestore Triggers fire `FUNCTION_TRIGGERED` technical logs.
- [ ] HTTPS operations trace `API_CALLED` and `API_ERROR`.
