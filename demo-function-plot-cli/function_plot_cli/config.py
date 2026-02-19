from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    x_min: float = -10.0
    x_max: float = 10.0
    y_min: float = -10.0
    y_max: float = 10.0
    plot_width: int = 64
    plot_height: int = 20
    recents_limit: int = 10
    unicode_mode: bool = True


def default_recents_path() -> Path:
    return Path.home() / ".function_plot_cli_recents.json"
