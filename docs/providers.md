# 模型与公式识别

通过 `.env` 选择 `openai_compatible`、`gemini` 或 `claude`。OpenAI-compatible 需要 `/v1` 风格的 Chat Completions 图像输入接口。

适配器只接收图片字节与“仅返回 LaTeX”的任务提示；API Key 只从环境变量或 `.env` 读取，绝不写入 `manifest.json`、日志或 Markdown。
