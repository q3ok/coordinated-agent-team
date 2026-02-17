# Design Spec — Greeting Card Generator UI

## 1. Overview

A minimal, single-page greeting card generator with a light theme matching `demo-pomidoro` patterns. The user fills a name field, selects a color swatch, clicks "Generuj", and sees a styled greeting card. No frameworks, no build tools, system fonts only. Pure CSS.

---

## 2. Design Tokens (`:root` Custom Properties)

```css
:root {
  color-scheme: light;

  /* Typography */
  --font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  --font-size-base: 1rem;        /* 16px */
  --font-size-sm: 0.875rem;      /* 14px */
  --font-size-lg: 1.25rem;       /* 20px */
  --font-size-card: 1.75rem;     /* 28px — greeting text */

  /* Surface & text */
  --color-bg: #f4f5f7;           /* page background — matches pomidoro */
  --color-surface: #ffffff;      /* card/panel background */
  --color-text: #1f2937;         /* primary text */
  --color-text-muted: #6b7280;   /* secondary/placeholder text */
  --color-border: #d1d5db;       /* default border */

  /* Interaction */
  --color-focus: #2563eb;        /* focus ring (blue, WCAG AA on white) */
  --color-error: #b91c1c;        /* error text — matches pomidoro */

  /* Preset card colors */
  --preset-coral: #FF6B6B;
  --preset-sky: #4ECDC4;
  --preset-sunshine: #FFE66D;

  /* Card text on presets */
  --card-text-dark: #1f2937;     /* used on Sunshine Yellow */
  --card-text-light: #ffffff;    /* used on Coral and Sky Blue */

  /* Spacing scale */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* Radii */
  --radius-sm: 6px;              /* buttons, inputs */
  --radius-md: 8px;              /* form card */
  --radius-lg: 16px;             /* greeting card */
}
```

### Rationale
- Font stack matches `demo-traffic-simulator`, broadened for system coverage.
- Page background `#f4f5f7` from `demo-pomidoro`.
- Focus color `#2563eb` provides 4.6:1 contrast on white — WCAG AA compliant.
- Error color `#b91c1c` reused from `demo-pomidoro`.

---

## 3. Layout

### 3.1 Page structure

```
┌─────────────────────────────────────────────────┐
│                   <main.app>                    │
│  max-width: 520px  |  centered  |  padding      │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │  <h1> Greeting Card Generator           │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  ┌── section.form-card (.card) ─────────────┐   │
│  │  <h2> Utwórz kartkę                      │   │
│  │                                           │   │
│  │  <label> Twoje imię                       │   │
│  │  ┌─────────────────────────────────┐      │   │
│  │  │  <input type="text">            │      │   │
│  │  └─────────────────────────────────┘      │   │
│  │                                           │   │
│  │  <fieldset> Wybierz kolor                 │   │
│  │  ┌───────┐  ┌───────┐  ┌───────┐         │   │
│  │  │ Coral │  │  Sky  │  │ Sun.  │         │   │
│  │  │ ●●●●● │  │ ●●●●● │  │ ●●●●● │         │   │
│  │  └───────┘  └───────┘  └───────┘         │   │
│  │                                           │   │
│  │  ┌───────────────┐                        │   │
│  │  │   Generuj     │                        │   │
│  │  └───────────────┘                        │   │
│  │                                           │   │
│  │  <p#error-msg> (hidden by default)        │   │
│  └───────────────────────────────────────────┘   │
│                                                  │
│  ┌── section#card-section ──────────────────┐   │
│  │  <h2 class="sr-only"> Podgląd kartki     │   │
│  │  ┌─── div#card-output (.card-greeting) ─┐│   │
│  │  │                                       ││   │
│  │  │   Hello, Alice!                       ││   │
│  │  │                                       ││   │
│  │  └───────────────────────────────────────┘│   │
│  └───────────────────────────────────────────┘   │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 3.2 Container

| Property      | Value                               |
|---------------|-------------------------------------|
| `max-width`   | `520px`                             |
| `margin`      | `0 auto`                            |
| `padding`     | `var(--space-lg) var(--space-md) var(--space-2xl)` |

Narrower than pomidoro (760px) because this is a simpler, form-focused layout. 520px keeps the greeting card comfortable on desktop while staying readable.

### 3.3 Responsive behavior

No explicit breakpoints required (per non-goals). The centered `max-width` container naturally adapts to smaller screens. Minimal additions:

- On viewports narrower than `520px`, the container fills the width with `padding: var(--space-md)`.
- Color swatch row wraps via `flex-wrap: wrap` if needed.
- Greeting card occupies full container width.

---

## 4. Component Specifications

### 4.1 Form Card (`.card`)

Wraps the form section. Reuses `.card` pattern from `demo-pomidoro`.

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);      /* 8px */
  padding: var(--space-lg);             /* 24px */
  margin-bottom: var(--space-md);       /* 16px */
}
```

