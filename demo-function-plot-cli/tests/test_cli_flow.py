from pathlib import Path

import function_plot_cli.cli as cli_module
from function_plot_cli.config import AppConfig
from function_plot_cli.errors import ExpressionValidationError, StorageError


def _run_cli(scripted_inputs, monkeypatch, tmp_path):
    outputs = []
    sequence = iter(scripted_inputs)

    monkeypatch.setattr(cli_module, "default_recents_path", lambda: tmp_path / "recents.json")

    def fake_input(prompt: str) -> str:
        outputs.append(prompt)
        return next(sequence)

    cli_module.main(
        input_fn=fake_input,
        output_fn=outputs.append,
        config=AppConfig(plot_width=30, plot_height=10, unicode_mode=False),
    )
    return outputs


def test_menu_contains_required_options(monkeypatch, tmp_path):
    outputs = _run_cli(["5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)

    assert "1) Plot function" in all_text
    assert "2) Evaluate y for x and mark point" in all_text
    assert "3) Show recent plots" in all_text
    assert "4) Export current plot to file" in all_text
    assert "5) Exit" in all_text


def test_evaluate_requires_active_function(monkeypatch, tmp_path):
    outputs = _run_cli(["2", "5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)
    assert "No active function" in all_text


def test_recents_persist_and_deduplicate(monkeypatch, tmp_path):
    outputs = _run_cli(["1", "sin(x)", "1", "x", "1", "sin(x)", "5"], monkeypatch, tmp_path)
    del outputs
    recents = (tmp_path / "recents.json").read_text(encoding="utf-8")
    assert recents.count("sin(x)") == 1


def test_evaluate_marks_visible_point(monkeypatch, tmp_path):
    outputs = _run_cli(["1", "sin(x)", "2", "0", "5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)

    assert "Result: x = 0.000, y = 0.000" in all_text
    assert "Marker placed on visible graph" in all_text


def test_export_creates_txt_file_with_graph(monkeypatch, tmp_path):
    export_path = tmp_path / "plot.txt"
    outputs = _run_cli(["1", "sin(x)", "4", str(export_path), "5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)

    assert "Plot exported to" in all_text
    assert export_path.exists()
    assert "Function Plot CLI Export" in export_path.read_text(encoding="utf-8")


def test_evaluate_validation_error_does_not_crash_flow(monkeypatch, tmp_path):
    def raise_validation_error(compiled, x):
        del compiled, x
        raise ExpressionValidationError("Unsupported expression construct.")

    monkeypatch.setattr(cli_module, "evaluate", raise_validation_error)
    outputs = _run_cli(["1", "sin(x)", "2", "1", "5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)

    assert "Unsupported expression construct." in all_text
    assert "Bye." in all_text


def test_recents_write_failure_does_not_crash_plotting_flow(monkeypatch, tmp_path):
    def raise_storage_error(path, expression_text, max_items=10):
        del path, expression_text, max_items
        raise StorageError("Could not persist recent plots.")

    monkeypatch.setattr(cli_module, "save_recent_function", raise_storage_error)
    outputs = _run_cli(["1", "sin(x)", "5"], monkeypatch, tmp_path)
    all_text = "\n".join(outputs)

    assert "Could not persist recent plots." in all_text
    assert "Function plotted." in all_text
    assert "Bye." in all_text
