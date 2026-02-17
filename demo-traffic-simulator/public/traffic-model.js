const VEHICLE_LENGTH = 20;
const MIN_GAP = 16;
const MAX_ACCEL = 32;
const MAX_BRAKE = 70;
const STOP_EPSILON = 1;

export function buildLanes(width, height) {
  const cx = width / 2;
  const cy = height / 2;
  const offset = 34;

  return [
    {
      id: 'eastbound',
      direction: 'horizontal',
      y: cy - offset,
      start: { x: -60, y: cy - offset },
      end: { x: width + 60, y: cy - offset },
      signalGroup: 'horizontal',
    },
    {
      id: 'westbound',
      direction: 'horizontal',
      y: cy + offset,
      start: { x: width + 60, y: cy + offset },
      end: { x: -60, y: cy + offset },
      signalGroup: 'horizontal',
    },
    {
      id: 'southbound',
      direction: 'vertical',
      x: cx + offset,
      start: { x: cx + offset, y: -60 },
      end: { x: cx + offset, y: height + 60 },
      signalGroup: 'vertical',
    },
    {
      id: 'northbound',
      direction: 'vertical',
      x: cx - offset,
      start: { x: cx - offset, y: height + 60 },
      end: { x: cx - offset, y: -60 },
      signalGroup: 'vertical',
    },
  ].map((lane) => {
    const dx = lane.end.x - lane.start.x;
    const dy = lane.end.y - lane.start.y;
    const length = Math.hypot(dx, dy);
    return {
      ...lane,
      dx: dx / length,
      dy: dy / length,
      length,
      stopLineS: length / 2 - 70,
      intersectionStartS: length / 2 - 45,
      intersectionEndS: length / 2 + 45,
    };
  });
}

export function worldToLanePoint(lane, s) {
  return {
    x: lane.start.x + lane.dx * s,
    y: lane.start.y + lane.dy * s,
  };
}

export function spawnVehicles(state, lanes, dtSec) {
  const world = state.world;
  const settings = state.settings;
  const laneCount = lanes.length;
  const perLaneRateSec = (settings.spawnRatePerMin / 60) * settings.laneDensity / laneCount;
  world.spawnRemainder += perLaneRateSec * dtSec * laneCount;

  while (world.spawnRemainder >= 1) {
    world.spawnRemainder -= 1;
    const lane = lanes[Math.floor(Math.random() * laneCount)];

    const firstVehicle = world.vehicles
      .filter((vehicle) => vehicle.laneId === lane.id)
      .sort((a, b) => a.s - b.s)[0];

    if (firstVehicle && firstVehicle.s < VEHICLE_LENGTH + MIN_GAP) {
      continue;
    }

    world.vehicles.push({
      id: `v-${world.nextVehicleId++}`,
      laneId: lane.id,
      s: 0,
      speed: 0,
      desiredSpeed: (35 + Math.random() * 15) * settings.speedMultiplier,
      length: VEHICLE_LENGTH,
      state: 'moving',
      inIntersection: false,
    });
  }
}

export function updateSignals(world, settings, dtMs) {
  if (settings.signalMode !== 'auto') {
    return;
  }

  world.signals.phaseElapsedMs += dtMs;
  if (world.signals.phaseElapsedMs >= world.signals.phaseDurationMs) {
    world.signals.phaseElapsedMs = 0;
    world.signals.phase = world.signals.phase === 'horizontal' ? 'vertical' : 'horizontal';
  }
}

function signalAllowsLane(lane, world, settings) {
  if (settings.signalMode === 'off') {
    return true;
  }
  if (settings.signalMode === 'blink') {
    return true;
  }
  return lane.signalGroup === world.signals.phase;
}

function getLeadVehicle(sortedLaneVehicles, index) {
  if (index === sortedLaneVehicles.length - 1) {
    return null;
  }
  return sortedLaneVehicles[index + 1];
}

