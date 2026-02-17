# agents/DISPATCH-REFERENCE.md
# DISPATCH REFERENCE — Mandatory read before every runSubagent call

## Purpose
This file contains the exact dispatch format, context_files requirements, I/O schemas, and failure policy. The Orchestrator MUST `read_file` this document before EVERY `runSubagent` call — no exceptions. This is a hard gate: no dispatch without a fresh read of this file.

---

## 1. Dispatch template (mandatory — verbatim)
Every `runSubagent` call MUST use this template. Do not shorten, omit sections, or paraphrase — even on the 10th dispatch in a session. Copy-paste and fill in the placeholders.

```
You are the {AGENT_NAME} agent. Follow your spec from `.github/agents/{AGENT_FILE}`.
Read CONTRACT.md (`.github/agents/CONTRACT.md`) for I/O schema and gates.

Session: `.agents-work/{SESSION}/`

Input JSON:
{FULL_INPUT_JSON}

Your MANDATORY first steps:
1. Read ALL files listed in context_files above.
2. Read your agent spec from `.github/agents/{AGENT_FILE}`.
3. Perform your work according to spec.
4. Update task status in `.agents-work/{SESSION}/tasks.yaml` if your role requires it.
5. Return your output as JSON per CONTRACT.md.
```

`{FULL_INPUT_JSON}` MUST be the complete Universal Input JSON (see section 4 below) with all fields populated per the schema. Note: `session_changed_files` is conditionally required — mandatory for Reviewer dispatches, omit (or pass `[]`) for other agents.

---

## 2. Pre-dispatch checklist (self-validation)
Before EVERY `runSubagent` call, verify:
- [ ] You have read THIS FILE (`DISPATCH-REFERENCE.md`) in the current turn
- [ ] Prompt contains the full dispatch template above (not a shortened version)
- [ ] `context_files` lists all required files for this agent (see section 3)
- [ ] All `context_files` paths use the actual session name (not `<session>` placeholder)
- [ ] `task.id` matches the task from `tasks.yaml` OR is `meta` (for cross-cutting dispatches like final review)
- [ ] `project_type` is included
- [ ] `repo_state` is included with current branch and CI status

If any item fails, fix the prompt before dispatching. Never send an incomplete dispatch.

---

## 3. Mandatory context_files per agent

| Agent | Required context_files |
|-------|----------------------|
| **SpecAgent** | (none — creates initial artifacts) |
| **Architect** | `spec.md`, `acceptance.json`, research report (if Researcher was involved) |
| **Designer** | `spec.md`, `architecture.md`, `acceptance.json` |
| **Researcher** | `spec.md`, `acceptance.json` (if available), `architecture.md` (if available) |
| **Planner** | `spec.md`, `acceptance.json`, `architecture.md`, design-spec (if Designer involved), research report (if Researcher involved) |
| **Coder** | `spec.md`, `tasks.yaml`, `architecture.md` (if exists), design-spec (**MANDATORY if Designer produced one**) |
| **Reviewer** | `spec.md`, `tasks.yaml`, `architecture.md` (if exists), design-spec (if applicable). Additionally: `session_changed_files` in task object (see full-scope rule below — NOT in `context_files`) |
| **QA** | `spec.md`, `acceptance.json`, `tasks.yaml` |
| **Security** | `tasks.yaml`, `architecture.md` (if exists) |
| **Integrator** | `tasks.yaml`, `acceptance.json` |
| **Docs** | `spec.md`, `tasks.yaml`, `acceptance.json`, `architecture.md` (if exists) |

**Designer spec enforcement**: If Designer was involved for a task, the design-spec path MUST be included in `context_files` for **Coder**, **Reviewer**, and **QA**. Omitting it is a workflow violation.

**Reviewer full-scope rule (mandatory)**: When dispatching Reviewer, the `task` object MUST include a `session_changed_files` array listing every file modified in the session so far (by any agent — Coder, Integrator, Docs, etc.). Each entry is an object: `{ "path": "...", "change_type": "added|modified|deleted|renamed" }`. For `change_type: "renamed"`, `old_path` is **required** (not optional). These are repo-relative paths, separate from `context_files`. `context_files` remains for session artifacts only (spec, architecture, tasks, design-specs).

- **Per-task review**: Reviewer focuses deep analysis on the current task's files but uses `session_changed_files` to selectively check cross-task interactions (callers, dependents, shared interfaces).
- **Final review** (`task.id: "meta"`): Reviewer reads all non-deleted files from `session_changed_files` comprehensively. For deleted files, reviews diff for intentional removal and dangling references.

If the Orchestrator cannot determine the full list, it MUST instruct the Reviewer to discover all changes independently (e.g., via `git diff` or `get_changed_files`).

All `context_files` paths must be fully qualified with the session prefix: `.agents-work/<session>/spec.md`, etc. `session_changed_files` paths are repo-relative (no session prefix).

---

## 4. Universal Input JSON schema (compact)
Every dispatch MUST include all fields from the schema below (canonical source: CONTRACT.md). All fields are required except `session_changed_files`, which is **conditionally required**: mandatory for Reviewer dispatches, omit (or pass `[]`) for all other agents.

```json
{
  "task": {
    "id": "T-XXX|meta",
    "title": "Short title",
    "goal": "What to achieve",
    "non_goals": ["What not to do"],
    "context_files": [".agents-work/<session>/spec.md", "..."],
    "session_changed_files": [
      {"path": "src/app.js", "change_type": "modified"},
      {"path": "src/old.js", "change_type": "deleted"},
      {"path": "src/new.js", "old_path": "src/prev.js", "change_type": "renamed"}
    ],
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
```

---

## 5. Expected Output JSON schema (compact)
Every agent returns this (canonical source: CONTRACT.md):

```json
{
  "status": "OK|BLOCKED|NEEDS_INFO|NEEDS_DECISION|FAIL",
  "summary": "1-3 sentences",
  "artifacts": {
    "files_to_create_or_update": [],
    "files_changed": [],
    "tests_added_or_updated": [],
    "commands_to_run": [],
    "manual_steps": [],
    "review_comments": [],
    "findings": [],
    "notes": []
  },
  "gates": {
    "meets_definition_of_done": true,
    "needs_review": false,
    "needs_tests": false,
    "security_concerns": []
  },
  "next": {
    "recommended_agent": "AgentName",
    "recommended_task_id": "T-XXX|meta",
    "reason": "Short"
  }
}
```

**Status enum usage**: `OK` = all agents. `BLOCKED`/`FAIL` = all agents. `NEEDS_INFO` = Researcher only. `NEEDS_DECISION` = Security only (triggers ASK_USER).

---

## 6. Subagent failure policy
If `runSubagent` fails (error, timeout, invalid/unparseable response):
1. Retry the same dispatch up to **2 times** with the same parameters.
2. If all retries fail → enter `BLOCKED` with `blocker: "subagent_failure"` and error details.
3. **NEVER do the failed agent's work yourself.** If Coder fails → BLOCKED, not self-implementation.
4. Sole exception: lean mode INTAKE_LEAN when SpecAgent is unavailable (minimal session artifacts only — never source code).

---

## 7. Canonical agent names
Use these exact names in dispatches:
`SpecAgent` | `Architect` | `Planner` | `Designer` | `Researcher` | `Coder` | `Reviewer` | `QA` | `Security` | `Integrator` | `Docs` | `Orchestrator`

