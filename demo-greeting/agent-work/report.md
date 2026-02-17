# Session Report — Greeting Card Generator

**Session:** `2026-02-17_demo-greeting`
**Date:** 2026-02-17
**Project type:** web (client-side only)

## Summary

The Greeting Card Generator is a minimal, zero-install browser app that lets users type a name, pick a background color (Coral, Sky Blue, Sunshine), and instantly generate a styled greeting card reading "Hello, {name}!". The project was implemented as 3 flat files (`index.html`, `app.js`, `styles.css`) in `demo-greeting/`, with unit tests in `tests/app.test.js`.

## What was done

### Artifacts produced

| File | Purpose |
|------|---------|
| `demo-greeting/index.html` | Semantic HTML structure with accessibility (aria-live, role=alert, fieldset/legend, labels, noscript) |
| `demo-greeting/styles.css` | Full visual design — CSS custom properties, form card, circular color swatches, greeting card, sr-only, focus-visible |
| `demo-greeting/app.js` | ES Module with pure functions (`validateName`, `greetingText`) and `initApp()` DOM binding |
| `demo-greeting/tests/app.test.js` | 17 unit tests using `node:test` + `node:assert/strict` |
| `demo-greeting/README.md` | Quickstart, features, requirements, scripts, project structure, troubleshooting |
| `.agents-work/2026-02-17_demo-greeting/spec.md` | Full specification with goals, user stories, functional/non-functional requirements, edge cases |
| `.agents-work/2026-02-17_demo-greeting/acceptance.json` | 8 acceptance criteria (AC-001 through AC-008) |
| `.agents-work/2026-02-17_demo-greeting/architecture.md` | Architecture doc — modules, data flow, interfaces, error handling, security |
| `.agents-work/2026-02-17_demo-greeting/tasks.yaml` | Task breakdown (T-001: HTML+CSS, T-002: JS logic) — both completed |
| `.agents-work/2026-02-17_demo-greeting/report.md` | This file |

### Tasks completed

| Task | Title | Status |
|------|-------|--------|
| T-001 | Create HTML structure and CSS styling | completed |
| T-002 | Implement greeting card JavaScript logic | completed |
| meta | Create README and final report | completed |

## How to run

1. Open `demo-greeting/index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
2. No server, no build step, no npm install required — works via `file://` protocol.

## How to test

```bash
node --test demo-greeting/tests/app.test.js
```

Requires Node.js v18+ (uses built-in `node:test` runner). No dependencies to install.

### Test coverage

- `validateName` — 9 tests (valid input, trimming, empty, whitespace, null, undefined, XSS, long names, unicode)
- `greetingText` — 5 tests (normal names, XSS, empty, unicode)
- `COLOR_PRESETS` — 3 tests (length, structure, preset values)

## Acceptance criteria status

| ID | Description | Status |
|----|-------------|--------|
| AC-001 | Page loads with name input, 3 color options, Generate button | PASS |
| AC-002 | Typing name + clicking Generate shows greeting card | PASS |
| AC-003 | Card text is "Hello, {name}!" | PASS |
| AC-004 | Card background matches selected color | PASS |
| AC-005 | Re-generating updates card in place | PASS |
| AC-006 | Empty name shows validation message | PASS |
| AC-007 | Special characters rendered safely (no XSS) | PASS |
| AC-008 | Works via file:// protocol, no server needed | PASS |

## Definition of Done

- [x] `index.html`, `app.js`, `styles.css` exist in `demo-greeting/`
- [x] Opening `index.html` shows the input form (name field, 3 color options, Generate button)
- [x] Typing a name, selecting a color, clicking Generate displays styled card
- [x] Re-generating with different inputs updates card in place
- [x] Empty/whitespace name handled with validation message
- [x] Special characters rendered safely (textContent, no innerHTML)
- [x] No external dependencies, no build step, no server required
- [x] All acceptance criteria pass
- [x] Unit tests pass
- [x] README.md created

## Known issues

None.

## Architecture decisions

- **Flat file structure** (no `public/` subfolder) — spec requires exactly 3 files in one directory
- **ES Modules** — `app.js` loaded as `<script type="module">` for testability and clean exports
- **Pure functions** — `validateName` and `greetingText` extracted for unit testing without DOM
- **No innerHTML** — all user input rendered via `textContent` to prevent XSS
- **Polish UI labels** — consistent with repository convention (`Twoje imię`, `Wybierz kolor`, `Generuj`)
- **CSS custom properties** — design tokens for maintainability
