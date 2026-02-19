from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompiledExpression:
    expression_text: str
    ast_tree: object


@dataclass
class MarkedPoint:
    x: float
    y: float
    visible: bool = False


@dataclass(frozen=True)
class PlotConfig:
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    width: int
    height: int


@dataclass(frozen=True)
class PlotResult:
    expression_text: str
    config: PlotConfig
    points: set[tuple[int, int]]
    axis_row: int | None
    axis_col: int | None
    marker: MarkedPoint | None
    clipped_points: int


@dataclass(frozen=True)
class RenderOutput:
    text: str
    metadata: dict[str, str]
