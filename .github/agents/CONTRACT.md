# agents/CONTRACT.md
# GLOBAL CONTRACT - Agent I/O, Artifacts, Gates

## Purpose
This document is the source of truth for all agents. Each agent MUST:
- read its input as JSON,
- return JSON ONLY (no markdown, no comments, no text outside of JSON),
- produce artifacts in the repo as files,
- respect gates and not proceed if the gate is not met.

**Exception — Orchestrator final response**: When the Orchestrator reaches DONE or BLOCKED, it returns a human-readable text summary (not JSON) directed at the user. All inter-agent communication remains JSON-only.

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
- `.agents-work/<session>/architecture.md` (full mode only — skipped in lean mode)
- `.agents-work/<session>/adr/` (optional)
- `.agents-work/<session>/tasks.yaml`
- `.agents-work/<session>/status.json`
- `.agents-work/<session>/report.md` (at the end)
- `.agents-work/<session>/design-specs/` (Designer output, when applicable)
- `.agents-work/<session>/research/` (Researcher output, when applicable)

This centralized location allows users to inspect, review, and track agent progress across sessions.
Previous sessions are read-only — agents may reference them but MUST NOT modify them.

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
  "user_decisions": [{"question":"...","answer":"...","timestamp":"ISO-8601","state_context":"which state triggered ASK_USER"}],
  "retry_counts": {"T-001": {"FIX_REVIEW": 0, "FIX_TESTS": 0, "FIX_SECURITY": 0, "FIX_BUILD": 0}},
  "known_issues": ["..."],
  "last_ci_result": "unknown|green|red",
  "last_update": "ISO-8601 timestamp"
}

Note: per-task status (not-started, in-progress, implemented, completed, blocked) lives ONLY in `tasks.yaml`. Do NOT duplicate it here.

## tasks.yaml — single source of truth for task status
Agents that change a task's state MUST update the `status` field in `.agents-work/<session>/tasks.yaml`.
Valid values: `not-started` | `in-progress` | `implemented` | `completed` | `blocked`.

### Task status lifecycle
- `not-started` — initial state, set by Planner at creation
- `in-progress` — set by Coder when implementation begins
- `implemented` — set by Coder after successful implementation; task awaits review/QA/security gates
- `completed` — set by Orchestrator after ALL gates pass (Reviewer OK + QA OK + Security OK if required)
- `blocked` — set by any agent that encounters a blocker for this task

**Important**: Coder MUST NOT set `completed` directly. Coder sets `implemented`. The Orchestrator promotes `implemented` → `completed` only after all gates for that task have passed.
`tasks.yaml` is the single source of truth for per-task progress. `status.json` tracks session-level state only (workflow position, retries, decisions).

**User-facing dashboard**: `tasks.yaml` and `status.json` are actively monitored by the user to track progress in real time. Agents MUST keep both files accurate and up-to-date at every state transition — they serve as the project's live dashboard, not just internal coordination artifacts.

## Status enum — usage guide
- `OK` — work completed successfully. Used by all agents.
- `BLOCKED` — cannot proceed; includes concrete blocker description. Used by all agents.
- `FAIL` — unrecoverable failure. Used by all agents.
- `NEEDS_INFO` — research is incomplete, more information needed. Used by **Researcher only**.
- `NEEDS_DECISION` — findings require a product/user decision (e.g., security medium fixes). Used by **Security** when medium-severity findings need user judgment. Orchestrator treats this as an ASK_USER trigger.

## Gates (hard blockers)
The agent MUST return status=BLOCKED if:
- a required context file from task.context_files is missing and cannot be run safely without it
- the task requires testing, but there are no tools or a way to run them
- a high-risk issue has been detected: security high/critical, non-compliance with the spec, missing key tests

## Artifact content validation (gates)
Gates check not only file existence but minimal content validity:
- `spec.md` MUST contain at minimum: Goals, Acceptance Criteria, Definition of Done sections
- `acceptance.json` MUST contain at least one AC with id, description, and verify fields
- `architecture.md` MUST contain at minimum: Overview and Modules/components sections (not required in lean mode — skip this gate if session is lean)
- `tasks.yaml` MUST contain at least one task with id, status, goal, and acceptance_checks

If an artifact exists but fails content validation, the consuming agent MUST return `status: BLOCKED` with the specific validation failure.

## project_type — checklist qualification
The `project_type` field in the input JSON tells agents what kind of project they are working on. Agents with context-sensitive checklists (Reviewer, QA, Security) MUST skip checklist items that are not applicable to the project type:
- `web` — full checklist (CSRF, XSS, SQL injection, tenant scoping, etc.)
- `api` — skip template/UI checks; focus on auth, input validation, rate limiting
- `cli` — skip CSRF, XSS, tenant scoping, template checks; focus on input validation, privilege escalation, secrets
- `lib` — skip CSRF, XSS, tenant scoping, template checks; focus on API safety, input validation, dependency hygiene
- `mixed` — apply all checks relevant to the specific files being reviewed

## Style rules
- In output: JSON only (exception: Orchestrator final user-facing response — see Purpose section).
- In .md files: regular markdown, but simple and to the point.

## Canonical agent names
Use these exact names in `dispatch.agent`, `recommended_agent`, and `runSubagent` calls:
`SpecAgent` | `Architect` | `Planner` | `Designer` | `Researcher` | `Coder` | `Reviewer` | `QA` | `Security` | `Integrator` | `Docs` | `Orchestrator`

Frontmatter `name` fields use kebab-case (`spec-agent`, `architect`, etc.) for system identification. Dispatch and inter-agent references MUST use PascalCase names from the list above.
