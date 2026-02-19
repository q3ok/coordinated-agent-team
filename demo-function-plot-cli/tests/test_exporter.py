import pytest

from function_plot_cli.errors import ExportError
from function_plot_cli.exporter import export_rendered_plot
from function_plot_cli.models import RenderOutput


def _sample_output() -> RenderOutput:
    return RenderOutput(
        text="Plot Function: f(x) = sin(x)\n+---+\n",
        metadata={
            "function": "sin(x)",
            "x_range": "[-10,10]",
            "y_range": "[-10,10]",
            "marker": "none",
            "render_mode": "ascii",
        },
    )


def test_export_writes_metadata_and_graph(tmp_path):
    export_path = tmp_path / "plot.txt"
    export_rendered_plot(export_path, _sample_output())

    content = export_path.read_text(encoding="utf-8")
    assert "Function Plot CLI Export" in content
    assert "Function: sin(x)" in content
    assert "Plot Function: f(x) = sin(x)" in content


def test_export_requires_txt_extension(tmp_path):
    with pytest.raises(ExportError):
        export_rendered_plot(tmp_path / "plot.log", _sample_output())


def test_export_fails_for_missing_directory(tmp_path):
    with pytest.raises(ExportError):
        export_rendered_plot(tmp_path / "missing" / "plot.txt", _sample_output())
