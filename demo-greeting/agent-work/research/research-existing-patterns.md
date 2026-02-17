# Research: Existing Demo Project Patterns

## Topic / Question
What patterns, conventions, and best practices are used in the existing demo projects (`demo-pomidoro`, `demo-traffic-simulator`) that should be followed by the new `demo-greeting` project?

## Context
The Orchestrator requested this research to inform the Architect and Coder working on a new `demo-greeting` project. The new project is a simple greeting card generator. Understanding how the existing demos are structured ensures consistency across the repository.

## Methodology
- Full read of all source files in `demo-pomidoro/` (HTML, CSS, JS, tests, scripts, package.json, architecture.md, spec.md)
- Full read of all source files in `demo-traffic-simulator/` (HTML, CSS, JS)
- Comparison of patterns, naming, architecture, and conventions

---

## Findings

### 1. Project Structure Conventions

#### demo-pomidoro (more complex, with build/test/lint)
```
demo-pomidoro/
  package.json
  spec.md, architecture.md, acceptance.json, status.json, tasks.yaml, report.md
  adr/
  public/
    index.html
    app.js
    timer.js
    storage.js
    ui.js
    styles.css
  scripts/
    build.mjs
    lint.mjs
  tests/
    timer.test.js
    storage.test.js
```

#### demo-traffic-simulator (simpler, no build/test tooling)
```
demo-traffic-simulator/
  index.html          ← root-level HTML
  README.md
  public/
    app.js
    controls.js
    metrics.js
    renderer-canvas.js
    simulation.js
    state.js
    storage.js
    styles.css
    traffic-model.js
    ui.js
```

**Key observations:**
- Both projects put JS and CSS in a `public/` directory.
- `demo-pomidoro` puts `index.html` inside `public/`, while `demo-traffic-simulator` puts it at the root. The traffic simulator references `./public/app.js` and `./public/styles.css` from the root HTML.
- `demo-pomidoro` has `package.json` with npm scripts (`test`, `lint`, `build`). `demo-traffic-simulator` has none.
- Agent artifacts (spec.md, architecture.md, etc.) live at the project root.

**Recommendation for demo-greeting:** Since it's a minimal 3-file project (index.html, app.js, styles.css), a flat `public/` directory with all files is the simplest approach. Given the spec states "3 files in a flat directory," the `demo-traffic-simulator` pattern (HTML at root, JS+CSS in public/) or a fully flat structure both work. The spec explicitly says no build tools, so no `package.json` is needed. However, if tests are required by QA, a minimal `package.json` can be added following `demo-pomidoro`'s pattern.

### 2. HTML Structure Patterns

#### Common patterns across both demos:
- `<!doctype html>` (lowercase)
- `<html lang="pl">` — Polish locale
- Standard meta tags: `<meta charset="UTF-8" />`, `<meta name="viewport" content="width=device-width, initial-scale=1.0" />`
- Self-closing void elements use ` />` (XHTML-style)
- CSS loaded via `<link rel="stylesheet">` in `<head>`
- JS loaded via `<script type="module">` at end of `<body>`
- Semantic structure: `<main>`, `<section>`, `<aside>` with `aria-labelledby` attributes
- Elements identified by `id` attributes for JS binding (e.g., `id="timer-display"`, `id="start-btn"`)
- Accessibility: `aria-live="polite"` on dynamic content, `aria-label` on interactive elements
- Labels associated with inputs

#### demo-pomidoro specific:
- Uses `.card` class for card-like sections
- Uses `<button type="button">` explicitly
- `<input>` elements have `maxlength`, `placeholder`, `aria-label`

#### demo-traffic-simulator specific:
- Uses `.panel` class for card-like sections
- Uses `<label for="...">` + `<input id="...">` association
- Uses `<output for="...">` for displaying slider values

**Recommendation for demo-greeting:** Follow common HTML patterns: `<!doctype html>`, `<html lang="pl">`, standard meta tags, semantic structure with `<main>` and `<section>`, `aria-labelledby` on sections, `<script type="module">`, `<button type="button">`, proper `<label>` elements.

### 3. CSS Patterns

