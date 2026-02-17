import { spawnVehicles, updateSignals, updateVehicles } from './traffic-model.js';
import { updateMetrics } from './metrics.js';

const FIXED_DT_MS = 100;
const FIXED_DT_SEC = FIXED_DT_MS / 1000;

export function createSimulation({ state, lanes, renderer, ui }) {
  let lastTime = performance.now();
  let accumulator = 0;
  let running = false;
  let rafId = 0;

  function tick(now) {
    if (!running) {
      return;
    }

    const elapsed = Math.min(1000, now - lastTime);
    lastTime = now;
    accumulator += elapsed;

    while (accumulator >= FIXED_DT_MS) {
      if (!state.world.paused) {
        spawnVehicles(state, lanes, FIXED_DT_SEC);
        updateSignals(state.world, state.settings, FIXED_DT_MS);
        updateVehicles(state, lanes, FIXED_DT_SEC, FIXED_DT_MS);
        state.world.timeMs += FIXED_DT_MS;
        state.world.tick += 1;
      }

      accumulator -= FIXED_DT_MS;
    }

    const metrics = updateMetrics(state);
    renderer.render(state);
    ui.updateMetrics(metrics);

    rafId = requestAnimationFrame(tick);
  }

  return {
    start() {
      if (running) {
        return;
      }
      running = true;
      lastTime = performance.now();
      rafId = requestAnimationFrame(tick);
    },
    stop() {
      running = false;
      cancelAnimationFrame(rafId);
    },
    resetTime() {
      accumulator = 0;
      lastTime = performance.now();
    },
  };
}