# Greeting Card Generator

A minimal, zero-install web application that generates styled greeting cards in the browser. Type a name, pick one of three preset background colors, click "Generuj" — and instantly see a card saying **"Hello, {name}!"**. No server, no build tools, no frameworks — just open `index.html` and go.

## Features

- **Instant card generation** — type a name, pick a color, click the button
- **3 preset background colors** — Coral (`#FF6B6B`), Sky Blue (`#4ECDC4`), Sunshine (`#FFE66D`)
- **In-place updates** — change inputs and re-generate without duplicating cards
- **Input validation** — empty or whitespace-only names show a friendly error message
- **XSS-safe** — all user input rendered via `textContent`, never `innerHTML`
- **Accessible** — proper `<label>` elements, `fieldset`/`legend`, `aria-live`, `role="alert"`, keyboard navigable
- **Fully offline** — no network requests, no backend, works via `file://` protocol
- **Zero dependencies** — no npm, no frameworks, no build step

## Requirements

- A modern web browser (Chrome, Firefox, Edge, Safari — latest versions)
- JavaScript enabled

No Node.js, npm, or any other tooling is required to **run** the app.

To run **tests**, you need:

- [Node.js](https://nodejs.org/) v18+ (uses built-in `node:test` runner)

## Quickstart

1. Clone or download this repository.
2. Open `demo-greeting/index.html` in your browser (double-click the file or use `File → Open`).
3. Type a name in the "Twoje imię" input field.
4. Select a background color (Coral, Sky Blue, or Sunshine).
5. Click **Generuj**.
6. Your greeting card appears below the form!

```
demo-greeting/index.html   ← just open this file
```

## Scripts

### Run tests

```bash
node --test demo-greeting/tests/app.test.js
```

Tests use the built-in Node.js test runner (`node:test`) and assertion module (`node:assert/strict`). No installation required.

### What is tested

| Suite            | Coverage                                                         |
|------------------|------------------------------------------------------------------|
| `validateName`   | Valid input, trimming, empty string, whitespace, null, undefined, XSS, long names, unicode |
| `greetingText`   | Normal names, special characters, empty string, unicode          |
| `COLOR_PRESETS`  | Length, structure, expected values for all 3 presets              |

## Project structure

```
demo-greeting/
├── index.html          # Entry point — HTML structure, loads CSS & JS
├── app.js              # Application logic (ES Module)
│                       #   Exports: COLOR_PRESETS, validateName, greetingText, initApp
├── styles.css          # All visual styles, CSS custom properties, card styling
├── README.md           # This file
└── tests/
    └── app.test.js     # Unit tests (node:test + node:assert/strict)
```

### File responsibilities

| File          | Role                                                                 |
|---------------|----------------------------------------------------------------------|
| `index.html`  | Semantic HTML structure with accessibility attributes, loads CSS & JS |
| `app.js`      | Pure functions (`validateName`, `greetingText`) + `initApp()` for DOM binding |
| `styles.css`  | Design tokens via CSS custom properties, layout, form card, color swatches, greeting card, sr-only, focus-visible |
| `tests/app.test.js` | 17 unit tests covering pure functions and COLOR_PRESETS constant |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Card does not appear after clicking "Generuj" | Make sure JavaScript is enabled in your browser |
| Page shows "Ta aplikacja wymaga włączonego JavaScript" | Enable JavaScript in browser settings |
| Tests fail with `SyntaxError` | Ensure you are using Node.js v18+ (ES Module + `node:test` support required) |
| Colors look different | Check that your browser/OS does not apply a forced color mode or high-contrast theme |
| File won't open from network drive | Copy files to a local directory and open from there |

## License

This project is part of the `coordinated-agent-team` demo suite. See the repository root for license information.
