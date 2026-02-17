import { setPaused, setSetting, resetWorld } from './state.js';

export function bindControls({ elements, state, ui, onReset, saveSettings }) {
  elements.spawnRate.addEventListener('input', () => {
    setSetting(state, 'spawnRatePerMin', Number(elements.spawnRate.value));
    ui.updateControlValues(state.settings);
    saveSettings(state.settings);
  });

  elements.speedMultiplier.addEventListener('input', () => {
    setSetting(state, 'speedMultiplier', Number(elements.speedMultiplier.value));
    ui.updateControlValues(state.settings);
    saveSettings(state.settings);
  });

  elements.signalMode.addEventListener('change', () => {
    setSetting(state, 'signalMode', elements.signalMode.value);
    ui.updateControlValues(state.settings);
    saveSettings(state.settings);
  });

  elements.laneDensity.addEventListener('input', () => {
    setSetting(state, 'laneDensity', Number(elements.laneDensity.value));
    ui.updateControlValues(state.settings);
    saveSettings(state.settings);
  });

  elements.pauseResumeButton.addEventListener('click', () => {
    setPaused(state, !state.world.paused);
    ui.updateStatus(state.world.paused);
  });

  elements.resetButton.addEventListener('click', () => {
    resetWorld(state);
    setPaused(state, false);
    onReset();
    ui.updateStatus(false);
  });
}

export function syncControlsFromState(elements, settings) {
  elements.spawnRate.value = String(settings.spawnRatePerMin);
  elements.speedMultiplier.value = String(settings.speedMultiplier);
  elements.signalMode.value = settings.signalMode;
  elements.laneDensity.value = String(settings.laneDensity);
}