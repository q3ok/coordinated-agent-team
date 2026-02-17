import { getVehiclePose } from './traffic-model.js';

function drawBackgroundGrid(ctx, width, height) {
  ctx.fillStyle = '#1b283d';
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = '#233754';
  ctx.lineWidth = 1;
  const spacing = 40;
  for (let x = 0; x <= width; x += spacing) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 0; y <= height; y += spacing) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }
}

function drawRoads(ctx, lanes, world) {
  const roadWidth = 56;
  ctx.lineCap = 'round';

  for (const lane of lanes) {
    ctx.strokeStyle = '#2f415e';
    ctx.lineWidth = roadWidth;
    ctx.beginPath();
    ctx.moveTo(lane.start.x, lane.start.y);
    ctx.lineTo(lane.end.x, lane.end.y);
    ctx.stroke();

    ctx.strokeStyle = '#5f769d';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([8, 10]);
    ctx.beginPath();
    ctx.moveTo(lane.start.x, lane.start.y);
    ctx.lineTo(lane.end.x, lane.end.y);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  const cx = world.width / 2;
  const cy = world.height / 2;
  ctx.strokeStyle = '#9fb1d6';
  ctx.lineWidth = 3;
  ctx.strokeRect(cx - 52, cy - 52, 104, 104);
}

function drawSignals(ctx, world, mode) {
  const cx = world.width / 2;
  const cy = world.height / 2;

  const horizontalGreen = mode === 'off' || mode === 'blink' || world.signals.phase === 'horizontal';
  const verticalGreen = mode === 'off' || mode === 'blink' || world.signals.phase === 'vertical';

  ctx.fillStyle = horizontalGreen ? '#53d28c' : '#ff6f6f';
  ctx.fillRect(cx - 80, cy - 68, 20, 10);
  ctx.fillRect(cx + 60, cy + 58, 20, 10);

  ctx.fillStyle = verticalGreen ? '#53d28c' : '#ff6f6f';
  ctx.fillRect(cx + 58, cy - 80, 10, 20);
  ctx.fillRect(cx - 68, cy + 60, 10, 20);
}

function drawVehicles(ctx, vehicles, lanesById) {
  for (const vehicle of vehicles) {
    const pose = getVehiclePose(vehicle, lanesById);

    ctx.save();
    ctx.translate(pose.x, pose.y);
    ctx.rotate(pose.angle);

    ctx.fillStyle = vehicle.state === 'stopped' ? '#ffcc66' : '#7cd7ff';
    ctx.fillRect(-vehicle.length / 2, -8, vehicle.length, 16);

    ctx.fillStyle = '#dcefff';
    ctx.fillRect(2 - vehicle.length / 2, -5, 8, 10);
    ctx.restore();
  }
}

export function createRenderer(canvas, lanes) {
  const ctx = canvas.getContext('2d');
  const lanesById = new Map(lanes.map((lane) => [lane.id, lane]));

  function render(state) {
    const world = state.world;
    drawBackgroundGrid(ctx, world.width, world.height);
    drawRoads(ctx, lanes, world);
    drawSignals(ctx, world, state.settings.signalMode);
    drawVehicles(ctx, world.vehicles, lanesById);
  }

  return { render };
}