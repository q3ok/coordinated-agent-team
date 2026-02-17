const THROUGHPUT_WINDOW_MS = 60000;

export function updateMetrics(state) {
  const world = state.world;
  const now = world.timeMs;

  world.throughputEventsMs = world.throughputEventsMs.filter((timestamp) => now - timestamp <= THROUGHPUT_WINDOW_MS);

  const activeVehicles = world.vehicles.length;
  const avgSpeed =
    activeVehicles === 0
      ? 0
      : world.vehicles.reduce((sum, vehicle) => sum + vehicle.speed, 0) / activeVehicles;

  const stoppedVehicles = world.vehicles.filter((vehicle) => vehicle.state === 'stopped' || vehicle.speed < 1).length;

  return {
    activeVehicles,
    avgSpeed,
    throughputPerMin: world.throughputEventsMs.length,
    stoppedVehicles,
  };
}