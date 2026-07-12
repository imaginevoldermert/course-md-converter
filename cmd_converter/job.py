from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .extractors import DocumentExtractor
from .markdown import build_lecture
from .models import ConversionResult, Formula
from .providers import get_provider


@dataclass
class ConversionConfig:
    output_dir: Path
    provider: str = "openai_compatible"
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    vision_enabled: bool = True

    @classmethod
    def from_environment(cls, **overrides):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        values = {
            "provider": os.getenv("CMD_PROVIDER", "openai_compatible"),
            "model": os.getenv("CMD_MODEL"), "base_url": os.getenv("CMD_BASE_URL"),
            "api_key": os.getenv("CMD_API_KEY"), "vision_enabled": True,
        }
        values.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**values)


class ConversionJob:
    def __init__(self, config: ConversionConfig): self.config = config

    def convert_path(self, input_path: Path) -> list[ConversionResult]:
        if input_path.is_file(): return [self.convert_file(input_path)]
        allowed = {".doc", ".docx", ".ppt", ".pptx", ".pdf"}
        return [self.convert_file(p) for p in sorted(input_path.rglob("*")) if p.suffix.lower() in allowed]

    def convert_file(self, source: Path) -> ConversionResult:
        source = source.resolve()
        slug = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in source.stem).strip("_") or "document"
        root = self.config.output_dir.resolve() / slug
        asset_dir = root / "assets"; root.mkdir(parents=True, exist_ok=True)
        document = DocumentExtractor().extract(source, asset_dir)
        pending = []
        provider = get_provider(self.config.provider, self.config.api_key, self.config.base_url, self.config.model) if self.config.vision_enabled else None
        for page in document.pages:
            for image in page.images:
                image_path = asset_dir / image.path
                if provider:
                    try:
                        answer = provider.recognize_formula(image_path)
                        if answer.latex:
                            page.formulas.append(Formula(answer.latex, page.number, "vision", answer.confidence))
                            if answer.confidence < 0.9: pending.append({"page": page.number, "image": image.path, "reason": "低置信度公式"})
                    except Exception as exc:
                        pending.append({"page": page.number, "image": image.path, "reason": f"视觉识别失败：{exc}"})
                else:
                    pending.append({"page": page.number, "image": image.path, "reason": "未配置视觉模型"})
        markdown_path = root / f"{slug}-讲义.md"
        markdown_path.write_text(build_lecture(document), encoding="utf-8")
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(document.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        pending_path = None
        if pending:
            pending_path = root / "pending_recognition.json"
            pending_path.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
        return ConversionResult(markdown_path, manifest_path, pending_path)
