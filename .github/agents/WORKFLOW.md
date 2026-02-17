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
Produces: `.agents-work/<session>/spec.md`, `.agents-work/<session>/acceptance.json`
Gate: both files exist and have testable ACs

### INTAKE_LEAN (lean mode only)
Orchestrator creates minimal artifacts directly (no SpecAgent):
- Short `.agents-work/<session>/spec.md` (goal + AC only)
- `.agents-work/<session>/acceptance.json`
- Single-task `.agents-work/<session>/tasks.yaml`
Gate: artifacts exist. If Coder discovers complexity, exit lean mode and restart from full INTAKE.

### DESIGN
Agents: Architect, then Designer (if task involves UI/UX)
Produces: `.agents-work/<session>/architecture.md`, `.agents-work/<session>/adr/ADR-001.md` (if needed), `.agents-work/<session>/design-specs/` (if Designer involved)
Gate: architecture consistent with spec, risks recorded. If UI involved, design spec exists.

### PLAN
Agent: Planner
Produces: `.agents-work/<session>/tasks.yaml`
Gate: tasks have dependencies, acceptance_checks and done_when

### IMPLEMENT_LOOP
For each task ready (deps done):
- Coder implements
- Reviewer reviews
- QA tests (if the task concerns behavior/logic or acceptance)
- Security (if risk_flags contains security or affects auth/input/network)
Gate per task:
- Reviewer OK
- QA OK (if required)
- Security OK (if required)
- Task marked completed in `.agents-work/<session>/status.json`

### ASK_USER
Trigger: Orchestrator enters this state when human judgment is needed.
Mechanism: Orchestrator uses `ask_questions` tool (NEVER plain text that ends the turn).
Resume: after receiving the user's answer, Orchestrator records it in `.agents-work/<session>/status.json` under `user_decisions` and returns to the state that triggered ASK_USER.
Examples:
- Ambiguous requirements with multiple valid interpretations
- Reviewer PASS WITH NOTES (user decides which notes to fix)
- Design trade-offs with no clear winner
- Scope creep risk (confirm before expanding)
- Security medium findings (fix-now vs fix-later is a product decision)

### INTEGRATE
Agent: Integrator
Purpose: green build, conflicts, full pipeline
Gate: CI/build green OR if no CI, local commands from acceptance_checks pass

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
Orchestrator MUST use all agents at least once in a full run:
- SpecAgent, Architect, Planner, Coder, Reviewer, QA, Security, Integrator, Docs
Optional (used when applicable):
- Designer (when task involves UI/UX)
- ASK_USER (when human judgment is needed)
Exception: Security can be "OK no findings," but must be run.

## Definition of Done (global)
DONE only if:
- All criteria from `.agents-work/<session>/acceptance.json` are met
- `.agents-work/<session>/status.json` is up-to-date and current_state=DONE
- `.agents-work/<session>/report.md` contains: what was done, how to run, how to test, known issues

## Context files enforcement
Orchestrator MUST populate `context_files` in every dispatch. If Designer produced a spec for a task, it MUST be included in context_files for Coder, Reviewer, and QA. Omitting it is a workflow violation. See Orchestrator's "Context files enforcement" section for the full per-agent matrix.