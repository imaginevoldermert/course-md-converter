# 故障排查

**没有公式识别结果**：检查 `CMD_API_KEY`、模型名及接口地址；无 Key 时会生成待识别清单。

**旧 PPT 转换失败**：确认 PowerPoint 已安装，或在 Office 中手动另存为 `.pptx`。

**网页不能启动**：执行 `pip install -r requirements.txt`，然后使用 `streamlit run app.py --server.address 127.0.0.1`。
