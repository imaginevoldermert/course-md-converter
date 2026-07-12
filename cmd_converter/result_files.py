from __future__ import annotations

import io
import zipfile
from pathlib import Path


def list_result_files(root: Path) -> list[dict[str, object]]:
    """Return a stable, display-ready inventory without exposing other folders."""
    return [
        {"文件": file.relative_to(root).as_posix(), "大小（KB）": round(file.stat().st_size / 1024, 1)}
        for file in sorted(root.rglob("*"))
        if file.is_file()
    ]


def build_result_zip(root: Path) -> bytes:
    """Package only one conversion result directory in memory."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(root.rglob("*")):
            if file.is_file():
                archive.write(file, file.relative_to(root))
    return buffer.getvalue()