function computeTargetSpeed(vehicle, lane, leadVehicle, world, settings, intersectionOccupied) {
  let target = vehicle.desiredSpeed;

  if (settings.signalMode === 'blink') {
    const distanceToStop = lane.stopLineS - vehicle.s;
    if (distanceToStop < 90 && distanceToStop > 0) {
      target = Math.min(target, vehicle.desiredSpeed * 0.6);
    }
  }

  const atIntersectionEntry = vehicle.s >= lane.intersectionStartS - 12;
  const beforeStopLine = vehicle.s < lane.stopLineS;
  const hasGreen = signalAllowsLane(lane, world, settings);

  if (beforeStopLine && atIntersectionEntry) {
    if (settings.signalMode === 'auto' && !hasGreen) {
      target = 0;
    }

    if ((settings.signalMode === 'off' || settings.signalMode === 'blink') && intersectionOccupied) {
      target = 0;
    }
  }

  if (leadVehicle) {
    const safeFrontS = leadVehicle.s - leadVehicle.length - MIN_GAP;
    const availableDistance = safeFrontS - vehicle.s;
    if (availableDistance <= 0) {
      target = 0;
    } else if (availableDistance < 40) {
      const ratio = Math.max(0, availableDistance / 40);
      target = Math.min(target, leadVehicle.speed * ratio);
    }
  }

  return Math.max(0, target);
}

export function updateVehicles(state, lanes, dtSec, dtMs) {
  const world = state.world;
  const settings = state.settings;
  let intersectionOccupied = world.vehicles.some((vehicle) => vehicle.inIntersection);

  for (const lane of lanes) {
    const laneVehicles = world.vehicles
      .filter((vehicle) => vehicle.laneId === lane.id)
      .sort((a, b) => a.s - b.s);

    for (let index = laneVehicles.length - 1; index >= 0; index -= 1) {
      const vehicle = laneVehicles[index];
      const leadVehicle = getLeadVehicle(laneVehicles, index);
      const targetSpeed = computeTargetSpeed(vehicle, lane, leadVehicle, world, settings, intersectionOccupied);

      if (vehicle.speed < targetSpeed) {
        vehicle.speed = Math.min(targetSpeed, vehicle.speed + MAX_ACCEL * dtSec);
      } else {
        vehicle.speed = Math.max(targetSpeed, vehicle.speed - MAX_BRAKE * dtSec);
      }

      vehicle.s += vehicle.speed * dtSec;

      const inIntersectionNow = vehicle.s >= lane.intersectionStartS && vehicle.s <= lane.intersectionEndS;
      if (inIntersectionNow && !vehicle.inIntersection) {
        intersectionOccupied = true;
      }
      if (!inIntersectionNow && vehicle.inIntersection) {
        intersectionOccupied = world.vehicles.some((v) => v !== vehicle && v.inIntersection);
      }
      vehicle.inIntersection = inIntersectionNow;

      if (vehicle.speed < STOP_EPSILON) {
        vehicle.state = 'stopped';
        world.stoppedTotalTicks += 1;
      } else if (targetSpeed < vehicle.desiredSpeed * 0.9) {
        vehicle.state = 'slowing';
      } else {
        vehicle.state = 'moving';
      }

      if (vehicle.s > lane.length + vehicle.length) {
        world.throughputEventsMs.push(world.timeMs + dtMs);
      }
    }
  }

  world.vehicles = world.vehicles.filter((vehicle) => {
    const lane = lanes.find((item) => item.id === vehicle.laneId);
    return lane && vehicle.s <= lane.length + vehicle.length;
  });
}

export function getVehiclePose(vehicle, lanesById) {
  const lane = lanesById.get(vehicle.laneId);
  const point = worldToLanePoint(lane, vehicle.s);
  const angle = Math.atan2(lane.dy, lane.dx);
  return { x: point.x, y: point.y, angle };
}