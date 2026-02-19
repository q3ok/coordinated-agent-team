from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .errors import ExportError
from .models import RenderOutput


def export_rendered_plot(path: Path, output: RenderOutput) -> None:
    if path.suffix.lower() != ".txt":
        raise ExportError("Output file must use .txt extension.")

    if path.parent and not path.parent.exists():
        raise ExportError("Output directory does not exist.")

    timestamp = datetime.now(timezone.utc).isoformat()
    header = [
        "Function Plot CLI Export",
        f"Timestamp: {timestamp}",
        f"Function: {output.metadata.get('function', '')}",
        f"Range: x={output.metadata.get('x_range', '')}, y={output.metadata.get('y_range', '')}",
        f"Marker: {output.metadata.get('marker', 'none')}",
        f"Render mode: {output.metadata.get('render_mode', 'unicode')}",
        "",
    ]
    payload = "\n".join(header) + output.text + "\n"

    try:
        path.write_text(payload, encoding="utf-8")
    except OSError as error:
        raise ExportError("Cannot write export file.") from error