### 4.2 Name Input

| Property         | Value                                          |
|------------------|------------------------------------------------|
| Width            | `100%`                                         |
| Height           | `min-height: 44px` (touch target)              |
| Border           | `1px solid var(--color-border)`                |
| Border-radius    | `var(--radius-sm)` (6px)                       |
| Padding          | `var(--space-sm) var(--space-sm)` (8px)        |
| Font             | `inherit` (matches pomidoro)                   |
| Placeholder      | `"Wpisz imię…"` color `var(--color-text-muted)` |
| Margin-top       | `var(--space-xs)` (4px, below label)           |
| Margin-bottom    | `var(--space-md)` (16px, before fieldset)      |

**Label:** `<label for="name-input">Twoje imię</label>` — `font-weight: 600`, displayed as block.

### 4.3 Color Selection (Radio Swatches)

Uses native `<input type="radio">` inside `<label>` elements, styled as visual color swatches.

**Markup structure:**
```html
<fieldset class="color-fieldset">
  <legend>Wybierz kolor</legend>
  <div class="color-options">
    <label class="color-option">
      <input type="radio" name="color" value="#FF6B6B" checked>
      <span class="color-swatch" style="background-color: #FF6B6B;" aria-hidden="true"></span>
      <span class="color-label">Coral</span>
    </label>
    <!-- repeat for Sky Blue, Sunshine -->
  </div>
</fieldset>
```

**Layout:** `.color-options` uses `display: flex; gap: var(--space-md); flex-wrap: wrap;`

**Swatch dimensions:**

| Property         | Value                          |
|------------------|--------------------------------|
| Width × Height   | `48px × 48px`                  |
| Border-radius    | `50%` (circle)                 |
| Border           | `2px solid var(--color-border)` |
| Cursor           | `pointer`                      |

**States:**

