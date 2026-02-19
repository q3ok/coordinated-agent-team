from __future__ import annotations


def format_status(level: str, message: str) -> str:
    normalized = level.upper()
    if normalized not in {"ERROR", "OK", "WARN", "INFO"}:
        normalized = "INFO"
    return f"[{normalized}] {message}"


def build_main_menu(active_function: str | None, recents_count: int) -> str:
    active = active_function if active_function else "None"
    lines = [
        "+--------------------------------------------------------------------------------+",
        "| Function Plot CLI                                                              |",
        "+--------------------------------------------------------------------------------+",
        f"| Active function: {active[:58]:<58} |",
        f"| Recents: {recents_count:<71}|",
        "+--------------------------------------------------------------------------------+",
        "| 1) Plot function                                                               |",
        "| 2) Evaluate y for x and mark point                                             |",
        "| 3) Show recent plots                                                           |",
        "| 4) Export current plot to file                                                 |",
        "| 5) Exit                                                                        |",
        "+--------------------------------------------------------------------------------+",
        "| [1-5] Select   [Q] Exit                                                        |",
        "+--------------------------------------------------------------------------------+",
    ]
    return "\n".join(lines)
