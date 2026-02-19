from function_plot_cli.expression import validate_and_compile
from function_plot_cli.models import MarkedPoint, PlotConfig
from function_plot_cli.plotting import build_plot
from function_plot_cli.renderer import render


CONFIG = PlotConfig(x_min=-5, x_max=5, y_min=-5, y_max=5, width=20, height=10)


def test_renderer_is_deterministic_for_same_input():
    compiled = validate_and_compile("x")
    plot = build_plot(compiled, CONFIG)

    output_a = render(plot, unicode_mode=False)
    output_b = render(plot, unicode_mode=False)

    assert output_a.text == output_b.text


def test_marker_overrides_curve_symbol_when_visible():
    compiled = validate_and_compile("x")
    marker = MarkedPoint(x=0.0, y=0.0)
    plot = build_plot(compiled, CONFIG, marker)
    output = render(plot, unicode_mode=False)

    assert "Marker: (0.000, 0.000)" in output.text
    assert "o" in output.text


def test_ascii_mode_uses_ascii_symbols():
    compiled = validate_and_compile("sin(x)")
    plot = build_plot(compiled, CONFIG)
    output = render(plot, unicode_mode=False)

    assert "+" in output.text
    assert "*" in output.text
