const SETTINGS_DEFAULTS = {
  spawnRatePerMin: 60,
  speedMultiplier: 1,
  signalMode: 'auto',
  laneDensity: 0.6,
};

const WORLD_DEFAULTS = {
  width: 1280,
  height: 720,
  tick: 0,
  timeMs: 0,
  paused: false,
  vehicles: [],
  nextVehicleId: 1,
  spawnRemainder: 0,
  throughputEventsMs: [],
  stoppedTotalTicks: 0,
  signals: {
    phase: 'horizontal',
    phaseElapsedMs: 0,
    phaseDurationMs: 6000,
  },
};

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function normalizeSettings(partialSettings = {}) {
  const signalMode = ['auto', 'blink', 'off'].includes(partialSettings.signalMode)
    ? partialSettings.signalMode
    : SETTINGS_DEFAULTS.signalMode;

  return {
    spawnRatePerMin: clamp(Number(partialSettings.spawnRatePerMin) || SETTINGS_DEFAULTS.spawnRatePerMin, 10, 120),
    speedMultiplier: clamp(Number(partialSettings.speedMultiplier) || SETTINGS_DEFAULTS.speedMultiplier, 0.5, 2),
    signalMode,
    laneDensity: clamp(Number(partialSettings.laneDensity) || SETTINGS_DEFAULTS.laneDensity, 0.2, 1),
  };
}

export function createInitialWorld() {
  return structuredClone(WORLD_DEFAULTS);
}

export function createState(initialSettings = {}) {
  return {
    settings: normalizeSettings({ ...SETTINGS_DEFAULTS, ...initialSettings }),
    world: createInitialWorld(),
  };
}

export function resetWorld(state) {
  state.world = createInitialWorld();
}

export function setPaused(state, paused) {
  state.world.paused = Boolean(paused);
}

export function setSetting(state, key, value) {
  if (!(key in state.settings)) {
    return;
  }

  const normalized = normalizeSettings({ ...state.settings, [key]: value });
  state.settings = normalized;
}

export { SETTINGS_DEFAULTS };