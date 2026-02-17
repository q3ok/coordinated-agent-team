# demo-click-message

## Purpose

Show the simplest UI flow: one button click changes the text in the result area without reloading the page.

## Quick start

1. Open `index.html` in a browser.
2. Click the "Show message" button.
3. Confirm the result area text changes without page reload.

## Run options

- Direct open: double-click `index.html` (`file://`).
- Optional local server: serve `demo-click-message/` (for final browser smoke-check parity).

## Scope

- Single HTML page.
- One button and one result area with `aria-live="polite"`.
- No backend, storage, network calls, or external dependencies.

## Release note

- Remaining manual step: execute one browser smoke-check in target release browser and confirm click-to-message flow end-to-end.
