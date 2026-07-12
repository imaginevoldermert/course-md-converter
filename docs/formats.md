# 支持格式与输出

`pptx` 和 `docx` 直接解析 OOXML；`ppt` 和 `doc` 使用 Windows Office 转换；PDF 优先读取文本层。扫描型 PDF 当前会保留文本提取结果；后续可接入页面渲染后视觉识别。

输出 Markdown、图片资源、逐页 `manifest.json` 和可选的 `pending_recognition.json`。原文件不会被修改。
