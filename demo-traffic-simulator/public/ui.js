export function createUi(elements) {
  function updateControlValues(settings) {
    elements.spawnRateValue.textContent = `${settings.spawnRatePerMin.toFixed(0)} poj./min`;
    elements.speedMultiplierValue.textContent = `${settings.speedMultiplier.toFixed(1)}x`;
    elements.laneDensityValue.textContent = `${settings.laneDensity.toFixed(1)}`;
    elements.pauseResumeButton.textContent = elements.pauseResumeButton.dataset.paused === 'true' ? 'Wznów' : 'Pauza';
  }

  function updateStatus(paused) {
    elements.status.textContent = paused ? 'Stan: Pauza' : 'Stan: Działa';
    elements.pauseResumeButton.textContent = paused ? 'Wznów' : 'Pauza';
    elements.pauseResumeButton.dataset.paused = paused ? 'true' : 'false';
  }

  function updateMetrics(metrics) {
    elements.metricActive.textContent = String(metrics.activeVehicles);
    elements.metricSpeed.textContent = metrics.avgSpeed.toFixed(1);
    elements.metricThroughput.textContent = metrics.throughputPerMin.toFixed(1);
    elements.metricStopped.textContent = String(metrics.stoppedVehicles);
  }

  return {
    updateControlValues,
    updateStatus,
    updateMetrics,
  };
}