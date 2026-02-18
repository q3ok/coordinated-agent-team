# agents/WORKFLOW.md
# GLOBAL WORKFLOW - State Machine, Dispatch, Loops

## Purpose
This document describes a workflow driven by an Orchestrator. It is a state machine with gates and repair loops.

### Source-of-truth boundaries
- This file is the canonical source for workflow states, transitions, and gate behavior.
- `CONTRACT.md` is the canonical source for persistence schema, decision record validity, retry/write semantics, and resume protocol details.
- `DISPATCH-REFERENCE.md` is the canonical source for pre-dispatch validation and prompt structure.

## State Machine
INTAKE -> DESIGN -> APPROVE_DESIGN -> PLAN -> REVIEW_STRATEGY -> IMPLEMENT_LOOP -> INTEGRATE -> RELEASE -> DONE
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

### APPROVE_DESIGN (mandatory user approval gate, full mode only)
Trigger: Orchestrator enters this state automatically after DESIGN completes (spec + architecture + design specs if applicable are ready).
The Orchestrator sets `current_state: APPROVE_DESIGN` in `status.json` (this is a distinct workflow state, NOT the generic `ASK_USER`).
Mechanism: Orchestrator uses `ask_questions` tool to present the user with a summary of:
- `spec.md` — scope, acceptance criteria, assumptions
- `architecture.md` — modules, data flows, key decisions / ADRs
- Design specs (if Designer was involved) — layout, interactions, components

The Orchestrator MUST ask the user to review these artifacts and confirm:
1. Whether they approve the proposed solution as-is, OR
2. Whether they have comments, corrections, or concerns.

Gate: User explicitly approves. If the user requests changes, Orchestrator routes corrections back to the appropriate agent (SpecAgent, Architect, or Designer), then re-enters APPROVE_DESIGN. Workflow MUST NOT proceed to PLAN until the user approves.

Persistence: The approval is recorded as a `user_decisions` entry in `status.json` (decision_id format: `UD-APPROVE-DESIGN`). Orchestrator MUST follow the full ASK_USER protocol from CONTRACT.md, including:
1. Write `UD-APPROVE-DESIGN` entry with `status: pending` BEFORE calling `ask_questions`.
2. After user response, classify the outcome:
   - **User approves** ("looks good", "approved", "go ahead", etc.): set `answer` to `"approved"`.
   - **User requests changes** ("fix X", "change Y", "I have concerns"): set `answer` to `"changes-requested: <summary>"`, append an audit record to `.agents-work/<session>/approve-design-history.jsonl` (JSON Lines, append-only), and set `gate_tracking.APPROVE_DESIGN.correction_status` to `queued`. Route corrections back to the appropriate agent, then re-enter APPROVE_DESIGN (the existing `UD-APPROVE-DESIGN` entry is updated in-place per the well-known ID rule). While routing corrections, Orchestrator MUST update `gate_tracking.APPROVE_DESIGN` (`queued` -> `dispatched` -> `completed`) in `status.json` so resume does not duplicate correction dispatches.
   - **No answer / invalid answer**: treat as missing mandatory gate decision (see CONTRACT.md mandatory gate exception). Re-ask up to 3 times, then enter `BLOCKED` if still unresolved. This gate retry counter is intentionally in-memory and not persisted across resume.
   - **Explicit defer/cancel by user**: mark `cancelled` with explicit reason and enter `BLOCKED` (`mandatory_user_decision_missing`).
3. **Gate verification**: Re-read `status.json` and confirm `UD-APPROVE-DESIGN` has `status: answered` AND `answer` starts with `"approved"`. If the answer starts with `"changes-requested"`, do NOT proceed — this is not a passing gate. If verification fails (persistence error), retry up to 3 times. If all retries fail, enter BLOCKED.
4. Only then proceed to PLAN.

Lean mode: This gate is skipped (lean mode has no DESIGN phase).

### PLAN
Agent: Planner
Produces: `.agents-work/<session>/tasks.yaml`
Gate: tasks have dependencies, acceptance_checks and done_when

### REVIEW_STRATEGY (mandatory user choice gate, full mode only)
Trigger: Orchestrator enters this state automatically after PLAN completes (tasks.yaml is ready).
The Orchestrator sets `current_state: REVIEW_STRATEGY` in `status.json` (this is a distinct workflow state, NOT the generic `ASK_USER`).
Mechanism: Orchestrator uses `ask_questions` tool to ask the user about the review/QA/security strategy for the implementation phase.

The Orchestrator MUST present:
1. The total number of tasks planned.
2. A brief summary of task scope and complexity.
3. The two available strategies:
   - **Per-batch review**: Review + QA + Security runs after each batch of tasks (more thorough, takes longer, catches issues earlier).
   - **Single final review**: Review + QA + Security runs once after all tasks are coded (faster, but issues found late may require more rework).
4. The Orchestrator's recommendation:
   - For large multi-step projects (≥5 tasks, or tasks with cross-cutting dependencies, or high risk_flags): recommend **per-batch review**.
   - For small/simple projects (<5 tasks, low complexity, no security flags): recommend **single final review**.

