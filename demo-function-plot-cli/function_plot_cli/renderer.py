from __future__ import annotations

from .models import PlotResult, RenderOutput
from .plotting import marker_cell


_UNICODE_SYMBOLS = {
    "frame_h": "─",
    "frame_v": "│",
    "tl": "┌",
    "tr": "┐",
    "bl": "└",
    "br": "┘",
    "axis_h": "─",
    "axis_v": "│",
    "axis_c": "┼",
    "curve": "•",
    "marker": "◆",
}

_ASCII_SYMBOLS = {
    "frame_h": "-",
    "frame_v": "|",
    "tl": "+",
    "tr": "+",
    "bl": "+",
    "br": "+",
    "axis_h": "-",
    "axis_v": "|",
    "axis_c": "+",
    "curve": "*",
    "marker": "o",
}


def render(plot: PlotResult, unicode_mode: bool = True) -> RenderOutput:
    symbols = _UNICODE_SYMBOLS if unicode_mode else _ASCII_SYMBOLS
    grid = [[" " for _ in range(plot.config.width)] for _ in range(plot.config.height)]

    if plot.axis_row is not None:
        for col in range(plot.config.width):
            grid[plot.axis_row][col] = symbols["axis_h"]

    if plot.axis_col is not None:
        for row in range(plot.config.height):
            grid[row][plot.axis_col] = symbols["axis_v"]

    if plot.axis_row is not None and plot.axis_col is not None:
        grid[plot.axis_row][plot.axis_col] = symbols["axis_c"]

    for row, col in sorted(plot.points):
        if 0 <= row < plot.config.height and 0 <= col < plot.config.width:
            grid[row][col] = symbols["curve"]

    marker_position = marker_cell(plot)
    if marker_position is not None:
        row, col = marker_position
        if 0 <= row < plot.config.height and 0 <= col < plot.config.width:
            grid[row][col] = symbols["marker"]

    graph_lines = ["".join(row) for row in grid]
    framed = _frame_lines(graph_lines, symbols)

    marker_text = "none"
    if plot.marker is not None:
        marker_text = f"({plot.marker.x:.3f}, {plot.marker.y:.3f})"

    metadata_lines = [
        f"Function: f(x) = {plot.expression_text}",
        f"Range: x:[{plot.config.x_min:g},{plot.config.x_max:g}] y:[{plot.config.y_min:g},{plot.config.y_max:g}]",
        f"Marker: {marker_text}",
        f"Render mode: {'unicode' if unicode_mode else 'ascii'}",
    ]

    if plot.clipped_points:
        metadata_lines.append(f"Warning: clipped samples = {plot.clipped_points}")

    output_text = "\n".join([
        f"Plot Function: f(x) = {plot.expression_text}",
        *framed,
        *metadata_lines,
    ])

    return RenderOutput(
        text=output_text,
        metadata={
            "function": plot.expression_text,
            "x_range": f"[{plot.config.x_min:g},{plot.config.x_max:g}]",
            "y_range": f"[{plot.config.y_min:g},{plot.config.y_max:g}]",
            "marker": marker_text,
            "render_mode": "unicode" if unicode_mode else "ascii",
        },
    )


def _frame_lines(lines: list[str], symbols: dict[str, str]) -> list[str]:
    if not lines:
        return []
    width = len(lines[0])
    top = symbols["tl"] + symbols["frame_h"] * width + symbols["tr"]
    bottom = symbols["bl"] + symbols["frame_h"] * width + symbols["br"]
    body = [f"{symbols['frame_v']}{line}{symbols['frame_v']}" for line in lines]
    return [top, *body, bottom]
