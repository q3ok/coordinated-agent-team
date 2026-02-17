# agents/CONTRACT.md
# GLOBAL CONTRACT - Agent I/O, Artifacts, Gates

## Purpose
This document is the source of truth for all agents. Each agent MUST:
- read its input as JSON,
- return JSON ONLY (no markdown, no comments, no text outside of JSON),
- produce artifacts in the repo as files,
- respect gates and not proceed if the gate is not met.

**Exception - Orchestrator final response**: When the Orchestrator reaches DONE or BLOCKED, it returns a human-readable text summary (not JSON) directed at the user. All inter-agent communication remains JSON-only.

## Universal Input JSON (all agents)
Each agent gets a structure:

{
  "task": {
    "id": "T-XXX|meta",
    "title": "Short title",
    "goal": "What to achieve",
    "non_goals": ["What not to do"],
    "context_files": [".agents-work/<session>/spec.md", ".agents-work/<session>/architecture.md", ".agents-work/<session>/tasks.yaml", "..."],
    "constraints": ["Hard constraints"],
    "acceptance_checks": ["cmd: ...", "manual: ..."],
    "risk_flags": ["security|perf|breaking-change|none"]
  },
  "project_type": "web|api|cli|lib|mixed",
  "repo_state": {
    "branch": "main",
    "ci_status": "unknown|green|red",
    "last_failed_step": "optional string or null"
  },
  "tools_available": ["read_file", "write_file", "apply_patch", "run_cmd", "search_repo"],
  "artifact_list": ["list of existing files optional"]
}

## Universal Output JSON (all agents)
Each agent returns ONLY:

{
  "status": "OK|BLOCKED|NEEDS_INFO|NEEDS_DECISION|FAIL",
  "summary": "1-3 sentences",
  "artifacts": {
    "files_to_create_or_update": ["... optional"],
    "files_changed": ["... optional"],
    "tests_added_or_updated": ["... optional"],
    "commands_to_run": ["..."],
    "manual_steps": ["... optional"],
    "review_comments": ["... optional"],
    "findings": ["... optional"],
    "notes": ["assumptions, tradeoffs, links to files"]
  },
  "gates": {
    "meets_definition_of_done": true,
    "needs_review": false,
    "needs_tests": false,
    "security_concerns": []
  },
  "next": {
    "recommended_agent": "SpecAgent|Architect|Planner|Designer|Researcher|Coder|Reviewer|QA|Security|Integrator|Docs|Orchestrator",
    "recommended_task_id": "T-XXX|meta",
    "reason": "Short"
  }
}

## Required repository artifacts (global)
All agent artifacts are stored in session subfolders under `.agents-work/` at the repo root.
Each session has the format: `.agents-work/YYYY-MM-DD_<short-slug>/`

Session contents:
- `.agents-work/<session>/spec.md`
- `.agents-work/<session>/acceptance.json`
- `.agents-work/<session>/architecture.md` (full mode only - skipped in lean mode)
- `.agents-work/<session>/adr/` (optional)
- `.agents-work/<session>/tasks.yaml`
- `.agents-work/<session>/status.json`
- `.agents-work/<session>/report.md` (at the end)
- `.agents-work/<session>/design-specs/` (Designer output, when applicable)
- `.agents-work/<session>/research/` (Researcher output, when applicable)

This centralized location allows users to inspect, review, and track agent progress across sessions.
Previous sessions are read-only - agents may reference them but MUST NOT modify them.

## Context files enforcement (mandatory)
The Orchestrator MUST populate `context_files` fully when dispatching tasks. Agents MUST read ALL files listed in `context_files` before starting work. If a `context_files` entry references a design-spec, the agent MUST read and follow it.

If a required context file is missing, the agent MUST return `status: BLOCKED` with the missing file path.

## status.json - minimal schema
`.agents-work/<session>/status.json` MUST exist and be updated by agents who change the state of work.

**Initial creation**: SpecAgent creates `status.json` during INTAKE (alongside `spec.md` and `acceptance.json`). In lean mode, the Orchestrator delegates initial artifact creation (including `status.json`) to a setup dispatch before implementation begins.

**Update responsibility**: Any agent that changes session-level state (assumptions, known_issues, etc.) MUST update `status.json`. The Orchestrator is the logical owner and REQUIRES agents to keep it current via dispatch instructions.

Minimal schema:

