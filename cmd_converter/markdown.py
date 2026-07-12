from __future__ import annotations

from .formulas import inline_formula_markdown
from .models import Document


def build_lecture(document: Document) -> str:
    lines = [f"# {document.pages[0].title if document.pages else '课堂讲义'}", "", "> 自动生成。带“待复核”的内容建议回看原始页确认。", ""]
    for page in document.pages:
        heading = page.title or f"第 {page.number} 页"
        lines += [f"## {heading}", f"<!-- 来源：第 {page.number} 页 -->", ""]
        seen = set()
        for text in page.text:
            if text not in seen:
                lines += [inline_formula_markdown(text), ""]
                seen.add(text)
        for formula in page.formulas:
            lines += ["$$", formula.latex, "$$", ""]
        for table in page.tables:
            if table:
                headers = table[0]
                lines += ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
                lines += ["| " + " | ".join(row) + " |" for row in table[1:]] + [""]
        for image in page.images:
            lines += [f"![第 {page.number} 页图片](assets/{image.path})", ""]
    return "\n".join(lines).rstrip() + "\n"
