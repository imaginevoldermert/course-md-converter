"""轻量规则：保留原生公式，规范常见文本数学符号。"""
from __future__ import annotations

import re


def omml_text_to_latex(text: str) -> str:
    """OMML 完整转换需要 Office XSLT；这里安全保留可读 token 并规范字符。"""
    text = re.sub(r"\s+", " ", text).strip()
    return (text.replace("×", r"\\times ").replace("÷", r"\\div ")
                .replace("≤", r"\\le ").replace("≥", r"\\ge ")
                .replace("∑", r"\\sum ").replace("√", r"\\sqrt{}"))


def looks_like_formula(text: str) -> bool:
    return bool(re.search(r"(?:[=≠≤≥∑∏√]|\b(?:sin|cos|log|exp|CR|CI)\b).{0,80}[0-9A-Za-z]", text))


def inline_formula_markdown(text: str) -> str:
    """仅包装整行明显公式，避免破坏普通中文句子。"""
    stripped = text.strip()
    if looks_like_formula(stripped) and len(stripped) <= 160:
        return f"$$\n{omml_text_to_latex(stripped)}\n$$"
    return text
