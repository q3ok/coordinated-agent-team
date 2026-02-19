from __future__ import annotations

from pathlib import Path
from typing import Callable

from .config import AppConfig, default_recents_path
from .errors import (
    ExportError,
    ExpressionDomainError,
    ExpressionValidationError,
    InputValidationError,
    StorageError,
)
from .exporter import export_rendered_plot
from .expression import evaluate, validate_and_compile
from .input_parser import normalize_expression, parse_float
from .models import MarkedPoint, PlotConfig, RenderOutput
from .plotting import build_plot
from .renderer import render
from .storage import clear_recent_functions, load_recent_functions, save_recent_function
from .ui import build_main_menu, format_status


def main(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    config: AppConfig | None = None,
) -> int:
    app_config = config or AppConfig()
    recents_path = default_recents_path()

    active_expression_text: str | None = None
    active_compiled = None
    last_render: RenderOutput | None = None

    while True:
        recents_count = len(load_recent_functions(recents_path))
        output_fn(build_main_menu(active_expression_text, recents_count))
        choice = input_fn("Select option [1-5]: ").strip().lower()

        if choice in {"5", "q"}:
            output_fn(format_status("info", "Bye."))
            return 0

        if choice == "1":
            expression_text = input_fn("Enter function f(x): ")
            active_expression_text, active_compiled, last_render = _plot_expression(
                expression_text,
                app_config,
                recents_path,
                output_fn,
            )
            continue

        if choice == "2":
            if active_compiled is None:
                output_fn(format_status("warn", "No active function. Plot a function first."))
                continue
            x_text = input_fn("Enter x value: ")
            try:
                x_value = parse_float(x_text, field_name="x")
                y_value = evaluate(active_compiled, x_value)
            except (InputValidationError, ExpressionDomainError, ExpressionValidationError) as error:
                output_fn(format_status("error", str(error)))
                continue

            marker = MarkedPoint(x=x_value, y=y_value)
            plot = build_plot(active_compiled, _plot_config(app_config), marker)
            last_render = render(plot, unicode_mode=app_config.unicode_mode)
            output_fn(f"Result: x = {x_value:.3f}, y = {y_value:.3f}")
            if plot.marker is not None and plot.marker.visible:
                output_fn(format_status("ok", "Marker placed on visible graph."))
            else:
                output_fn(format_status("warn", "Marker is outside visible range."))
            output_fn(last_render.text)
            continue

        if choice == "3":
            _show_recents(input_fn, output_fn, recents_path)
            selection = input_fn("Select recent index to plot, C to clear, M to return: ").strip().lower()
            if selection == "m":
                continue
            if selection == "c":
                clear_recent_functions(recents_path)
                output_fn(format_status("ok", "Recent plots cleared."))
                continue

            recents = load_recent_functions(recents_path)
            try:
                index = int(selection) - 1
            except ValueError:
                output_fn(format_status("error", "Invalid selection."))
                continue

            if index < 0 or index >= len(recents):
                output_fn(format_status("error", "Recent index out of range."))
                continue

            active_expression_text, active_compiled, last_render = _plot_expression(
                recents[index],
                app_config,
                recents_path,
                output_fn,
            )
            continue

        if choice == "4":
            if last_render is None:
                output_fn(format_status("error", "No rendered plot available. Plot a function first."))
                continue
            path_text = input_fn("Output path (.txt): ")
            export_path = Path(path_text.strip())
            try:
                export_rendered_plot(export_path, last_render)
            except ExportError as error:
                output_fn(format_status("error", str(error)))
                continue
            output_fn(format_status("ok", f"Plot exported to {export_path}"))
            continue

        output_fn(format_status("error", "Unknown option. Use values 1-5."))


def _plot_config(config: AppConfig) -> PlotConfig:
    return PlotConfig(
        x_min=config.x_min,
        x_max=config.x_max,
        y_min=config.y_min,
        y_max=config.y_max,
        width=config.plot_width,
        height=config.plot_height,
    )


def _plot_expression(
    expression_text: str,
    app_config: AppConfig,
    recents_path: Path,
    output_fn: Callable[[str], None],
):
    try:
        normalized = normalize_expression(expression_text)
        compiled = validate_and_compile(normalized)
    except (InputValidationError, ExpressionValidationError) as error:
        output_fn(format_status("error", str(error)))
        return None, None, None

    plot = build_plot(compiled, _plot_config(app_config))
    output = render(plot, unicode_mode=app_config.unicode_mode)
    try:
        save_recent_function(recents_path, normalized, max_items=app_config.recents_limit)
    except StorageError as error:
        output_fn(format_status("warn", str(error)))
    output_fn(format_status("ok", "Function plotted."))
    output_fn(output.text)
    return normalized, compiled, output


def _show_recents(
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    recents_path: Path,
) -> None:
    del input_fn
    recents = load_recent_functions(recents_path)
    output_fn("Recent Plots (max 10, most-recent-first)")
    if not recents:
        output_fn(format_status("info", "No recent plots yet. Plot a function to create history."))
        return

    for index, expression_text in enumerate(recents, start=1):
        output_fn(f"{index}) {expression_text}")


if __name__ == "__main__":
    raise SystemExit(main())
