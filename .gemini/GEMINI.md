# RUXAILAB — Agent Configuration

> Optimized for Antigravity (Claude) contributing to [RUXAILAB](https://github.com/ruxailab/RUXAILAB).
> Canonical methodology: [PROJECT_RULES.md](../PROJECT_RULES.md)

---

## Project Context

| Key          | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| **Stack**    | Vue 2 + Vuex + Vuetify + Firebase (Firestore/RTDB/Auth/Functions)     |
| **Language** | JavaScript (ES Modules in `/functions`, Vue SFC in `/src`)            |
| **Styling**  | Vuetify + vanilla CSS                                                 |
| **i18n**     | `vue-i18n` — locales at `src/app/plugins/locales/{en,pt_br}.json`     |
| **Testing**  | Vitest (unit), Playwright (E2E)                                       |
| **Linting**  | ESLint + Prettier                                                     |
| **Branch**   | Always branch from `develop`, PR to `develop`                         |
| **Commits**  | Conventional: `fix(store):`, `refactor(functions):`, `test:`, `feat:` |

---

## 🔴 Critical Rules (Learned from Failures)

### Git Staging Discipline

```
ALWAYS: prettier --write → git add → git commit
NEVER:  git add → prettier --write → git commit (OVERWRITES STAGED CHANGES!)
```

> **Why:** Prettier `--write` modifies the working copy. If you stage first, then format, the staged version becomes stale and the commit misses your changes.

### PR Media Requirement

```
Every PR MUST include at least one image, GIF, or video:
- Screenshot of code diff (from GitHub commit page)
- Screenshot of terminal output (for backend changes)
- Screenshot of UI (for frontend changes)

CI auto-closes PRs without media. Cannot reopen via API.
```

### Browser Subagent Limitations

```
❌ Browser CANNOT log into GitHub (no stored auth)
✅ Use `gh` CLI for: issue creation, PR creation, commenting
✅ Browser CAN take screenshots of public GitHub pages
✅ Browser CAN capture recordings for walkthroughs
```

### GitHub CLI Workarounds

```
# Issue templates may block non-interactive creation
# Workaround: write body to file, use --body-file
echo "body content" > /tmp/issue_body.md
gh issue create --title "..." --body-file /tmp/issue_body.md

# PR creation with media: user must create via browser
# Agent prepares: branch, commit, PR body file, screenshot
```

---

## Contribution Workflow Checklist

```
□ 1. Check existing issues & PRs (no duplicates)
□ 2. Create issue → comment requesting assignment
□ 3. Branch from develop: git checkout -b fix/description
□ 4. Make code changes
□ 5. Format: npx prettier --write <files>
□ 6. Lint: npx eslint <files> (warnings OK, no errors)
□ 7. Stage: git add <files>
□ 8. Commit: git commit -m "type(scope): description"
□ 9. Push: git push origin <branch>
□ 10. Capture screenshot of diff from GitHub commit page
□ 11. Create PR with screenshot embedded in description
□ 12. Add "Closes #XXXX" in PR body
```

---

## Codebase Patterns

### Error Handling (Vuex Store)

```javascript
// Import toast utility
import { showError } from '@/shared/utils/toast'

// In catch blocks — use i18n keys
catch (error) {
  console.error('[StoreName] description:', error)
  showError('errors.i18nKey')
}
```

### Cloud Functions Logging

```javascript
// Use project logger, never raw console.log
import logger from '../utils/logger.js'

logger.info('functionName: description', { key: value })
logger.error('functionName: error description', { error: error.message })
logger.warn('functionName: warning', { context })
```

### i18n Error Keys

- Add to `src/app/plugins/locales/en.json` under `errors` object
- Portuguese translations (`pt_br.json`) can be deferred to native speakers
- `showError()` auto-resolves i18n keys via `resolveMessage()`

---

## Multi-Agent Orchestration & Model Selection

RUXAILAB uses a strict **Manager-Worker** multi-agent orchestration model via the GSD framework (`/.agent`) and persistent memory (`/memory`).

### 1. The Managers (Planners)

**Models**: `Claude 3 Opus`, `Gemini 1.5 Pro` / `Gemini 3.1 Pro (High)`
**Role**: The Architects and Strategists.

**Core Responsibilities & Workflows**:

- Execute `/.agent/workflows/map.md` to understand the codebase structure and update architecture docs.
- Execute `/.agent/workflows/plan.md` to decompose requirements into executable `PLAN.md` phases.
- Manage the project state machine explicitly (updates `SPEC.md`, `ROADMAP.md`, `STATE.md`, `TODO.md`, and `/memory/status.md`).

**Performance Optimization Playbook (How to act as a Manager)**:

1. **Chain-of-Thought Planning**: Before writing `PLAN.md` files, Managers MUST explicitly perform step-by-step reasoning evaluating the architectural trade-offs, potential latency, and state side-effects.
2. **Constitutional AI Directives**:
   - _Never write codebase implementation directly._ Your sole output format for execution is exact prompts and instructions for Worker agents.
   - _Protect Context Budgets._ Enforce the Token Optimization Guide (`docs/token-optimization-guide.md`). Plan tasks that keep Workers strictly under 50% context loading to prevent quality degradation.
   - _Aggressive Atomicity._ Limit every `PLAN.md` document to 2-3 atomic tasks maximum. If a phase is larger, break it into multiple waves.
3. **Execution Instructions Quality**: When writing `<task>` blocks in `PLAN.md`, include explicit `<verify>` commands (e.g., specific `pytest` or `npm test` scripts based on `docs/runbook.md`) and undeniable `<done>` acceptance criteria.
4. **Handoff Mechanics**: Always conclude a planning session by updating `STATE.md` with Next Steps and dumping current progress into `/memory/status.md`. Ensure to clearly state: _"Ready for execution. A Worker (Flash/Sonnet) model should take over from here."_

### 2. The Workers (Executors)

**Models**: `Claude 3.5 Sonnet`, `Gemini 1.5 Flash`
**Role**: The Engineers.

**Core Responsibilities & Workflows**:

- Execute `/.agent/workflows/execute.md` to consume exact instructions from `PLAN.md` files.
- Implement the code changes atomically, format via Prettier, and run build/tests.

**Performance Optimization Playbook (How to act as a Worker)**:

1. **Search-First execution**: Never `view_file` entirely if you can `grep_search` or use `/outline` first (per `docs/token-optimization-guide.md`). Save context budget for code completion.
2. **Strict Verification**: Before marking a task complete, run the exact `<verify>` commands listed in the plan (e.g., `pytest`, `npm test`, or `npm run lint`).
3. **Escalation Protocol**: _Do not alter architectural flow._ If a test fails 3 times (`docs/runbook.md` 3-Strike Rule) or a dependency is missing, STOP. Log the failure explicitly to `/memory/status.md` indicating "Blocked - escalate to Manager".
4. **Handoff Mechanics**: Update the phase's `SUMMARY.md` file and `/memory/status.md` when execution successfully completes, notifying the Manager that implementation is finished.

### 3. Coordination & Memory Handoffs

The `/memory` directory is the standard brain-sync layer when coordinating multi-model shifts:

- **`memory/status.md`** — The active handoff document. Managers write the global progress and execution targets; Workers write their execution results or blocking issues.
- **`memory/agent_patterns.md`** — Reusable codebase architectural patterns (e.g. `run_in_executor`) distilled by Managers for Workers to apply seamlessly.
- **Workflow Loop**: The transition between Planning and Execution MUST dump context into memory, followed by a formal model shift out of the reasoning tier and into the execution tier.

---

## Quick Reference

```
Before coding     → Check for existing issues/PRs first
Before file read  → Search first (grep, view_file_outline)
After formatting  → Stage files (never stage before format!)
Before PR         → Screenshot + media in description
After each issue  → Update memory/status.md
Long conversations → Recommend model switch for mechanical tasks
```

---

_Tuned: 2026-03-05 | Based on session analysis with 3 failure mitigations_
_Canonical rules: [PROJECT_RULES.md](../PROJECT_RULES.md)_