{
  "current_state": "INTAKE|INTAKE_LEAN|DESIGN|PLAN|IMPLEMENT_LOOP|INTEGRATE|RELEASE|DONE|ASK_USER|FIX_REVIEW|FIX_TESTS|FIX_SECURITY|FIX_BUILD|BLOCKED",
  "session": "YYYY-MM-DD_short-slug",
  "assumptions": ["..."],
  "user_decisions": [
    {
      "decision_id": "UD-1",
      "question": "...",
      "status": "pending|answered|cancelled|skipped",
      "answer": "... or null",
      "asked_at": "ISO-8601 timestamp",
      "resolved_at": "ISO-8601 timestamp or null",
      "state_context": "which state triggered ASK_USER",
      "resolution_reason": "... or null"
    }
  ],
  "retry_counts": {"T-001": {"FIX_REVIEW": 0, "FIX_TESTS": 0, "FIX_SECURITY": 0, "FIX_BUILD": 0}},
  "known_issues": ["..."],
  "last_ci_result": "unknown|green|red",
  "last_update": "ISO-8601 timestamp"
}

Note: per-task status (not-started, in-progress, implemented, completed, blocked) lives ONLY in `tasks.yaml`. Do NOT duplicate it here.

### ASK_USER protocol (single source of truth)
- Orchestrator is the single writer for `user_decisions` while in `ASK_USER`.
- Before calling `ask_questions`, Orchestrator MUST write one `user_decisions[]` entry per question with:
  - stable `decision_id` - format `UD-<N>` where `<N>` is a sequential integer, unique per session. On resumed sessions, continue from the highest existing `decision_id` + 1.
  - `status: pending`
  - `answer: null`
  - `asked_at`, `state_context`
  - `resolved_at: null`, `resolution_reason: null`
- After user response, Orchestrator MUST update the same entries and persist terminal status:
  - `answered` when user provided an answer
  - `cancelled` when user explicitly cancels/defers the decision
  - `skipped` when the question is no longer applicable due to scope/state changes
- If `ask_questions` returns fewer answers than questions asked (partial response), mark answered questions as `answered` and unanswered ones as `cancelled` with `resolution_reason: "no response provided"`.
- **Exception - security decisions**: When ASK_USER was triggered by a Security `NEEDS_DECISION` response, all security-related questions MUST be explicitly resolved by the user. If any security question receives no answer (partial response), Orchestrator MUST re-ask the unanswered security questions instead of auto-cancelling them. If the user explicitly declines to answer after re-ask, mark as `cancelled` with `resolution_reason` describing the user's explicit deferral (e.g., `"user deferred: will address in next sprint"`). This is a valid terminal state for security decisions - the key constraint is that auto-cancellation (no user interaction) is never allowed, but conscious deferral is.
- Orchestrator MUST keep captured user responses in memory until they are durably written.
- Writes to `status.json` MUST use proper JSON serialization (never build JSON via string concatenation). Use the best write strategy available in the current tooling environment (e.g., full-file write via `create_file` or `replace_string_in_file`).
- Orchestrator MUST perform read-after-write verification by reopening `.agents-work/<session>/status.json` and validating updated records.
- If write or verification fails, Orchestrator MUST retry the write up to 3 times using the same captured response data, without re-asking the user.
- If all retries fail, Orchestrator MUST return/enter `BLOCKED` with an explicit persistence error and recovery instruction. Do not silently continue.
- On session resume, if unresolved `pending` decisions exist, Orchestrator MUST resolve them first by either:
  - asking follow-up only for unresolved decisions, or
  - marking them `skipped` with `resolution_reason` if no longer applicable.

Decision record validity rules:
- `status: pending` -> `answer: null`, `resolved_at: null`, `resolution_reason: null`
- `status: answered` -> non-empty `answer`, non-null `resolved_at`, `resolution_reason` may be null
- `status: cancelled|skipped` -> non-null `resolved_at`, non-empty `resolution_reason`, `answer` may be null

## tasks.yaml - single source of truth for task status
Agents that change a task's state MUST update the `status` field in `.agents-work/<session>/tasks.yaml`.
Valid values: `not-started` | `in-progress` | `implemented` | `completed` | `blocked`.

### Task status lifecycle
- `not-started` - initial state, set by Planner at creation
- `in-progress` - set by Coder when implementation begins
- `implemented` - set by Coder after successful implementation; task awaits review/QA/security gates
- `completed` - set by Orchestrator after ALL gates pass (Reviewer OK + QA OK + Security OK if required)
- `blocked` - set by any agent that encounters a blocker for this task

