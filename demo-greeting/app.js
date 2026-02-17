// @ts-check

/**
 * Greeting Card Generator — app.js
 * ES Module: pure functions + initApp factory for DOM binding.
 */

/** Preset card colors with matching text colors for contrast. */
export const COLOR_PRESETS = [
  { value: '#FF6B6B', label: 'Coral', textColor: '#ffffff' },
  { value: '#4ECDC4', label: 'Sky Blue', textColor: '#1f2937' },
  { value: '#FFE66D', label: 'Sunshine', textColor: '#1f2937' },
];

/**
 * Validate a raw name string.
 * @param {string} raw
 * @returns {{ ok: true, name: string } | { ok: false, error: string }}
 */
export function validateName(raw) {
  const trimmed = (raw ?? '').trim();
  if (trimmed.length === 0) {
    return { ok: false, error: 'Wpisz imię, aby wygenerować kartkę.' };
  }
  return { ok: true, name: trimmed };
}

/**
 * Generate the greeting text for a given name.
 * @param {string} name
 * @returns {string}
 */
export function greetingText(name) {
  return `Hello, ${name}!`;
}

/**
 * Initialise the Greeting Card app — binds DOM elements and event handlers.
 * @param {Document} [doc=document]
 */
export function initApp(doc = document) {
  const _nameInput = /** @type {HTMLInputElement} */ (doc.getElementById('name-input'));
  const _generateBtn = doc.getElementById('generate-btn');
  const _errorMsg = doc.getElementById('error-msg');
  const _cardOutput = doc.getElementById('card-output');

  if (!_nameInput || !_generateBtn || !_errorMsg || !_cardOutput) {
    return; // DOM not ready or IDs missing — bail silently
  }

  // Re-bind after null guard so TS recognises non-null in closures
  /** @type {HTMLInputElement} */
  const nameInput = _nameInput;
  /** @type {HTMLElement} */
  const errorMsg = _errorMsg;
  /** @type {HTMLElement} */
  const cardOutput = _cardOutput;

  /**
   * Show the validation error message and mark the input as invalid.
   * @param {string} message
   */
  function showError(message) {
    errorMsg.textContent = message;
    errorMsg.hidden = false;
    nameInput.classList.add('input-error');
  }

  /** Hide the validation error message and remove the invalid marker. */
  function hideError() {
    errorMsg.textContent = '';
    errorMsg.hidden = true;
    nameInput.classList.remove('input-error');
  }

  /**
   * Read the currently selected color radio value.
   * Falls back to the first preset if nothing is checked.
   * @returns {{ value: string, textColor: string }}
   */
  function getSelectedColor() {
    const checked = /** @type {HTMLInputElement | null} */ (doc.querySelector('input[name="color"]:checked'));
    const colorValue = checked ? checked.value : COLOR_PRESETS[0].value;
    const preset = COLOR_PRESETS.find((p) => p.value === colorValue);
    return preset ?? COLOR_PRESETS[0];
  }

  /**
   * Render the greeting card into #card-output.
   * Uses textContent exclusively — never innerHTML.
   * @param {string} name
   * @param {{ value: string, textColor: string }} preset
   */
  function renderCard(name, preset) {
    cardOutput.textContent = greetingText(name);
    cardOutput.style.backgroundColor = preset.value;
    cardOutput.style.color = preset.textColor;

    // Enhanced readability for Coral (white text on medium background)
    cardOutput.style.textShadow =
      preset.value === COLOR_PRESETS[0].value
        ? '0 1px 2px rgba(0,0,0,0.2)'
        : 'none';

    cardOutput.classList.add('card-greeting');
  }

  /** Handle Generate button click. */
  function handleGenerate() {
    const result = validateName(nameInput.value);

    if (!result.ok) {
      showError(result.error);
      // Hide the card when validation fails
      cardOutput.classList.remove('card-greeting');
      cardOutput.textContent = '';
      cardOutput.style.backgroundColor = '';
      cardOutput.style.color = '';
      cardOutput.style.textShadow = '';
      return;
    }

    hideError();
    const preset = getSelectedColor();
    renderCard(result.name, preset);
  }

  _generateBtn.addEventListener('click', handleGenerate);
}

// Auto-init when loaded as a module in the browser
initApp();
