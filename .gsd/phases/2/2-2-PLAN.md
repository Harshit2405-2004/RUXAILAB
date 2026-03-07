---
phase: 2
plan: 2
wave: 2
---

# Plan 2.2: Frontend Auth & Study Technical Event Hooks

## Objective

Wire the frontend Vuex store (Auth and Study modules) to emit the remaining technical event interactions mapping directly to system operations initiated by users in the UI.

## Context

- .gsd/SPEC.md
- src/features/auth/store/Auth.js
- src/store/modules/Study.js
- src/ux/UserTest/store/UserStudy.js

## Tasks

<task type="auto">
  <name>Implement Frontend HTTP Webhook</name>
  <files>src/utils/logger.js</files>
  <action>
    - Create a lightweight `axios`/`fetch` utility in `src/utils/logger.js` pointing to `process.env.VUE_APP_LOG_API_URL`.
    - Include full Local Buffer implementation from ADR-003. Provide a `flushBuffer()` method handling `__log_buffer` up to 100 entries, invoked at the start of every emit.
    - Expose `emitSystemTechnicalLog(type, studyId, payload)`.
    - Ensure failed network requests gracefully buffer without crashing the user's flow.
  </action>
  <verify>Review the network implementation of logger.js</verify>
  <done>Lightweight network wrapper created</done>
</task>

<task type="auto">
  <name>Hook Auth Events</name>
  <files>src/features/auth/store/Auth.js</files>
  <action>
    - Emit `USER_SIGNED_IN` with actor ID inside the login success flow.
    - NOTE: actor_id for auth events passes Firebase UID directly. Full anonymization handled in Phase 5 middleware. Mark these logs `is_anonymized: false` until Phase 5.
    - Emit `USER_SIGNED_OUT` during logout flow.
  </action>
  <verify>grep_search USER_SIGNED_IN in Auth.js</verify>
  <done>Login/logout actions produce audit logs</done>
</task>

<task type="auto">
  <name>Hook Study CRUD Events</name>
  <files>src/store/modules/Study.js</files>
  <action>
    - Attach `STUDY_CREATED`, `STUDY_UPDATED`, and `STUDY_DELETED` to their respective Vuex action dispatches.
    - Crucially: Emit `STUDY_DELETED` strictly inside the `.then()` or after the `await` — never in the catch block or prior to successful database deletion.
  </action>
  <verify>grep_search STUDY_CREATED in Study.js</verify>
  <done>Study management actions trace to technical history</done>
</task>

<task type="auto">
  <name>Hook Session Events</name>
  <files>src/ux/UserTest/store/UserStudy.js</files>
  <action>
    - Wire `SESSION_STARTED` to the beginning of the participant sequence.
    - Wire `SESSION_ENDED` to completion of the study.
  </action>
  <verify>grep_search SESSION_STARTED in UserStudy.js</verify>
  <done>Session lifecycle technical events emitted successfully.</done>
</task>

## Success Criteria

- [ ] Authentication produces `USER_SIGNED_IN` & `OUT` traces.
- [ ] Study management actions trace their technical mutations.
- [ ] The `emitSystemTechnicalLog` utility handles fetch operations without crashing the frontend flow on network lag.
