from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VisionResponse:
    latex: str
    confidence: float


class VisionProvider:
    def recognize_formula(self, image: Path) -> VisionResponse:
        raise NotImplementedError


class OpenAICompatibleProvider(VisionProvider):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key, self.base_url, self.model = api_key, base_url.rstrip("/"), model

    def recognize_formula(self, image: Path) -> VisionResponse:
        import requests
        payload = base64.b64encode(image.read_bytes()).decode("ascii")
        prompt = "识别图中的数学公式。只返回可直接使用的 LaTeX，不要解释；若不是公式，返回 NONE。"
        response = requests.post(
            f"{self.base_url}/chat/completions", timeout=90,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "temperature": 0,
                  "messages": [{"role": "user", "content": [
                      {"type": "text", "text": prompt},
                      {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{payload}"}},
                  ]}]},
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        return VisionResponse("" if text.upper() == "NONE" else text.strip("`$ \n"), 0.8)


class GeminiProvider(VisionProvider):
    """Gemini REST 适配器；密钥从 CMD_API_KEY 读取。"""
    def __init__(self, api_key: str, model: str): self.api_key, self.model = api_key, model
    def recognize_formula(self, image: Path) -> VisionResponse:
        import requests
        data = base64.b64encode(image.read_bytes()).decode("ascii")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {"contents": [{"parts": [{"text": "仅返回图中数学公式的 LaTeX；非公式返回 NONE。"}, {"inline_data": {"mime_type": "image/png", "data": data}}]}]}
        r = requests.post(url, json=body, timeout=90); r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return VisionResponse("" if text.upper() == "NONE" else text.strip("`$ \n"), 0.8)


class ClaudeProvider(VisionProvider):
    """Anthropic Messages API 适配器。"""
    def __init__(self, api_key: str, model: str): self.api_key, self.model = api_key, model
    def recognize_formula(self, image: Path) -> VisionResponse:
        import requests
        data = base64.b64encode(image.read_bytes()).decode("ascii")
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=90,
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": self.model, "max_tokens": 300, "messages": [{"role": "user", "content": [
                {"type": "text", "text": "仅返回图中数学公式的 LaTeX；非公式返回 NONE。"},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}},
            ]}]})
        r.raise_for_status(); text = r.json()["content"][0]["text"].strip()
        return VisionResponse("" if text.upper() == "NONE" else text.strip("`$ \n"), 0.8)


def get_provider(name: str, api_key: str | None, base_url: str | None, model: str | None) -> VisionProvider | None:
    # DeepSeek V4 is text-only. Returning None makes the conversion job retain
    # image formulas in pending_recognition.json instead of issuing invalid
    # image_url requests to a text-only API.
    if name == "deepseek":
        return None
    if not api_key:
        return None
    if name == "openai_compatible":
        return OpenAICompatibleProvider(api_key, base_url or "https://api.openai.com/v1", model or "gpt-4.1-mini")
    if name == "gemini": return GeminiProvider(api_key, model or "gemini-2.0-flash")
    if name == "claude": return ClaudeProvider(api_key, model or "claude-sonnet-4-20250514")
    raise ValueError(f"未知模型提供方: {name}")