Gate: User explicitly chooses a strategy. The choice is stored as a `user_decisions` entry in `status.json` (decision_id format: `UD-REVIEW-STRATEGY`) and affects IMPLEMENT_LOOP behavior. Orchestrator MUST follow the full ASK_USER protocol from CONTRACT.md, including:
1. Write `UD-REVIEW-STRATEGY` entry with `status: pending` BEFORE calling `ask_questions`.
2. After user response, persist only canonical strategy values:
   - `"per-batch"` OR `"single-final"`.
   - If answer is missing/invalid/non-canonical, re-ask up to 3 times (mandatory gate exception in CONTRACT.md).
   - If user explicitly defers/cancels, enter `BLOCKED` (`mandatory_user_decision_missing`).
3. **Read-after-write verification**: Re-read `status.json` and confirm `UD-REVIEW-STRATEGY` has `status: answered` and canonical `answer` (`per-batch|single-final`). If verification fails, retry up to 3 times. If all retries fail, enter BLOCKED.
4. Only then proceed to IMPLEMENT_LOOP.
5. **During IMPLEMENT_LOOP**: Before dispatching Reviewer/QA/Security, Orchestrator MUST re-read `UD-REVIEW-STRATEGY` from `status.json` to confirm the chosen strategy. NEVER rely on in-memory state alone — always verify from disk. This prevents context loss after summarization or session resume.

Lean mode: This gate is skipped (lean mode always does per-task review by default).

#### IMPLEMENT_LOOP behavior based on review strategy
- **Per-batch review** (default for large projects): After each Coder task completes, Reviewer + QA (if applicable) + Security (if applicable) run immediately. This is the standard flow described below.
- **Single final review**: Coder implements all tasks sequentially. After ALL tasks reach `implemented` status, a single combined Reviewer + QA + Security pass runs for all changes at once — this combined pass IS the cross-task final review (dispatched with `task.id: "meta"`). There is no additional separate final review step. Repair loops still apply — if the single review finds issues, Coder fixes them and re-review runs.

### IMPLEMENT_LOOP
Behavior depends on the chosen review strategy (see REVIEW_STRATEGY gate above; lean mode always uses per-batch).

#### Per-batch review path
For each task ready (deps done):
1. Coder implements the task.
2. Reviewer reviews (with ALL session-changed files, not just current task — see full-scope context rule below).
3. QA tests (if the task concerns behavior/logic or acceptance).
4. Security audits (if risk_flags contains security or affects auth/input/network).

Gate per task:
- Reviewer OK
- QA OK (if required)
- Security OK (if required). If Security returns `NEEDS_DECISION` (medium findings), Orchestrator enters ASK_USER before proceeding.
- Task marked `status: implemented` by Coder, then promoted to `completed` by Orchestrator after all gates pass.

#### Single-final review path
For each task ready (deps done):
1. Coder implements the task.
2. Task marked `status: implemented` by Coder. **No Reviewer/QA/Security dispatch at this point.**

After ALL tasks reach `implemented` status:
1. Orchestrator dispatches a single combined Reviewer (with `task.id: "meta"` and `task.goal: "Single-final review of all session changes"`) + QA (if applicable) + Security (if applicable) pass covering all changes at once. This combined pass IS the cross-task final review — there is no separate final review step in single-final mode.
2. `session_changed_files` in `task` MUST list ALL files changed during the session (by any agent) with `change_type` per entry. Reviewer reads the full content of every non-deleted file and applies the full checklist with cross-cutting focus (interface consistency, no duplicated logic, no conflicting assumptions, no regressions).
3. Gate (applied once, for the entire batch):
   - Reviewer OK
   - QA OK (if required)
   - Security OK (if required). If Security returns `NEEDS_DECISION`, Orchestrator enters ASK_USER before proceeding.
4. If the combined review finds issues, Coder fixes them and the combined review re-runs (standard repair loop, up to CONTRACT retry limits).
5. After the combined review passes, all tasks are promoted to `completed` by Orchestrator, and workflow proceeds directly to INTEGRATE (skipping the per-batch-only cross-task final review).

