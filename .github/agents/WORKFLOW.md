# agents/WORKFLOW.md
# GLOBAL WORKFLOW - State Machine, Dispatch, Loops

## Purpose
This document describes a workflow driven by an Orchestrator. It is a state machine with gates and repair loops.

## State Machine
INTAKE -> DESIGN -> PLAN -> IMPLEMENT_LOOP -> INTEGRATE -> RELEASE -> DONE
Lean mode: INTAKE_LEAN -> IMPLEMENT_LOOP -> INTEGRATE -> DONE

All artifacts are stored in `.agents-work/<session>/` (see CONTRACT.md for session naming).

### INTAKE
Agent: SpecAgent
Produces: `.agents-work/<session>/spec.md`, `.agents-work/<session>/acceptance.json`, `.agents-work/<session>/status.json` (initial creation)
Gate: all three files exist, spec.md has testable ACs, status.json has valid schema

### INTAKE_LEAN (lean mode only)
Orchestrator delegates initial artifact creation to SpecAgent (with lean flag).
SpecAgent is used here as a utility for artifact bootstrapping - it is not a mandatory dispatch in the lean mode agent list.
- Short `.agents-work/<session>/spec.md` (goal + AC only)
- `.agents-work/<session>/acceptance.json`
- Single-task `.agents-work/<session>/tasks.yaml`
- `.agents-work/<session>/status.json` (initial creation)
- No `architecture.md` - lean mode skips the DESIGN phase entirely

Note: Orchestrator does not create files directly - it delegates via dispatch. Exception: if SpecAgent is unavailable in lean mode, Orchestrator MAY create minimal artifacts directly as the sole exception to the no-edit rule.
Gate: artifacts exist. If Coder discovers complexity, exit lean mode and restart from full INTAKE.

