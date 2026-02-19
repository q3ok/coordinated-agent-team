from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .errors import StorageError


def load_recent_functions(path: Path) -> list[str]:
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(content, list):
        return []

    result: list[str] = []
    for item in content:
        if isinstance(item, str):
            cleaned = item.strip()
            if cleaned and cleaned not in result:
                result.append(cleaned)
    return result[:10]


def save_recent_function(path: Path, expression_text: str, max_items: int = 10) -> list[str]:
    expression = expression_text.strip()
    if not expression:
        return load_recent_functions(path)

    recents = [entry for entry in load_recent_functions(path) if entry != expression]
    recents.insert(0, expression)
    recents = recents[:max_items]
    _atomic_write_json(path, recents)
    return recents


def clear_recent_functions(path: Path) -> None:
    _atomic_write_json(path, [])


def _atomic_write_json(path: Path, content: list[str]) -> None:
    temp_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as temp:
            json.dump(content, temp, ensure_ascii=False, indent=2)
            temp.flush()
            temp_path = Path(temp.name)
        temp_path.replace(path)
    except OSError as error:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise StorageError("Could not persist recent plots.") from error
