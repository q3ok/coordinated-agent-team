# agents/CONTRACT.md
# GLOBAL CONTRACT - Agent I/O, Artifacts, Gates

## Purpose
This document is the source of truth for all agents. Each agent MUST:
- read its input as JSON,
- return JSON ONLY (no markdown, no comments, no text outside of JSON),
- produce artifacts in the repo as files,
- respect gates and not proceed if the gate is not met.

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
  "status": "OK|BLOCKED|NEEDS_INFO|FAIL",
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
    "recommended_agent": "SpecAgent|Architect|Planner|Coder|Reviewer|QA|Security|Integrator|Docs|Orchestrator",
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
- `.agents-work/<session>/architecture.md`
- `.agents-work/<session>/adr/` (optional)
- `.agents-work/<session>/tasks.yaml`
- `.agents-work/<session>/status.json`
- `.agents-work/<session>/report.md` (at the end)
- `.agents-work/<session>/design-specs/` (Designer output, when applicable)

This centralized location allows users to inspect, review, and track agent progress across sessions.
Previous sessions are read-only — agents may reference them but MUST NOT modify them.

## Context files enforcement (mandatory)
The Orchestrator MUST populate `context_files` fully when dispatching tasks. Agents MUST read ALL files listed in `context_files` before starting work. If a `context_files` entry references a design-spec, the agent MUST read and follow it.

If a required context file is missing, the agent MUST return `status: BLOCKED` with the missing file path.

## status.json - minimal schema
`.agents-work/<session>/status.json` MUST exist and be updated by agents who change the state of work:

{
  "current_state": "INTAKE|DESIGN|PLAN|IMPLEMENT_LOOP|INTEGRATE|RELEASE|DONE|ASK_USER|BLOCKED",
  "session": "YYYY-MM-DD_short-slug",
  "completed_tasks": ["T-001"],
  "blocked_tasks": [{"id":"T-002","reason":"..."}],
  "assumptions": ["..."],
  "user_decisions": [{"question":"...","answer":"...","timestamp":"ISO-8601","state_context":"which state triggered ASK_USER"}],
  "retry_counts": {"T-001": {"FIX_REVIEW": 0, "FIX_TESTS": 0, "FIX_SECURITY": 0, "FIX_BUILD": 0}},
  "known_issues": ["..."],
  "last_ci_result": "unknown|green|red",
  "last_update": "ISO-8601 timestamp"
}

## Gates (hard blockers)
The agent MUST return status=BLOCKED if:
- a required context file from task.context_files is missing and cannot be run safely without it
- the task requires testing, but there are no tools or a way to run them
- a high-risk issue has been detected: security high/critical, non-compliance with the spec, missing key tests

## Style rules
- In output: JSON only.
- In .md files: regular markdown, but simple and to the point.