### DESIGN
Agents: Researcher (if research needed - see Orchestrator's Researcher trigger policy), then Architect, then Designer (if task involves UI/UX)
Produces: `.agents-work/<session>/research/` (if Researcher involved), `.agents-work/<session>/architecture.md`, `.agents-work/<session>/adr/ADR-001.md` (if needed), `.agents-work/<session>/design-specs/` (if Designer involved)
Gate: architecture consistent with spec, risks recorded. If research was requested, research report exists. If UI involved, design spec exists.

### PLAN
Agent: Planner
Produces: `.agents-work/<session>/tasks.yaml`
Gate: tasks have dependencies, acceptance_checks and done_when

### IMPLEMENT_LOOP
For each task ready (deps done):
- Coder implements
- Reviewer reviews (with ALL session-changed files, not just current task — see full-scope context rule below)
- QA tests (if the task concerns behavior/logic or acceptance)
- Security (if risk_flags contains security or affects auth/input/network)
Gate per task:
- Reviewer OK
- QA OK (if required)
- Security OK (if required). If Security returns `NEEDS_DECISION` (medium findings), Orchestrator enters ASK_USER before proceeding.
- Task marked `status: implemented` by Coder, then promoted to `completed` by Orchestrator after all gates pass

#### Full-scope context rule for Reviewer
Orchestrator MUST provide Reviewer with the list of ALL files changed during the entire session (not just the current task's files) via a `session_changed_files` field in the `task` object. This is separate from `context_files` (which lists session artifacts like `spec.md`, `architecture.md`, etc.).

**Per-task review (incremental)**: Reviewer receives `session_changed_files` for awareness but focuses deep reading on the current task's files. Reviewer checks `session_changed_files` selectively — only following dependencies and callers of the current task's changes to detect cross-task interactions.

**Final review (comprehensive)**: Reviewer reads all non-deleted files from `session_changed_files` in full and reviews deleted files via diff only. This is the exhaustive cross-cutting pass.

This two-tier approach keeps per-task reviews efficient (O(1) per task) while the final review provides full O(n) coverage once.

#### Cross-task final review (mandatory in full mode)
After ALL tasks in IMPLEMENT_LOOP reach `completed` status, and BEFORE entering INTEGRATE:
1. Orchestrator dispatches Reviewer one final time with `task.id: "meta"` and `task.goal: "Cross-task final review of all session changes"`.
2. `session_changed_files` in `task` MUST list ALL files changed during the session (by any agent — Coder, Integrator, Docs, etc.) with `change_type` per entry. `context_files` lists session artifacts as usual.
3. Reviewer reads the full content of every non-deleted file in `session_changed_files` and applies the full checklist with focus on cross-cutting concerns: interface consistency between tasks, no duplicated logic, no conflicting assumptions, no regressions from task interactions. For deleted files, Reviewer verifies intentional removal and no dangling references via diff.
4. Gate: Final review must be OK (or PASS WITH NOTES). If BLOCKED, enter FIX_REVIEW targeting the specific findings.

This step is skipped in lean mode (single-task, already reviewed).

### ASK_USER
Trigger: Orchestrator enters this state when human judgment is needed.
Mechanism: Orchestrator uses `ask_questions` tool (NEVER plain text that ends the turn).
Protocol: follow the canonical ASK_USER protocol in `CONTRACT.md` (single source of truth for schema, persistence, retries, and resume behavior).
Resume: only after CONTRACT validation passes, then return to the state that triggered ASK_USER.
If persistence cannot be completed after retries, transition to `BLOCKED`.
Examples:
- Ambiguous requirements with multiple valid interpretations
- Reviewer PASS WITH NOTES (user decides which notes to fix)
- Design trade-offs with no clear winner
- Scope creep risk (confirm before expanding)
- Deterministic security trigger: Security agent returns `NEEDS_DECISION` (medium findings) -> Orchestrator MUST enter ASK_USER (see Orchestrator ASK_USER trigger policy for details)

### INTEGRATE
Agent: Integrator (full mode) or Orchestrator directly (lean mode)
Purpose: green build, conflicts, full pipeline
Gate: CI/build green OR if no CI, local commands from acceptance_checks pass

In **lean mode**, Orchestrator runs acceptance_checks commands directly instead of dispatching Integrator. If checks fail, enter FIX_BUILD as normal.

### RELEASE
Agents:
- Docs updates README/report
- Integrator finalizes release artifacts (tag/release notes if applicable)
Gate: README current, `.agents-work/<session>/report.md` ready, all ACs met

### DONE
Orchestrator final report in `.agents-work/<session>/report.md` and `.agents-work/<session>/status.json` current_state=DONE

## Repair loops
- If Reviewer BLOCKED -> FIX_REVIEW -> Coder updates -> back to Reviewer
- If QA BLOCKED -> FIX_TESTS -> Coder/QA updates -> back to QA
- If Security BLOCKED -> FIX_SECURITY -> Coder updates -> back to Security
- If build/CI red -> FIX_BUILD -> Integrator/Coder -> back to INTEGRATE

### Retry budget
Each repair loop has a **maximum of 3 iterations** per task.
After 3 failed attempts, Orchestrator MUST enter ASK_USER with:
- Summary of what was tried and why it failed
- Options: (a) try a different approach, (b) accept with known issues, (c) simplify scope, (d) user guidance
Retry counts are tracked in `.agents-work/<session>/status.json` under `retry_counts`.

## Dispatch rules (must)
Orchestrator MUST use all core agents at least once in a full run:
- SpecAgent, Architect, Planner, Coder, Reviewer, QA, Security, Integrator, Docs
Optional (used when applicable):
- Researcher (when task requires technology evaluation, codebase analysis, or best practices research)
- Designer (when task involves UI/UX)
- ASK_USER (when human judgment is needed)
Exception: Security can be "OK no findings," but must be run.

**Lean mode exception**: In lean mode, only Coder, Reviewer, and (conditionally) QA and Security are mandatory. SpecAgent is used for INTAKE_LEAN artifact creation (delegated by Orchestrator) but is not counted as a "mandatory core agent" for dispatch tracking. Architect, Planner, Designer, Integrator, Docs, and Researcher are skipped in lean mode. Orchestrator handles INTEGRATE checks directly and creates `report.md` directly (since Docs is skipped).

## Definition of Done (global)
DONE only if:
- All criteria from `.agents-work/<session>/acceptance.json` are met
- `.agents-work/<session>/status.json` is up-to-date and current_state=DONE
- `.agents-work/<session>/status.json` has no unresolved `user_decisions` with `status: pending`
- `.agents-work/<session>/report.md` contains: what was done, how to run, how to test, known issues

## Context files enforcement
Orchestrator MUST populate `context_files` in every dispatch. If Designer produced a spec for a task, it MUST be included in context_files for Coder, Reviewer, and QA. Omitting it is a workflow violation. See Orchestrator's "Context files enforcement" section for the full per-agent matrix.
