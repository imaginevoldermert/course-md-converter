"""课堂文档转 Markdown 命令行入口。"""
from __future__ import annotations

import argparse
from pathlib import Path

from cmd_converter.job import ConversionConfig, ConversionJob
from cmd_converter.menu import interactive_menu
from cmd_converter.defaults import DEFAULT_OUTPUT_DIR


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="将 Word、PPT、PDF 转为带公式的 Markdown 讲义")
    sub = p.add_subparsers(dest="command", required=True)
    convert = sub.add_parser("convert", help="转换一个文件或目录")
    convert.add_argument("input", type=Path)
    convert.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    convert.add_argument("--provider", default="openai_compatible", choices=["openai_compatible", "deepseek", "gemini", "claude"])
    convert.add_argument("--model", default=None)
    convert.add_argument("--base-url", default=None)
    convert.add_argument("--api-key", default=None)
    convert.add_argument("--no-vision", action="store_true", help="不调用视觉模型")
    sub.add_parser("menu", help="启动交互式终端菜单")
    return p


def main() -> int:
    args = parser().parse_args()
    if args.command == "menu":
        return interactive_menu()
    config = ConversionConfig.from_environment(
        output_dir=args.output,
        provider=args.provider,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        vision_enabled=not args.no_vision,
    )
    results = ConversionJob(config).convert_path(args.input)
    for result in results:
        print(f"完成: {result.markdown_path}")
        if result.pending_path:
            print(f"待识别项目: {result.pending_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