**Important**: Coder MUST NOT set `completed` directly. Coder sets `implemented`. The Orchestrator promotes `implemented` → `completed` only after all gates for that task have passed.
`tasks.yaml` is the single source of truth for per-task progress. `status.json` tracks session-level state only (workflow position, retries, decisions).

**User-facing dashboard**: `tasks.yaml` and `status.json` are actively monitored by the user to track progress in real time. Agents MUST keep both files accurate and up-to-date at every state transition - they serve as the project's live dashboard, not just internal coordination artifacts.

## Status enum - usage guide
- `OK` - work completed successfully. Used by all agents.
- `BLOCKED` - cannot proceed; includes concrete blocker description. Used by all agents.
- `FAIL` - unrecoverable failure. Used by all agents.
- `NEEDS_INFO` - research is incomplete, more information needed. Used by **Researcher only**.
- `NEEDS_DECISION` - findings require a product/user decision (e.g., security medium fixes). Used by **Security** when medium-severity findings need user judgment. Orchestrator treats this as an ASK_USER trigger.

## Gates (hard blockers)
The agent MUST return status=BLOCKED if:
- a required context file from task.context_files is missing and cannot be run safely without it
- the task requires testing, but there are no tools or a way to run them
- a high-risk issue has been detected: security high/critical, non-compliance with the spec, missing key tests

Additionally, the **Orchestrator** MUST NOT leave ASK_USER state until all `user_decisions` have been persisted and verified in `.agents-work/<session>/status.json` (see ASK_USER protocol). This gate applies only to the Orchestrator - other agents do not have the context to verify it.

## Artifact content validation (gates)
Gates check not only file existence but minimal content validity:
- `spec.md` MUST contain at minimum: Goals, Acceptance Criteria, Definition of Done sections
- `acceptance.json` MUST contain at least one AC with id, description, and verify fields
- `architecture.md` MUST contain at minimum: Overview and Modules/components sections (not required in lean mode - skip this gate if session is lean)
- `tasks.yaml` MUST contain at least one task with id, status, goal, and acceptance_checks
- `status.json` MUST satisfy ASK_USER protocol rules whenever ASK_USER was used in the session
- `status.json` MUST be parseable JSON after every write, and user-provided text fields (e.g., `answer`, `resolution_reason`) MUST be written via JSON serializer (escaped), not raw string interpolation

If an artifact exists but fails content validation, the consuming agent MUST return `status: BLOCKED` with the specific validation failure.

## project_type - checklist qualification
The `project_type` field in the input JSON tells agents what kind of project they are working on. Agents with context-sensitive checklists (Reviewer, QA, Security) MUST skip checklist items that are not applicable to the project type:
- `web` - full checklist (CSRF, XSS, SQL injection, tenant scoping, etc.)
- `api` - skip template/UI checks; focus on auth, input validation, rate limiting
- `cli` - skip CSRF, XSS, tenant scoping, template checks; focus on input validation, privilege escalation, secrets
- `lib` - skip CSRF, XSS, tenant scoping, template checks; focus on API safety, input validation, dependency hygiene
- `mixed` - apply all checks relevant to the specific files being reviewed

## Role boundaries (hard constraint)
The Orchestrator MUST NOT create or edit application source code, test code, or configuration files. Only Coder and Integrator may produce implementation artifacts (Coder for task implementation; Integrator for build/config fixes in INTEGRATE and FIX_BUILD loops). This constraint applies regardless of mode (full or lean) and regardless of circumstances (including subagent failures, retry exhaustion, or time pressure). The Orchestrator's `edit` and `execute` tools exist solely because subagents inherit the Orchestrator's toolset - they are not authorization for the Orchestrator to perform implementation work. Orchestrator's direct file operations are limited to session management artifacts inside `.agents-work/<session>/`.

If a subagent dispatch fails after retries, the Orchestrator MUST enter BLOCKED - never silently assume the agent's role.

## Style rules
- In output: JSON only (exception: Orchestrator final user-facing response - see Purpose section).
- In .md files: regular markdown, but simple and to the point.

## Canonical agent names
Use these exact names in `dispatch.agent`, `recommended_agent`, and `runSubagent` calls:
`SpecAgent` | `Architect` | `Planner` | `Designer` | `Researcher` | `Coder` | `Reviewer` | `QA` | `Security` | `Integrator` | `Docs` | `Orchestrator`

Frontmatter `name` fields use kebab-case (`spec-agent`, `architect`, etc.) for system identification. Dispatch and inter-agent references MUST use PascalCase names from the list above.
