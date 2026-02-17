# Coordinated Agent Team

Framework do **autonomicznego dostarczania oprogramowania** przez skoordynowany zespół agentów AI, sterowany maszyną stanów.

## Idea

Zamiast jednego monolitycznego agenta AI, projekty realizuje **zespół 11 wyspecjalizowanych agentów**, z których każdy pełni odrębną rolę — od zbierania wymagań, przez architekturę, planowanie, implementację, code review, testy, audyt bezpieczeństwa, aż po dokumentację i release. Całością zarządza **Orchestrator**, który nigdy nie pisze kodu samodzielnie — jedynie deleguje zadania i pilnuje bramek jakości.

## Architektura

### Maszyna stanów (workflow)

```
INTAKE → DESIGN → PLAN → IMPLEMENT_LOOP → INTEGRATE → RELEASE → DONE
```

Tryb uproszczony dla trywialnych zmian:
```
INTAKE_LEAN → IMPLEMENT_LOOP → INTEGRATE → DONE
```

Dodatkowe stany naprawcze: `FIX_REVIEW`, `FIX_TESTS`, `FIX_SECURITY`, `FIX_BUILD`, `ASK_USER`, `BLOCKED`.

### Agenci

| #  | Agent          | Model            | Rola                                                        |
|----|----------------|------------------|-------------------------------------------------------------|
| 00 | **Orchestrator** | Claude Opus 4.6  | Steruje workflow, deleguje zadania, nie pisze kodu         |
| 01 | **SpecAgent**    | Claude Opus 4.6  | Tworzy specyfikacje (`spec.md`, `acceptance.json`)         |
| 02 | **Architect**    | GPT-5.3-Codex    | Projektuje architekturę, tworzy ADR                        |
| 03 | **Planner**      | GPT-5.3-Codex    | Tworzy backlog zadań (`tasks.yaml`)                        |
| 04 | **Coder**        | Claude Opus 4.6  | Implementuje zadania                                       |
| 05 | **Reviewer**     | GPT-5.3-Codex    | Code review z checklistą + devil's advocate                |
| 06 | **QA**           | Gemini 3 Pro     | Testy, walidacja kryteriów akceptacji                      |
| 07 | **Security**     | GPT-5.3-Codex    | Audyt bezpieczeństwa (XSS, CSRF, SSRF, auth, secrets)     |
| 08 | **Integrator**   | GPT-5.3-Codex    | Integracja, green build, release                           |
| 09 | **Docs**         | Claude Haiku 4.5 | Dokumentacja, README, raport końcowy                       |
| 10 | **Designer**     | Gemini 3 Pro     | UX/UI design specs (wywoływany warunkowo)                  |

### Komunikacja przez artefakty

Agenci nie komunikują się przez czat — **źródłem prawdy są pliki w repozytorium**:

| Artefakt             | Format   | Opis                                      |
|----------------------|----------|--------------------------------------------|
| `spec.md`            | Markdown | Specyfikacja wymagań (PRD)                 |
| `acceptance.json`    | JSON     | Kryteria akceptacji                        |
| `architecture.md`    | Markdown | Architektura systemu                       |
| `tasks.yaml`         | YAML     | Backlog zadań z zależnościami              |
| `status.json`        | JSON     | Stan sesji, retry, decyzje użytkownika     |
| `report.md`          | Markdown | Raport końcowy                             |
| `adr/ADR-XXX.md`     | Markdown | Architecture Decision Records              |
| `design-specs/`      | Markdown | Specyfikacje UX/UI od Designera            |

Artefakty każdej sesji trafiają do `.agents-work/YYYY-MM-DD_<slug>/`.

### Bramki jakości (gates)

Workflow nie przechodzi dalej, jeśli:
- Brakuje wymaganych artefaktów (`spec.md`, `acceptance.json`, `tasks.yaml`)
- **Reviewer** blokuje (BLOCKED)
- **QA** blokuje (BLOCKED)
- **Security** blokuje (high severity)
- CI/build jest czerwony

Pętle naprawcze mają budżet **maks 3 prób** — po wyczerpaniu następuje eskalacja do użytkownika (`ASK_USER`).

## Pliki konfiguracyjne

```
.github/
└── agents/
    ├── 00-orchestrator.md    # Definicja roli Orchestratora
    ├── 01-spec-agent.md      # Definicja roli SpecAgenta
    ├── 02-architect.md       # Definicja roli Architekta
    ├── 03-planner.md         # Definicja roli Plannera
    ├── 04-coder.md           # Definicja roli Codera
    ├── 05-reviewer.md        # Definicja roli Reviewera
    ├── 06-qa.md              # Definicja roli QA
    ├── 07-security.md        # Definicja roli Security
    ├── 08-integrator.md      # Definicja roli Integratora
    ├── 09-docs.md            # Definicja roli Docs
    ├── 10-designer.md        # Definicja roli Designera
    ├── CONTRACT.md           # Globalny kontrakt I/O agentów
    └── WORKFLOW.md           # Maszyna stanów, reguły dispatch
```

## Projekty demo

### 🍅 FocusFlow (demo-pomidoro)

Aplikacja Pomodoro Timer z dziennikiem rozproszeń. Vanilla JS, zero zależności, statyczny hosting.

**Funkcje:** timer 25 min (Date.now-based), stany idle/running/paused/completed, dziennik rozproszeń z walidacją, liczniki dzienne, localStorage, import/export JSON, skróty klawiaturowe.

**Status:** ✅ DONE — w pełni zrealizowany przez pipeline agentów.

### 🚦 Traffic Simulator (demo-traffic-simulator)

Minimalna symulacja ruchu drogowego na skrzyżowaniu. Vanilla JS + Canvas API, zero zależności.

**Funkcje:** rendering mapy i pojazdów na canvas, logika hamowania, sygnalizacja świetlna, sterowanie parametrami (natężenie, prędkość, gęstość), statystyki live (aktywne pojazdy, średnia prędkość, przepustowość).

## Tech stack

- **Środowisko:** VS Code + GitHub Copilot Chat (custom agents / chat participants)
- **Multi-model:** Claude Opus 4.6, GPT-5.3-Codex, Gemini 3 Pro, Claude Haiku 4.5
- **Projekty demo:** Vanilla JS, zero frameworków, zero zależności, statyczny hosting
- **Quality gates:** `npm test`, `npm run lint`, `npm run build` + manualne checklists
- **Artefakty:** Markdown, JSON, YAML — wszystko wersjonowane w repo

## Jak to działa

1. Użytkownik opisuje cel w czacie z Orchestratorem
2. Orchestrator tworzy sesję w `.agents-work/` i deleguje do **SpecAgenta** (specyfikacja)
3. **Architect** projektuje architekturę, **Planner** dzieli na zadania
4. **Coder** implementuje zadanie po zadaniu
5. Po każdym zadaniu: **Reviewer** (code review) → **QA** (testy) → opcjonalnie **Security**
6. Pętle naprawcze (`FIX_*`) jeśli bramka blokuje, maks 3 próby
7. **Integrator** sprawdza green build, **Docs** generuje dokumentację
8. Orchestrator zamyka sesję ze statusem `DONE` i generuje `report.md`