#### demo-pomidoro (light theme):
- CSS custom properties on `:root` (only `color-scheme: light`)
- Universal `* { box-sizing: border-box; }`
- `body { margin: 0; }` reset
- Container with `max-width` + `margin: 0 auto` for centering
- `.card` class: white background, border, `border-radius: 8px`, padding, margin-bottom
- Buttons: explicit border, background, border-radius, padding, cursor
- `button:disabled` with opacity
- `.controls` uses `display: flex; flex-wrap: wrap; gap`
- `font: inherit` on form elements
- Error messages styled with specific color (#b91c1c)
- Animations via `@keyframes`
- No CSS framework, no utility classes

#### demo-traffic-simulator (dark theme):
- Heavy use of CSS custom properties: `--bg`, `--panel`, `--panel-border`, `--text`, `--muted`, `--accent`, `--good`, `--warn`
- Grid layout: `display: grid; grid-template-columns`
- `.panel` class: background, border, border-radius: 10px, padding
- `:focus-visible` styling for accessibility
- Responsive: `@media (max-width: 1023px)` breakpoint
- `system-ui, -apple-system, ...` font stack

**Common CSS conventions:**
- `* { box-sizing: border-box; }`
- `body { margin: 0; }` reset
- Card/panel class with background, border, border-radius, padding
- `font: inherit` on form controls
- Flexbox or Grid for layout
- No CSS frameworks or preprocessors
- Semantic class names (`.controls`, `.card`, `.panel`, `.status`)

**Recommendation for demo-greeting:** Use `:root` custom properties for colors, `* { box-sizing: border-box; }`, `body { margin: 0; }`, centered container, card styling with border-radius/shadow, and simple semantic class names. Light theme preferred (matches pomidoro). No framework/preprocessor.

### 4. JavaScript Patterns

#### Module system
- Both use ES Modules (`type="module"` in script tag, `import`/`export` in JS files)
- Named exports preferred (not default exports)
- `app.js` is the entry point that imports from other modules

#### Architecture pattern — Factory functions
- Both projects use **factory functions** (not classes) for creating instances:
  - `createTimer(config)` in pomidoro
  - `createUI(doc)` in pomidoro
  - `createUi(elements)` in traffic-simulator
  - `createState(settings)` in traffic-simulator
  - `createRenderer(canvas, lanes)` in traffic-simulator
  - `createSimulation({...})` in traffic-simulator
- Factory functions return plain objects with methods (closures over internal state)
- No `class` keyword used anywhere

#### State management
- **demo-pomidoro**: Immutable-ish style — functions return new/normalized state objects. `saveState()` returns normalized state. State passed explicitly to functions.
- **demo-traffic-simulator**: Mutable style — state object mutated directly (`state.world.paused = true`). Settings normalized via `normalizeSettings()`.

#### DOM access pattern
- Elements fetched by `document.getElementById()` once at initialization, cached in a plain object
- UI module encapsulates all DOM manipulation
- `textContent` used exclusively for rendering user data (never `innerHTML`)
- DOM elements created via `document.createElement()` + `appendChild()`
- Event listeners bound via `addEventListener()`

#### Security conventions
- No `innerHTML` with user data
- No `eval()`
- No `new Function()`
- Input sanitization: `trim()`, length limits, type checks
- `textContent` for safe text rendering
- Custom lint script checks for forbidden patterns

#### Naming conventions
- camelCase for variables and functions
- SCREAMING_SNAKE_CASE for constants (e.g., `STORAGE_KEY`, `DEFAULT_DURATION_MS`, `FIXED_DT_MS`)
- Descriptive function names: `handleStart`, `handlePause`, `renderTimer`, `updateMetrics`
- Files named in kebab-case or simple lowercase (e.g., `timer.js`, `storage.js`, `renderer-canvas.js`, `traffic-model.js`)
- `app.js` always the entry module

#### Error handling
- `try/catch` around localStorage operations
- Fallback to default state on parse errors
- Result objects with `{ ok, error?, state? }` pattern for operations that can fail (pomidoro)
- `null` returns for failed operations (traffic-simulator)

#### Input validation
- Validation before action (e.g., empty check before adding journal entry)
- `Number.isFinite()` for numeric validation
- String type checks before processing
- Clamping values to valid ranges (`Math.min`, `Math.max`)

### 5. Testing Approach (demo-pomidoro only)

- **Test runner**: Node.js built-in `node:test` module (no external test framework)
- **Assertion library**: `node:assert/strict`
- **Test file naming**: `<module>.test.js` in `tests/` directory
- **Test style**: Each test is a top-level `test()` call with descriptive Polish-language name
- **Strategy**: Unit tests for pure logic modules (`timer.js`, `storage.js`), no UI tests
- **Dependency injection**: Timer accepts `now` parameter to control time; Storage accepts `storage` parameter for mock localStorage
- **Memory storage mock**: `createMemoryStorage()` utility exported from `storage.js` for testing without real localStorage
- **Test runner command**: `node --test` (configured in `package.json` as `npm test`)

**Key testability patterns:**
- Pure functions with injectable dependencies (time, storage)
- Factory functions that accept config objects
- No global mutable state in logic modules
- Exported utility functions for test support (e.g., `createMemoryStorage`)

**Recommendation for demo-greeting:** The spec says no build tools/npm, so tests may not be needed. If QA requires tests, follow the `node:test` + `node:assert/strict` pattern with test files in `tests/`.

### 6. Build & Lint (demo-pomidoro only)

- **Build script** (`scripts/build.mjs`): Verifies required files exist, copies `public/` to `dist/`
- **Lint script** (`scripts/lint.mjs`): Custom scanner checking for forbidden patterns (`innerHTML=`, `eval(`, `new Function(`)
- **No external dependencies**: No node_modules, no eslint, no prettier
- **package.json**: Minimal, `"type": "module"`, only 3 scripts

**Recommendation for demo-greeting:** Not needed per spec (no build tools). If added later, follow the same pattern.

### 7. Localization

- Both demos use Polish language for UI text (button labels, status messages, headings)
- `<html lang="pl">`
- Test descriptions also in Polish

**Recommendation for demo-greeting:** Use `<html lang="pl">` and Polish labels. However, the spec requires greeting text in English ("Hello, {name}!"), so the greeting output is English while UI chrome can be Polish.

---

## Options / Alternatives

### OPT-1: Flat structure (all 3 files in one directory)
- **Pros**: Matches spec exactly ("3 files in a flat directory"), simplest possible structure, opens via file:// immediately
- **Cons**: Doesn't follow existing `public/` convention, no room for tests/scripts
- **Effort**: Low
- **Recommended**: Yes — for the initial scope

### OPT-2: Root HTML + public/ for JS/CSS (traffic-simulator pattern)
- **Pros**: Follows traffic-simulator convention, separates concerns
- **Cons**: Slightly more complex than spec requires, 2 directories instead of 1
- **Effort**: Low
- **Recommended**: Acceptable alternative

### OPT-3: Everything in public/ (pomidoro pattern)
- **Pros**: Follows pomidoro convention, allows adding package.json/tests/scripts at root
- **Cons**: Spec says flat directory; user must navigate to public/ to open index.html
- **Effort**: Low
- **Recommended**: Only if tests/build are added

---

## Recommendation

Follow **OPT-1** (flat structure) for the deliverable files, placing `index.html`, `app.js`, and `styles.css` directly inside `demo-greeting/`. This matches the spec requirement and keeps the project as simple as possible.

Apply the following conventions from existing demos:
1. **HTML**: `<!doctype html>`, `<html lang="pl">`, standard meta tags, semantic elements, `aria` attributes, `<script type="module">`, `<button type="button">`
2. **CSS**: `:root` variables, `box-sizing: border-box`, `body { margin: 0 }`, card styling with border-radius, no frameworks
3. **JS**: ES Modules, factory functions (if needed), `getElementById` for DOM access, `textContent` only (no `innerHTML`), camelCase naming, `SCREAMING_SNAKE_CASE` for constants
4. **Security**: No `innerHTML`, no `eval()`, `textContent` for user input, `trim()` + validation before action
5. **Accessibility**: `<label>` elements for inputs, keyboard-accessible buttons, `aria-live` for dynamic content

**Confidence**: High — all findings are based on direct source code analysis of the existing demos.

---

## Sources / References

All findings are from direct analysis of repository source files:
- `demo-pomidoro/public/index.html`, `app.js`, `timer.js`, `storage.js`, `ui.js`, `styles.css`
- `demo-pomidoro/tests/timer.test.js`, `tests/storage.test.js`
- `demo-pomidoro/scripts/build.mjs`, `scripts/lint.mjs`
- `demo-pomidoro/package.json`, `architecture.md`, `spec.md`
- `demo-traffic-simulator/index.html`
- `demo-traffic-simulator/public/app.js`, `state.js`, `ui.js`, `controls.js`, `storage.js`, `simulation.js`, `metrics.js`, `traffic-model.js`, `renderer-canvas.js`, `styles.css`

## Open Questions

1. **File placement**: Should `demo-greeting` files go in root or in `public/`? Spec says flat; recommend root for simplicity.
2. **Tests**: Spec says no build tools, but QA may require tests. If so, add a minimal `package.json` and `tests/` directory following pomidoro patterns.
3. **Language of UI chrome**: Spec example uses English greeting but existing demos use Polish UI. Suggest Polish labels + English greeting text per spec.
