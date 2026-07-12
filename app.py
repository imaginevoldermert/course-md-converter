"""仅监听本机的 Streamlit 预览界面。"""
from __future__ import annotations

import uuid
from pathlib import Path

import streamlit as st

from cmd_converter.job import ConversionConfig, ConversionJob

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

if uploaded and st.button("开始转换", type="primary"):
    work = Path.cwd() / "work"
    work.mkdir(exist_ok=True)
    upload_dir = work / f"cmd_upload_{uuid.uuid4().hex[:12]}"
    upload_dir.mkdir()
    staging = upload_dir / uploaded.name
    staging.write_bytes(uploaded.getvalue())
    config = ConversionConfig.from_environment(
        output_dir=Path("outputs"), provider=provider, model=model or None,
        base_url=base_url or None, api_key=api_key or None, vision_enabled=use_vision,
    )
    with st.spinner("正在提取课堂内容…"):
        result = ConversionJob(config).convert_file(staging)
    st.session_state["result"] = result

result = st.session_state.get("result")
if result:
    st.success(f"已生成：{result.markdown_path.name}")
    markdown = result.markdown_path.read_text(encoding="utf-8")
    preview, source = st.tabs(["渲染预览", "Markdown 源码"])
    with preview:
        st.markdown(markdown)
    with source:
        st.code(markdown, language="markdown")
    st.download_button("下载 Markdown", markdown, file_name=result.markdown_path.name, mime="text/markdown")
    if result.pending_path:
        st.warning(f"存在待复核内容：{result.pending_path.name}")
else:
    st.info("从左侧选择文件并开始转换。未配置 API Key 时仍会完成本地提取。")
