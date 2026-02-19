from __future__ import annotations

from .expression import evaluate
from .models import CompiledExpression, MarkedPoint, PlotConfig, PlotResult


def build_plot(
    compiled: CompiledExpression,
    config: PlotConfig,
    marker: MarkedPoint | None = None,
) -> PlotResult:
    points: set[tuple[int, int]] = set()
    clipped_points = 0

    for column in range(config.width):
        x_value = _column_to_x(column, config)
        try:
            y_value = evaluate(compiled, x_value)
        except Exception:
            continue

        if y_value < config.y_min or y_value > config.y_max:
            clipped_points += 1
            continue

        row = _y_to_row(y_value, config)
        points.add((row, column))

    axis_col = _axis_col(config)
    axis_row = _axis_row(config)

    resolved_marker = None
    if marker is not None:
        visible = (
            config.x_min <= marker.x <= config.x_max
            and config.y_min <= marker.y <= config.y_max
        )
        resolved_marker = MarkedPoint(x=marker.x, y=marker.y, visible=visible)

    return PlotResult(
        expression_text=compiled.expression_text,
        config=config,
        points=points,
        axis_row=axis_row,
        axis_col=axis_col,
        marker=resolved_marker,
        clipped_points=clipped_points,
    )


def marker_cell(plot: PlotResult) -> tuple[int, int] | None:
    if not plot.marker or not plot.marker.visible:
        return None
    row = _y_to_row(plot.marker.y, plot.config)
    col = _x_to_column(plot.marker.x, plot.config)
    return row, col


def _column_to_x(column: int, config: PlotConfig) -> float:
    if config.width <= 1:
        return config.x_min
    ratio = column / (config.width - 1)
    return config.x_min + ratio * (config.x_max - config.x_min)


def _x_to_column(x_value: float, config: PlotConfig) -> int:
    if config.x_max == config.x_min:
        return 0
    ratio = (x_value - config.x_min) / (config.x_max - config.x_min)
    return int(round(ratio * (config.width - 1)))


def _y_to_row(y_value: float, config: PlotConfig) -> int:
    if config.y_max == config.y_min:
        return 0
    ratio = (config.y_max - y_value) / (config.y_max - config.y_min)
    return int(round(ratio * (config.height - 1)))


def _axis_col(config: PlotConfig) -> int | None:
    if not (config.x_min <= 0 <= config.x_max):
        return None
    return _x_to_column(0.0, config)


def _axis_row(config: PlotConfig) -> int | None:
    if not (config.y_min <= 0 <= config.y_max):
        return None
    return _y_to_row(0.0, config)
