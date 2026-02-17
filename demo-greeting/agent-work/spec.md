# Greeting Card Generator — Specification

## Problem Statement

Users want a quick, zero-install way to generate a simple styled greeting card in their browser. They type a name, pick a background color from three presets, click "Generate", and instantly see a styled card saying "Hello, {name}!". No server, no build tools, no frameworks — just open `index.html` and go.

## Goals

- Provide a single-page web application that generates a greeting card.
- Allow the user to enter their name via a text input.
- Offer exactly 3 preset background colors for the card.
- On clicking "Generate", display a styled greeting card with the text "Hello, {name}!" on the selected background.
- Work entirely offline — no network requests, no backend, no API.
- Deliverable is 3 files: `index.html`, `app.js`, `styles.css`, openable directly in any modern browser.

## Non-Goals

- No backend / server-side logic.
- No JavaScript frameworks or libraries (React, Vue, jQuery, etc.).
- No build tools (Webpack, Vite, npm, etc.).
- No data persistence or storage (localStorage, cookies, database).
- No deployment pipeline or hosting.
- No image export or download feature.
- No user authentication.

## User Stories

1. **US-01** — As a user, I can see a clean landing page with a name input, 3 color options, and a "Generate" button.
2. **US-02** — As a user, I can type my name into the text input field.
3. **US-03** — As a user, I can select one of three preset background colors for my greeting card.
4. **US-04** — As a user, I can click "Generate" and see a styled greeting card appear on the page.
5. **US-05** — As a user, the greeting card displays "Hello, {name}!" where {name} is replaced with what I typed.
6. **US-06** — As a user, the greeting card has the background color I selected.
7. **US-07** — As a user, if I change inputs and click "Generate" again, the card updates.
8. **US-08** — As a user, I can use this app by simply opening `index.html` in my browser — no install steps.

## Functional Requirements

### FR-01: Name Input
- A single text input field labeled "Your Name" (or equivalent).
- Accepts any text. No maximum length enforced in the UI (browser default applies).

### FR-02: Color Selection
- Exactly 3 preset background colors are presented as selectable options (e.g., radio buttons, clickable swatches, or a `<select>`).
- Suggested presets: Coral (`#FF6B6B`), Sky Blue (`#4ECDC4`), Sunshine Yellow (`#FFE66D`). Architect/Coder may adjust exact values.
- One color must be pre-selected by default so the user can generate immediately after typing a name.

### FR-03: Generate Button
- A button labeled "Generate" (or equivalent clear CTA).
- Clicking it creates / updates the greeting card in a visible area of the page.

### FR-04: Greeting Card Display
- The card is a styled `<div>` (or similar block element) rendered below or beside the form.
- Card content: the text "Hello, {name}!" centered on the card.
- Card background: the selected preset color.
- Card has readable text color that contrasts with the background.
- Card has visual styling (padding, border-radius, shadow, or similar) to look like a card.

### FR-05: Re-generation
- The user can change name and/or color and click "Generate" again.
- The card updates in place (no duplicate cards).

## Non-Functional Requirements

### Performance
- Page loads instantly (no external resources, no build step).
- Card generation is synchronous DOM manipulation — no perceptible delay.

### Usability
- The interface is self-explanatory; no instructions beyond labels are needed.
- Works on desktop browsers (Chrome, Firefox, Edge, Safari latest).
- Responsive layout is a nice-to-have but not required.

### Accessibility
- Inputs have associated `<label>` elements.
- The Generate button is keyboard-accessible (default `<button>` behavior).
- Card text has sufficient contrast against all 3 preset backgrounds.

### Security
- No user data is transmitted anywhere — the app is fully client-side.
- No `eval()`, no `innerHTML` with unsanitized user input (use `textContent`).

## Edge Cases

1. **Empty name** — User clicks "Generate" without typing a name. Expected: show "Hello, !" or show a validation message prompting the user to enter a name. Recommended: show a brief inline validation message and do not generate the card.
2. **Whitespace-only name** — User enters only spaces. Treat the same as empty name.
3. **Very long name** — User enters an extremely long string. The card should not break layout; text may wrap or truncate gracefully.
4. **Special characters in name** — User enters `<script>alert(1)</script>`. Must not execute; use `textContent` to render.
5. **No color selected** — Should not happen if a default is pre-selected, but if somehow no color is selected, treat as first preset.
6. **Rapid repeated clicks** — User clicks "Generate" many times quickly. Card should simply update each time; no duplicate cards, no errors.
7. **Browser back/forward** — No SPA routing; back/forward behaves as browser default. No special handling needed.
8. **JavaScript disabled** — The page will not function. No specific fallback required, but a `<noscript>` message is a nice-to-have.

## Assumptions

1. The target audience uses a modern desktop browser (ES6+ support assumed).
2. The 3 preset colors will be defined at build time (hardcoded), not configurable by the user beyond selection.
3. The greeting text format is exactly `Hello, {name}!` — no other templates or customization.
4. The app consists of exactly 3 files in a flat directory: `index.html`, `app.js`, `styles.css`.
5. No accessibility audit (WCAG AA) is formally required, but basic accessibility best practices are followed.

## Definition of Done

- [ ] `index.html`, `app.js`, and `styles.css` exist in the project directory.
- [ ] Opening `index.html` in a modern browser shows the input form (name field, 3 color options, Generate button).
- [ ] Typing a name, selecting a color, and clicking Generate displays a styled card with "Hello, {name}!" on the chosen background.
- [ ] Re-generating with different inputs updates the card in place.
- [ ] Empty/whitespace name is handled gracefully (validation message or safe fallback).
- [ ] Special characters in name are rendered safely (no XSS).
- [ ] No external dependencies, no build step, no server required.
- [ ] All acceptance criteria in `acceptance.json` pass.

## Acceptance Criteria

See `acceptance.json` for the machine-readable list. Summary:

| ID     | Description                                                    |
|--------|----------------------------------------------------------------|
| AC-001 | Page loads with name input, 3 color options, Generate button   |
| AC-002 | Typing a name and clicking Generate shows greeting card        |
| AC-003 | Card text is "Hello, {name}!" with the entered name            |
| AC-004 | Card background matches selected color                         |
| AC-005 | Changing inputs and re-generating updates the card in place    |
| AC-006 | Empty name shows validation / does not produce broken card     |
| AC-007 | Special characters are rendered safely (no XSS)                |
| AC-008 | App works by opening index.html directly (no server needed)    |
