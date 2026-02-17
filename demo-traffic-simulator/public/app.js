import { createState, normalizeSettings } from './state.js';
import { buildLanes } from './traffic-model.js';
import { createRenderer } from './renderer-canvas.js';
import { createUi } from './ui.js';
import { bindControls, syncControlsFromState } from './controls.js';
import { createSimulation } from './simulation.js';
import { loadSettings, saveSettings } from './storage.js';

function getElements() {
  return {
    canvas: document.getElementById('sim-canvas'),
    status: document.getElementById('simulation-status'),
    spawnRate: document.getElementById('spawn-rate'),
    spawnRateValue: document.getElementById('spawn-rate-value'),
    speedMultiplier: document.getElementById('speed-multiplier'),
    speedMultiplierValue: document.getElementById('speed-multiplier-value'),
    signalMode: document.getElementById('signal-mode'),
    laneDensity: document.getElementById('lane-density'),
    laneDensityValue: document.getElementById('lane-density-value'),
    pauseResumeButton: document.getElementById('pause-resume'),
    resetButton: document.getElementById('reset'),
    metricActive: document.getElementById('metric-active'),
    metricSpeed: document.getElementById('metric-speed'),
    metricThroughput: document.getElementById('metric-throughput'),
    metricStopped: document.getElementById('metric-stopped'),
  };
}

function bootstrap() {
  const elements = getElements();
  const persistedSettings = normalizeSettings(loadSettings() || {});
  const state = createState(persistedSettings);
  const lanes = buildLanes(state.world.width, state.world.height);
  const ui = createUi(elements);
  const renderer = createRenderer(elements.canvas, lanes);
  const simulation = createSimulation({ state, lanes, renderer, ui });

  syncControlsFromState(elements, state.settings);
  ui.updateControlValues(state.settings);
  ui.updateStatus(false);
  renderer.render(state);

  bindControls({
    elements,
    state,
    ui,
    onReset: () => simulation.resetTime(),
    saveSettings,
  });

  simulation.start();
}

bootstrap();