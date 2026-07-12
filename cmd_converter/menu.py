from __future__ import annotations

from getpass import getpass
from pathlib import Path
import traceback

from .job import ConversionConfig, ConversionJob
from .defaults import DEFAULT_OUTPUT_DIR


def interactive_menu() -> int:
    provider, model, base_url, api_key = "openai_compatible", None, None, None
    output_dir = DEFAULT_OUTPUT_DIR
    try:
        import questionary
        action = questionary.select("课堂文档转 Markdown", choices=["转换文件", "退出"]).ask()
        if action != "转换文件": return 0
        raw = questionary.text("输入文件或目录路径").ask()
        output_raw = questionary.path("输出文件夹", default=str(DEFAULT_OUTPUT_DIR)).ask()
        output_dir = Path(output_raw or DEFAULT_OUTPUT_DIR).expanduser()
        provider = questionary.select("模型提供方", choices=["openai_compatible", "deepseek", "gemini", "claude"]).ask()
        if provider == "deepseek":
            model = questionary.select("DeepSeek 模型", choices=["deepseek-v4-pro", "deepseek-v4-flash"]).ask()
            base_url = "https://api.deepseek.com"
            print("DeepSeek 为文本模型：图片公式识别已关闭，本地提取仍会执行。")
        else:
            model = questionary.text("模型名（可留空）").ask() or None
            base_url = questionary.text("接口地址（可留空）").ask() or None
        api_key = questionary.password("API Key（仅本次运行使用，可留空）").ask() or None
    except ImportError:
        raw = input("输入文件或目录路径（安装 questionary 后可使用方向键菜单）：").strip()
        output_raw = input(f"输出文件夹 [{DEFAULT_OUTPUT_DIR}]：").strip()
        output_dir = Path(output_raw or DEFAULT_OUTPUT_DIR).expanduser()
        provider = input("模型提供方 [openai_compatible/deepseek/gemini/claude]：").strip() or provider
        if provider == "deepseek":
            model = input("DeepSeek 模型 [deepseek-v4-pro]：").strip() or "deepseek-v4-pro"
            base_url = "https://api.deepseek.com"
            print("DeepSeek 为文本模型：图片公式识别已关闭，本地提取仍会执行。")
        else:
            model = input("模型名（可留空）：").strip() or None
            base_url = input("接口地址（可留空）：").strip() or None
        api_key = getpass("API Key（仅本次运行使用，可留空）：") or None
    if not raw: return 0
    input_path = Path(raw.strip().strip('"').strip("'"))
    if not input_path.exists():
        print(f"文件或目录不存在：{input_path}")
        return 1
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        result = ConversionJob(ConversionConfig.from_environment(
            output_dir=output_dir, provider=provider, model=model,
            base_url=base_url, api_key=api_key, vision_enabled=provider != "deepseek",
        )).convert_path(input_path)
    except Exception as exc:
        work = Path("work")
        work.mkdir(exist_ok=True)
        (work / "last_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        print(f"转换失败：{exc}")
        print("终端不会退出；详细信息已保存到 work/last_error.log。")
        return 1
    for item in result: print(f"完成：{item.markdown_path}")
    return 0
