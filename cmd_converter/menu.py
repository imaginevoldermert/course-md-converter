from __future__ import annotations

from pathlib import Path

from .job import ConversionConfig, ConversionJob


def interactive_menu() -> int:
    try:
        import questionary
        action = questionary.select("课堂文档转 Markdown", choices=["转换文件", "退出"]).ask()
        if action != "转换文件": return 0
        raw = questionary.text("输入文件或目录路径").ask()
    except ImportError:
        raw = input("输入文件或目录路径（安装 questionary 后可使用方向键菜单）：").strip()
    if not raw: return 0
    result = ConversionJob(ConversionConfig.from_environment(output_dir=Path("outputs"))).convert_path(Path(raw))
    for item in result: print(f"完成：{item.markdown_path}")
    return 0
