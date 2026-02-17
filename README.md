# Coordinated Agent Team

A framework for **autonomous software delivery** by a coordinated team of AI agents, driven by a state machine.

## Concept

Instead of a single monolithic AI agent, projects are delivered by a **team of 12 specialized agents**, each fulfilling a distinct role — from requirements gathering, through architecture, planning, implementation, code review, testing, security audit, all the way to documentation and release. The entire workflow is managed by an **Orchestrator** that never writes code itself — it only delegates tasks and enforces quality gates.

## Architecture

### State machine (workflow)

```
INTAKE → DESIGN → PLAN → IMPLEMENT_LOOP → INTEGRATE → RELEASE → DONE
```

Simplified mode for trivial changes:
```
INTAKE_LEAN → IMPLEMENT_LOOP → INTEGRATE → DONE
```

Additional repair states: `FIX_REVIEW`, `FIX_TESTS`, `FIX_SECURITY`, `FIX_BUILD`, `ASK_USER`, `BLOCKED`.

### Agents

| #  | Agent          | Model            | Role                                                         |
|----|----------------|------------------|--------------------------------------------------------------|
| 00 | **Orchestrator** | Claude Opus 4.6  | Controls workflow, delegates tasks, never writes code       |
| 01 | **SpecAgent**    | Claude Opus 4.6  | Creates specifications (`spec.md`, `acceptance.json`)       |
| 02 | **Architect**    | GPT-5.3-Codex    | Designs architecture, creates ADRs                          |
| 03 | **Planner**      | GPT-5.3-Codex    | Creates task backlog (`tasks.yaml`)                         |
| 04 | **Coder**        | Claude Opus 4.6  | Implements tasks                                            |
| 05 | **Reviewer**     | GPT-5.3-Codex    | Code review with checklist + devil's advocate               |
| 06 | **QA**           | Gemini 3 Pro     | Tests, acceptance criteria validation                       |
| 07 | **Security**     | GPT-5.3-Codex    | Security audit (XSS, CSRF, SSRF, auth, secrets)            |
| 08 | **Integrator**   | GPT-5.3-Codex    | Integration, green build, release                           |
| 09 | **Docs**         | Claude Haiku 4.5 | Documentation, README, final report                         |
| 10 | **Designer**     | Gemini 3 Pro     | UX/UI design specs (invoked conditionally)                  |
| 11 | **Researcher**   | Claude Opus 4.6  | Technology research, pattern analysis, codebase investigation (conditionally) |

### Communication via artifacts

Agents do not communicate through chat — **the source of truth is the files in the repository**:

| Artifact             | Format   | Description                                |
|----------------------|----------|--------------------------------------------|
| `spec.md`            | Markdown | Requirements specification (PRD)           |
| `acceptance.json`    | JSON     | Acceptance criteria                        |
| `architecture.md`    | Markdown | System architecture                        |
| `tasks.yaml`         | YAML     | Task backlog with dependencies and status  |
| `status.json`        | JSON     | Session state, retries, user decisions     |
| `report.md`          | Markdown | Final report                               |
| `adr/ADR-XXX.md`     | Markdown | Architecture Decision Records              |
| `design-specs/`      | Markdown | UX/UI specifications from Designer         |
| `research/`          | Markdown | Research reports from Researcher           |

Each session's artifacts are stored in `.agents-work/YYYY-MM-DD_<slug>/`.

### Quality gates

The workflow does not progress if:
- Required artifacts are missing (`spec.md`, `acceptance.json`, `tasks.yaml`)
- **Reviewer** blocks (BLOCKED)
- **QA** blocks (BLOCKED)
- **Security** blocks (high severity)
- CI/build is red

Repair loops have a budget of **max 3 attempts** — after exhaustion, the issue is escalated to the user (`ASK_USER`).

## Configuration files

```
.github/
└── agents/
    ├── 00-orchestrator.md    # Orchestrator role definition
    ├── 01-spec-agent.md      # SpecAgent role definition
    ├── 02-architect.md       # Architect role definition
    ├── 03-planner.md         # Planner role definition
    ├── 04-coder.md           # Coder role definition
    ├── 05-reviewer.md        # Reviewer role definition
    ├── 06-qa.md              # QA role definition
    ├── 07-security.md        # Security role definition
    ├── 08-integrator.md      # Integrator role definition
    ├── 09-docs.md            # Docs role definition
    ├── 10-designer.md        # Designer role definition
    ├── 11-researcher.md      # Researcher role definition
    ├── CONTRACT.md           # Global agent I/O contract
    └── WORKFLOW.md           # State machine, dispatch rules
```
## Tech stack

- **Environment:** VS Code + GitHub Copilot Chat (custom agents / chat participants)
- **Multi-model:** Claude Opus 4.6, GPT-5.3-Codex, Gemini 3 Pro, Claude Haiku 4.5
- **Demo projects:** Vanilla JS, zero frameworks, zero dependencies, static hosting
- **Quality gates:** `npm test`, `npm run lint`, `npm run build` + manual checklists
- **Artifacts:** Markdown, JSON, YAML — all version-controlled in the repo

## How it works

1. The user describes a goal in chat with the Orchestrator
2. Orchestrator creates a session in `.agents-work/` and delegates to **SpecAgent** (specification)
3. **Researcher** investigates technologies/patterns if needed, then **Architect** designs the architecture, **Planner** breaks it into tasks
4. **Coder** implements tasks one by one
5. After each task: **Reviewer** (code review) → **QA** (tests) → optionally **Security**
6. Repair loops (`FIX_*`) if a gate blocks, max 3 attempts
7. **Integrator** ensures green build, **Docs** generates documentation
8. Orchestrator closes the session with `DONE` status and generates `report.md`

## Demo projects

### 🍅 FocusFlow (demo-pomidoro)

A Pomodoro Timer app with a distraction journal. Vanilla JS, zero dependencies, static hosting.

**Features:** 25-min timer (Date.now-based), idle/running/paused/completed states, distraction journal with validation, daily counters, localStorage, JSON import/export, keyboard shortcuts.

**Status:** ✅ DONE — fully delivered by the agent pipeline.

### 🚦 Traffic Simulator (demo-traffic-simulator)

A minimal intersection traffic simulation. Vanilla JS + Canvas API, zero dependencies.

**Features:** map and vehicle rendering on canvas, braking logic, traffic lights, parameter controls (intensity, speed, density), live statistics (active vehicles, average speed, throughput).
