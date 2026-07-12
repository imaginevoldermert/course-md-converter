from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ImageAsset:
    path: str
    source_page: int
    description: str = ""


@dataclass
class Formula:
    latex: str
    source_page: int
    source: str
    confidence: float = 1.0


@dataclass
class Page:
    number: int
    title: str = ""
    text: list[str] = field(default_factory=list)
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    formulas: list[Formula] = field(default_factory=list)


@dataclass
class Document:
    source: str
    kind: str
    pages: list[Page]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConversionResult:
    markdown_path: Path
    manifest_path: Path
    pending_path: Path | None = None
