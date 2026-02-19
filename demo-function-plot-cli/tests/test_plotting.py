from function_plot_cli.expression import validate_and_compile
from function_plot_cli.models import MarkedPoint, PlotConfig
from function_plot_cli.plotting import build_plot, marker_cell


def _config() -> PlotConfig:
    return PlotConfig(x_min=-10, x_max=10, y_min=-10, y_max=10, width=40, height=14)


def test_build_plot_creates_points_and_axes():
    compiled = validate_and_compile("sin(x)")
    plot = build_plot(compiled, _config())

    assert len(plot.points) > 0
    assert plot.axis_col is not None
    assert plot.axis_row is not None


def test_marker_visible_and_mapped_to_cell():
    compiled = validate_and_compile("x")
    marker = MarkedPoint(x=2.0, y=2.0)
    plot = build_plot(compiled, _config(), marker)

    assert plot.marker is not None
    assert plot.marker.visible is True
    assert marker_cell(plot) is not None


def test_marker_outside_viewport_is_not_visible():
    compiled = validate_and_compile("x")
    marker = MarkedPoint(x=100.0, y=100.0)
    plot = build_plot(compiled, _config(), marker)

    assert plot.marker is not None
    assert plot.marker.visible is False
    assert marker_cell(plot) is None
