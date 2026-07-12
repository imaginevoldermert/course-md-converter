"""仅监听本机的 Streamlit 预览界面。"""
from __future__ import annotations

import os
import uuid
import traceback
from pathlib import Path

import streamlit as st

from cmd_converter.job import ConversionConfig, ConversionJob
from cmd_converter.result_files import build_result_zip, list_result_files
from cmd_converter.defaults import DEFAULT_OUTPUT_DIR

st.set_page_config(page_title="课堂文档转 Markdown", layout="wide")
st.title("课堂文档转 Markdown")
st.caption("本地运行：Word、PPT、PDF → 讲义 Markdown + LaTeX 公式")

with st.sidebar:
    provider = st.selectbox("模型提供方", ["openai_compatible", "deepseek", "gemini", "claude"])
    if provider == "deepseek":
        model = st.selectbox("DeepSeek 模型", ["deepseek-v4-pro", "deepseek-v4-flash"])
        base_url = "https://api.deepseek.com"
        st.text_input("接口地址", value=base_url, disabled=True)
        st.info("DeepSeek V4 目前是文本模型；本工具会保留本地公式提取，但不会把图片发送给 DeepSeek。")
        use_vision = st.checkbox("调用视觉模型识别图片公式", value=False, disabled=True)
    else:
        model = st.text_input("模型名（留空则读取 .env）")
        base_url = st.text_input("接口地址（OpenAI-compatible 可用）")
        use_vision = st.checkbox("调用视觉模型识别图片公式", value=True)
    api_key = st.text_input("API Key（仅本次运行使用）", type="password", help="不会写入 Markdown、输出文件或项目配置。")
    uploaded = st.file_uploader("选择 Word、PPT 或 PDF", type=["doc", "docx", "ppt", "pptx", "pdf"])
    output_presets = {
        "默认输出目录": DEFAULT_OUTPUT_DIR,
        "项目 outputs": (Path.cwd() / "outputs").resolve(),
        "桌面": Path.home() / "Desktop" / "course-md-converter",
        "文档": Path.home() / "Documents" / "course-md-converter",
        "下载": Path.home() / "Downloads" / "course-md-converter",
    }
    output_choice = st.selectbox("输出位置", [*output_presets, "自定义路径"])
    if output_choice == "自定义路径":
        output_text = st.text_input("自定义输出文件夹", value=str(DEFAULT_OUTPUT_DIR))
    else:
        output_text = st.text_input("输出文件夹", value=str(output_presets[output_choice]), disabled=True)

if uploaded and st.button("开始转换", type="primary"):
    try:
        work = Path.cwd() / "work"
        work.mkdir(exist_ok=True)
        upload_dir = work / f"cmd_upload_{uuid.uuid4().hex[:12]}"
        upload_dir.mkdir()
        staging = upload_dir / uploaded.name
        staging.write_bytes(uploaded.getvalue())
        output_dir = Path(output_text).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        config = ConversionConfig.from_environment(
            output_dir=output_dir, provider=provider, model=model or None,
            base_url=base_url or None, api_key=api_key or None, vision_enabled=use_vision,
        )
        with st.spinner("正在提取课堂内容…"):
            result = ConversionJob(config).convert_file(staging)
        st.session_state["result"] = result
        st.session_state.pop("conversion_error", None)
    except Exception as exc:
        work.mkdir(exist_ok=True)
        (work / "last_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        st.session_state["conversion_error"] = str(exc)

if st.session_state.get("conversion_error"):
    st.error(f"转换失败：{st.session_state['conversion_error']}")
    st.caption("界面仍会保持运行。详细信息已保存到 work/last_error.log。")

result = st.session_state.get("result")
if result:
    st.success(f"已生成：{result.markdown_path.name}")
    result_dir = result.markdown_path.parent.resolve()
    st.subheader("输出文件夹")
    st.code(str(result_dir), language=None)
    open_col, refresh_col = st.columns(2)
    with open_col:
        if st.button("在资源管理器中打开输出文件夹"):
            try:
                os.startfile(result_dir)  # type: ignore[attr-defined]
                st.toast("已打开输出文件夹")
            except Exception as exc:
                st.error(f"无法打开文件夹：{exc}")
    with refresh_col:
        st.caption("以下清单来自该文件夹，包含 Markdown、图片、清单和待复核项。")
    inventory = list_result_files(result_dir)
    st.dataframe(inventory, use_container_width=True, hide_index=True)
    markdown = result.markdown_path.read_text(encoding="utf-8")
    # Rendering a 100+ page Markdown document at once can exhaust the embedded
    # browser and close its tab. Preview one section at a time while keeping the
    # complete document available for download.
    raw_sections = markdown.split("\n## ")
    sections = [raw_sections[0]] + ["## " + section for section in raw_sections[1:]]
    selected = st.number_input("预览章节", min_value=1, max_value=len(sections), value=1, step=1)
    visible_markdown = sections[int(selected) - 1]
    preview, source = st.tabs(["分段渲染预览", "当前章节源码"])
    with preview:
        st.markdown(visible_markdown)
    with source:
        st.code(visible_markdown, language="markdown")
    md_col, zip_col = st.columns(2)
    with md_col:
        st.download_button("下载 Markdown", markdown, file_name=result.markdown_path.name, mime="text/markdown")
    with zip_col:
        st.download_button(
            "下载完整结果 ZIP",
            build_result_zip(result_dir),
            file_name=f"{result_dir.name}-完整结果.zip",
            mime="application/zip",
        )
    if result.pending_path:
        st.warning(f"存在待复核内容：{result.pending_path.name}")
        st.download_button(
            "下载待复核清单",
            result.pending_path.read_bytes(),
            file_name=result.pending_path.name,
            mime="application/json",
        )
else:
    st.info("从左侧选择文件并开始转换。未配置 API Key 时仍会完成本地提取。")