#### Full-scope context rule for Reviewer
Orchestrator MUST provide Reviewer with the list of ALL files changed during the entire session (not just the current task's files) via a `session_changed_files` field in the `task` object. This is separate from `context_files` (which lists session artifacts like `spec.md`, `architecture.md`, etc.).

**Per-task review (incremental)**: Reviewer receives `session_changed_files` for awareness but focuses deep reading on the current task's files. Reviewer checks `session_changed_files` selectively — only following dependencies and callers of the current task's changes to detect cross-task interactions.

**Final review (comprehensive)**: Reviewer reads all non-deleted files from `session_changed_files` in full and reviews deleted files via diff only. This is the exhaustive cross-cutting pass.

This two-tier approach keeps per-task reviews efficient (O(1) per task) while the final review provides full O(n) coverage once.

#### Cross-task final review (mandatory in full mode, per-batch strategy only)
This step applies ONLY when the review strategy is **per-batch**. In **single-final** mode, the combined review pass (see above) already serves as the cross-task final review — do NOT run it a second time.

After ALL tasks in IMPLEMENT_LOOP reach `completed` status, and BEFORE entering INTEGRATE:
1. Orchestrator dispatches Reviewer one final time with `task.id: "meta"` and `task.goal: "Cross-task final review of all session changes"`.
2. `session_changed_files` in `task` MUST list ALL files changed during the session (by any agent — Coder, Integrator, Docs, etc.) with `change_type` per entry. `context_files` lists session artifacts as usual.
3. Reviewer reads the full content of every non-deleted file in `session_changed_files` and applies the full checklist with focus on cross-cutting concerns: interface consistency between tasks, no duplicated logic, no conflicting assumptions, no regressions from task interactions. For deleted files, Reviewer verifies intentional removal and no dangling references via diff.
4. Gate: Final review must be OK (or PASS WITH NOTES). If BLOCKED, enter FIX_REVIEW targeting the specific findings.

This step is skipped in lean mode (single-task, already reviewed).

### Session resume for mandatory gate states
- If `current_state: APPROVE_DESIGN`, resume APPROVE_DESIGN directly from `status.json` (not via ASK_USER state recovery).
- If `UD-APPROVE-DESIGN.answer` starts with `"changes-requested:"`, consult `gate_tracking.APPROVE_DESIGN.correction_status` before dispatching corrections. If the field is missing/null (or `gate_tracking` is absent), treat it as `"none"`:
  - `none` -> set `correction_status` to `queued` (backward compatibility for old sessions), then continue.
  - `queued` -> correction dispatch is allowed.
  - `dispatched` -> do not dispatch duplicate correction work; first verify completion and move to `completed`.
  - `completed` -> do not dispatch correction work again; re-ask approval.
- If `current_state: REVIEW_STRATEGY`, resume REVIEW_STRATEGY directly and enforce canonical strategy answer before leaving the gate.
- ASK_USER resume routing still uses `state_context` from CONTRACT.md.

### ASK_USER (ad-hoc decisions only)
Trigger: Orchestrator enters this state (`current_state: ASK_USER`) when human judgment is needed for ad-hoc decisions.
Note: `APPROVE_DESIGN` and `REVIEW_STRATEGY` are NOT `ASK_USER` — they are distinct workflow states with their own `current_state` values. They use `ask_questions` and the ASK_USER persistence protocol, but have deterministic state transitions and well-known decision IDs.
Mechanism: Orchestrator uses `ask_questions` tool (NEVER plain text that ends the turn).
Protocol: follow the canonical ASK_USER protocol in `CONTRACT.md` (single source of truth for schema, persistence, retries, and resume behavior).
Resume: only after CONTRACT validation passes, then return to the state recorded in `state_context` of the resolved decision (this is the workflow state that was active when ASK_USER was triggered).
If persistence cannot be completed after retries, transition to `BLOCKED`.
Examples of ad-hoc ASK_USER triggers:
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
Mandatory user checkpoints (full mode only):
- APPROVE_DESIGN (after DESIGN, before PLAN — user must approve spec + architecture + design)
- REVIEW_STRATEGY (after PLAN, before IMPLEMENT_LOOP — user chooses review/QA/security strategy)
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

## Project-level instructions (copilot-instructions.md)
If a file `.github/copilot-instructions.md` exists in the repository, the Orchestrator MUST instruct every subagent to read it as part of their dispatch. This file contains project-level conventions, coding standards, design system rules, and other context that all agents must follow.

Detection and persistence rules:
- At session start, detect existence and persist result in `.agents-work/<session>/status.json` under:
  - `runtime_flags.copilot_instructions_exists`
  - `runtime_flags.copilot_checked_at`
- Before every dispatch, read this value from disk (not memory-only cache).
- If the value is missing/uncertain after resume/context compression, re-check filesystem and re-persist before dispatching.

If `runtime_flags.copilot_instructions_exists` is true, include the instruction line in every dispatch prompt (see DISPATCH-REFERENCE.md for exact template behavior).

### Precedence rule
`copilot-instructions.md` describes the **project environment** (tech stack, conventions, design system). It MUST NOT override agent behavioral rules or workflow controls. Precedence order (highest first):
1. CONTRACT.md (I/O schema, gates, role boundaries)
2. Agent specs (`.github/agents/XX-agent.md`)
3. WORKFLOW.md / DISPATCH-REFERENCE.md
4. `.github/copilot-instructions.md` (project conventions — lowest priority)

Conflicts MUST be resolved in favor of higher-priority sources, with the conflict noted in `artifacts.notes`.

## Context files enforcement
Orchestrator MUST populate `context_files` in every dispatch. If Designer produced a spec for a task, it MUST be included in context_files for Coder, Reviewer, and QA. Omitting it is a workflow violation. See Orchestrator's "Context files enforcement" section for the full per-agent matrix.
