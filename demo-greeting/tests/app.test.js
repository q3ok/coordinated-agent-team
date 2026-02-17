// @ts-check

// Provide a minimal document mock so the auto-initApp() call at module
// scope does not throw in Node.js (it calls getElementById which returns
// null → initApp bails silently, which is the expected path).
// IMPORTANT: Must be set BEFORE importing app.js because ESM hoists imports.
globalThis.document = /** @type {any} */ ({
  getElementById: () => null,
  querySelector: () => null,
});

// Dynamic import so globalThis.document is set first
const { validateName, greetingText, COLOR_PRESETS } = await import('../app.js');

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

// ─── validateName ────────────────────────────────────────────────────────────

describe('validateName', () => {
  it('returns ok:true with trimmed name for valid input', () => {
    const result = validateName('Alice');
    assert.deepStrictEqual(result, { ok: true, name: 'Alice' });
  });

  it('trims leading and trailing whitespace', () => {
    const result = validateName('  Bob  ');
    assert.deepStrictEqual(result, { ok: true, name: 'Bob' });
  });

  it('returns ok:false for empty string', () => {
    const result = validateName('');
    assert.equal(result.ok, false);
    assert.ok('error' in result && result.error.length > 0);
  });

  it('returns ok:false for whitespace-only string', () => {
    const result = validateName('   ');
    assert.equal(result.ok, false);
    assert.ok('error' in result && result.error.length > 0);
  });

  it('returns ok:false for null/undefined input', () => {
    // @ts-ignore — intentional null test
    const result = validateName(null);
    assert.equal(result.ok, false);

    // @ts-ignore — intentional undefined test
    const result2 = validateName(undefined);
    assert.equal(result2.ok, false);
  });

  it('preserves special characters in the name (XSS-safe at validation level)', () => {
    const xss = '<script>alert(1)</script>';
    const result = validateName(xss);
    assert.deepStrictEqual(result, { ok: true, name: xss });
  });

  it('handles very long names without error', () => {
    const longName = 'A'.repeat(10000);
    const result = validateName(longName);
    assert.equal(result.ok, true);
    assert.ok('name' in result && result.name.length === 10000);
  });

  it('handles single-character name', () => {
    const result = validateName('X');
    assert.deepStrictEqual(result, { ok: true, name: 'X' });
  });

  it('handles name with unicode characters', () => {
    const result = validateName('Łukasz');
    assert.deepStrictEqual(result, { ok: true, name: 'Łukasz' });
  });
});

// ─── greetingText ────────────────────────────────────────────────────────────

describe('greetingText', () => {
  it('returns "Hello, {name}!" for a normal name', () => {
    assert.equal(greetingText('Alice'), 'Hello, Alice!');
  });

  it('returns "Hello, Bob!" for Bob', () => {
    assert.equal(greetingText('Bob'), 'Hello, Bob!');
  });

  it('includes special characters literally', () => {
    const xss = '<script>alert(1)</script>';
    assert.equal(greetingText(xss), `Hello, ${xss}!`);
  });

  it('handles empty string', () => {
    assert.equal(greetingText(''), 'Hello, !');
  });

  it('handles name with unicode', () => {
    assert.equal(greetingText('Łukasz'), 'Hello, Łukasz!');
  });
});

// ─── COLOR_PRESETS ───────────────────────────────────────────────────────────

describe('COLOR_PRESETS', () => {
  it('contains exactly 3 presets', () => {
    assert.equal(COLOR_PRESETS.length, 3);
  });

  it('each preset has value, label, and textColor', () => {
    for (const preset of COLOR_PRESETS) {
      assert.ok(typeof preset.value === 'string' && preset.value.startsWith('#'));
      assert.ok(typeof preset.label === 'string' && preset.label.length > 0);
      assert.ok(typeof preset.textColor === 'string' && preset.textColor.startsWith('#'));
    }
  });

  it('has Coral as first preset', () => {
    assert.equal(COLOR_PRESETS[0].label, 'Coral');
    assert.equal(COLOR_PRESETS[0].value, '#FF6B6B');
  });

  it('has Sky Blue as second preset', () => {
    assert.equal(COLOR_PRESETS[1].label, 'Sky Blue');
    assert.equal(COLOR_PRESETS[1].value, '#4ECDC4');
  });

  it('has Sunshine as third preset', () => {
    assert.equal(COLOR_PRESETS[2].label, 'Sunshine');
    assert.equal(COLOR_PRESETS[2].value, '#FFE66D');
  });
});