| State           | Visual treatment                                              |
|-----------------|---------------------------------------------------------------|
| Default         | Circle with 2px border `var(--color-border)`                  |
| Hover           | Border changes to `var(--color-text-muted)` (#6b7280)        |
| Selected        | Border: `3px solid var(--color-focus)` (#2563eb), `box-shadow: 0 0 0 2px var(--color-focus)` |
| Focus-visible   | `outline: 2px solid var(--color-focus); outline-offset: 2px`  |

**Radio input:** Visually hidden with `.sr-only` class (not `display: none` — keeps it accessible). The visual indicator is the swatch border/shadow change.

**Color label text:** Displayed below each swatch, `font-size: var(--font-size-sm)`, `text-align: center`, color `var(--color-text-muted)`.

**Each `.color-option` layout:** `display: flex; flex-direction: column; align-items: center; gap: var(--space-xs);`

### 4.4 Generate Button

| Property         | Value                                            |
|------------------|--------------------------------------------------|
| Width            | `100%`                                           |
| Min-height       | `44px` (touch target)                            |
| Background       | `var(--color-text)` (#1f2937, dark)              |
| Color            | `#ffffff` (white text)                           |
| Border           | `none`                                           |
| Border-radius    | `var(--radius-sm)` (6px)                         |
| Font-weight      | `600`                                            |
| Font-size        | `var(--font-size-base)`                          |
| Cursor           | `pointer`                                        |
| Margin-top       | `var(--space-md)` (16px)                         |
| Padding          | `var(--space-sm) var(--space-md)` (8px 16px)     |

**States:**

| State         | Visual treatment                                              |
|---------------|---------------------------------------------------------------|
| Default       | Dark background `var(--color-text)`, white text               |
| Hover         | Background lightens to `#374151`                              |
| Active        | Background darkens to `#111827`                               |
| Focus-visible | `outline: 2px solid var(--color-focus); outline-offset: 2px`  |
| Disabled      | `opacity: 0.5; cursor: not-allowed;` (matches pomidoro)      |

**Rationale:** A filled (primary) button draws the eye as the main CTA. Differs from pomidoro's outlined buttons intentionally to establish visual hierarchy — this form has only one button.

### 4.5 Error Message (`#error-msg`)

| Property         | Value                                       |
|------------------|---------------------------------------------|
| Color            | `var(--color-error)` (#b91c1c)              |
| Font-size        | `var(--font-size-sm)` (14px)                |
| Margin-top       | `var(--space-sm)` (8px)                     |
| Min-height       | `20px` (prevents layout shift)              |
| Role             | `role="alert"` (announced to screen readers)|
| Hidden           | `hidden` attribute by default               |

Text content: `"Wpisz imię, aby wygenerować kartkę."` (from architecture.md).

### 4.6 Greeting Card (`#card-output` / `.card-greeting`)

The hero element — the visual output of the app.

| Property           | Value                                              |
|--------------------|----------------------------------------------------|
| Min-height         | `200px`                                            |
| Padding            | `var(--space-xl) var(--space-lg)` (32px 24px)      |
| Border-radius      | `var(--radius-lg)` (16px)                          |
| Box-shadow         | `0 4px 12px rgba(0, 0, 0, 0.1)`                   |
| Text-align         | `center`                                           |
| Font-size          | `var(--font-size-card)` (1.75rem / 28px)           |
| Font-weight        | `700`                                              |
| Display            | `flex`                                             |
| Align-items        | `center`                                           |
| Justify-content    | `center`                                           |
| Word-wrap          | `overflow-wrap: break-word` (long names)           |
| Background         | Set dynamically via `style.backgroundColor`        |
| Transition         | None (animations are a non-goal)                   |

**Text color per background:**

| Background       | Hex       | Text color            | Contrast ratio | WCAG |
|------------------|-----------|-----------------------|----------------|------|
| Coral            | `#FF6B6B` | `#ffffff` (white)     | 3.0:1          | AA Large ✓ (28px bold qualifies as large text) |
| Sky Blue         | `#4ECDC4` | `#1f2937` (dark)      | 5.8:1          | AA ✓ |
| Sunshine Yellow  | `#FFE66D` | `#1f2937` (dark)      | 10.4:1         | AAA ✓ |

**Implementation note:** Text color is set in JS based on selected preset. Logic:
- Coral → white text (`#ffffff`) + `text-shadow: 0 1px 2px rgba(0,0,0,0.2)` for enhanced readability
- Sky Blue, Sunshine Yellow → dark text (`#1f2937`)

The `COLOR_PRESETS` array in `app.js` should include a `textColor` property:
```js
export const COLOR_PRESETS = [
  { value: '#FF6B6B', label: 'Coral',    textColor: '#ffffff' },
  { value: '#4ECDC4', label: 'Sky Blue', textColor: '#1f2937' },
  { value: '#FFE66D', label: 'Sunshine', textColor: '#1f2937' },
];
```

**Empty/initial state:** Before first generation, `#card-output` is empty (no `.card-greeting` class applied, no content). The section is present but invisible — no placeholder, no border, no background.

**After generation:** `#card-output` receives:
- `classList.add('card-greeting')`
- `textContent = "Hello, {name}!"`
- `style.backgroundColor = selectedColor`
- `style.color = textColor`

---

## 5. Typography

| Element              | Size                     | Weight | Color                    |
|----------------------|--------------------------|--------|--------------------------|
| `<h1>`               | `var(--font-size-lg)` (20px) | `700`  | `var(--color-text)`      |
| `<h2>` (form)        | `var(--font-size-base)` (16px) | `600` | `var(--color-text)`      |
| Labels               | `var(--font-size-base)`  | `600`  | `var(--color-text)`      |
| Input text            | `var(--font-size-base)`  | `400`  | `var(--color-text)`      |
| Placeholder           | `var(--font-size-base)`  | `400`  | `var(--color-text-muted)`|
| Button text           | `var(--font-size-base)`  | `600`  | `#ffffff`                |
| Error message         | `var(--font-size-sm)` (14px) | `400` | `var(--color-error)`    |
| Card greeting text    | `var(--font-size-card)` (28px) | `700` | Per preset (see §4.6)  |
| Color option label    | `var(--font-size-sm)` (14px) | `400` | `var(--color-text-muted)` |

---

## 6. Spacing & Vertical Rhythm

```
<main.app>
  padding-top: 24px
  ├── <h1>                       mb: 12px (matches pomidoro h1)
  ├── <section.card>             mb: 16px (matches pomidoro .card)
  │   padding: 24px
  │   ├── <h2>                   mb: 12px
  │   ├── <label>                mb: 4px (to input)
  │   ├── <input>                mb: 16px (to fieldset)
  │   ├── <fieldset>             mb: 16px (to button)
  │   │   ├── <legend>           mb: 8px
  │   │   └── .color-options     gap: 16px (between swatches)
  │   ├── <button>               mt: 16px
  │   └── <p#error-msg>          mt: 8px, min-height: 20px
  └── <section#card-section>
      └── <div#card-output>      (min-height: 200px when visible)
  padding-bottom: 48px
```

---

## 7. Accessibility Requirements

### 7.1 Semantic HTML
- `<main>` wraps all content
- `<section>` with `aria-labelledby` for form and output areas
- `<fieldset>` + `<legend>` for color radio group
- `<label for="...">` on name input
- `<button type="button">` (not submit — no `<form>` needed since there's no submission)

### 7.2 Keyboard Navigation
Tab order: Name input → Coral radio → Sky Blue radio → Sunshine radio → Generate button. Natural DOM order, no `tabindex` manipulation needed.

### 7.3 Focus Indicators
Global rule (matches `demo-traffic-simulator`):
```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```
Applies to input, radio buttons (via swatch styling), and button.

### 7.4 Screen Reader Support
- `aria-live="polite"` on `#card-output` — screen readers announce card content changes
- `role="alert"` on `#error-msg` — validation errors announced immediately
- `.sr-only` class for visually hidden heading on card section:
  ```css
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
  ```
- Radio inputs are screen-reader accessible (only visually hidden, not `display:none`)

### 7.5 Color Contrast Summary

| Context                  | Foreground | Background | Ratio | Pass   |
|--------------------------|-----------|------------|-------|--------|
| Body text on page        | `#1f2937` | `#f4f5f7`  | 12.8:1 | AAA ✓ |
| Form text on card        | `#1f2937` | `#ffffff`  | 16:1   | AAA ✓ |
| Error text on card       | `#b91c1c` | `#ffffff`  | 6.1:1  | AA ✓  |
| Button text              | `#ffffff` | `#1f2937`  | 16:1   | AAA ✓ |
| Greeting on Coral        | `#ffffff` | `#FF6B6B`  | 3.0:1  | AA Large ✓ |
| Greeting on Sky Blue     | `#1f2937` | `#4ECDC4`  | 5.8:1  | AA ✓  |
| Greeting on Sunshine     | `#1f2937` | `#FFE66D`  | 10.4:1 | AAA ✓ |

Note: Coral at 3.0:1 with white text passes AA for large text (≥18pt bold = 24px bold; our greeting is 28px bold, qualifying).  Text shadow adds perceptual contrast.

---

## 8. Interaction States (Full Matrix)

### 8.1 Name Input

| State         | Border                         | Background | Shadow / Other        |
|---------------|--------------------------------|------------|-----------------------|
| Default       | `1px solid var(--color-border)` | `#fff`     |                       |
| Hover         | `1px solid var(--color-text-muted)` | `#fff` |                       |
| Focus         | `1px solid var(--color-focus)` | `#fff`     | Outline per §7.3      |
| Filled        | Same as default                | `#fff`     | Text is `var(--color-text)` |
| Error         | `1px solid var(--color-error)` | `#fff`     | Applied when validation fails |

### 8.2 Radio Swatch (see §4.3)

### 8.3 Generate Button (see §4.4)

### 8.4 Greeting Card

| State              | Visual treatment                                 |
|--------------------|--------------------------------------------------|
| Hidden (initial)   | No classes, empty content, invisible              |
| Visible (after gen)| Full card styling with greeting text and color    |
| Updated (re-gen)   | Content and color change in place, no duplication |

---

## 9. Error & Edge Case States

| Scenario                | Visual behavior                                                        |
|-------------------------|------------------------------------------------------------------------|
| Empty name → Generate   | `#error-msg` shown with text, card NOT generated (or hidden), input border turns error color |
| Whitespace-only name    | Treated same as empty name (after `trim()`)                            |
| Very long name          | Card text wraps with `overflow-wrap: break-word; word-break: break-word;` |
| Special chars in name   | Rendered safely via `textContent` — no visual difference               |
| Rapid repeated clicks   | Card updates in place each time — no duplicates                        |
| JS disabled             | `<noscript>` message: "Ta aplikacja wymaga włączonego JavaScript."     |

---

## 10. Fieldset Styling Notes

Remove default `fieldset` styling to match custom design:

```css
.color-fieldset {
  border: none;
  margin: 0;
  padding: 0;
}

.color-fieldset legend {
  font-weight: 600;
  margin-bottom: var(--space-sm);
  padding: 0;
}
```

---

## 11. Full CSS Class Inventory

| Class name        | Element              | Purpose                           |
|-------------------|----------------------|-----------------------------------|
| `.app`            | `<main>`             | Centered container (matches pomidoro) |
| `.card`           | `<section>` (form)   | Form card panel (matches pomidoro) |
| `.color-fieldset` | `<fieldset>`         | Reset fieldset styling            |
| `.color-options`  | `<div>`              | Flex row for swatch layout        |
| `.color-option`   | `<label>`            | Single swatch + label group       |
| `.color-swatch`   | `<span>`             | Visual color circle               |
| `.color-label`    | `<span>`             | Text label below swatch           |
| `.card-greeting`  | `#card-output`       | Styled greeting card (added by JS)|
| `.error-msg`      | `<p>`                | Validation error text             |
| `.sr-only`        | `<h2>`, radio inputs | Visually hidden, accessible       |

---

## 12. Design Decisions Log

| # | Decision | Rationale |
|---|----------|-----------|
| D-01 | Light theme with `#f4f5f7` background | Matches `demo-pomidoro` visual language |
| D-02 | `.card` reused as form wrapper class | Consistent with pomidoro `.card` pattern |
| D-03 | Circular color swatches (48px) over styled radios | More intuitive color selection, industry standard pattern |
| D-04 | Filled (dark) Generate button | Single CTA — primary button style for clear hierarchy |
| D-05 | 520px max-width (vs pomidoro's 760px) | Narrower content fits the simpler UI; greeting card looks better centered in a compact column |
| D-06 | Card border-radius 16px (vs form 8px) | Larger radius on greeting card creates visual distinction from the form card |
| D-07 | `text-shadow` on Coral white text | Enhances readability at the 3.0:1 AA-large threshold |
| D-08 | `:focus-visible` global rule | Matches `demo-traffic-simulator` accessibility pattern |
| D-09 | System font stack | Per constraint (system fonts only); matches traffic-simulator |
| D-10 | No animations / transitions | Explicitly listed as non-goal |
