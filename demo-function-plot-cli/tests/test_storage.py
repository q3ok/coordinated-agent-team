import json

from function_plot_cli.storage import load_recent_functions, save_recent_function


def test_missing_recents_file_returns_empty_list(tmp_path):
    path = tmp_path / "recents.json"
    assert load_recent_functions(path) == []


def test_corrupt_recents_file_returns_empty_list(tmp_path):
    path = tmp_path / "recents.json"
    path.write_text("{bad", encoding="utf-8")
    assert load_recent_functions(path) == []


def test_save_deduplicates_and_keeps_most_recent_first(tmp_path):
    path = tmp_path / "recents.json"
    save_recent_function(path, "sin(x)")
    save_recent_function(path, "x**2")
    recents = save_recent_function(path, "sin(x)")

    assert recents == ["sin(x)", "x**2"]


def test_save_caps_recents_at_10(tmp_path):
    path = tmp_path / "recents.json"
    for index in range(12):
        save_recent_function(path, f"x+{index}")

    recents = json.loads(path.read_text(encoding="utf-8"))
    assert len(recents) == 10
    assert recents[0] == "x+11"
    assert recents[-1] == "x+2"
