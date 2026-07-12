# Windows 旧格式转换

处理 `.ppt` 或 `.doc` 需要本机安装 Microsoft PowerPoint 或 Word。转换器会先把源文件复制到临时 ASCII 文件名，再通过 `cscript.exe` 调用 Office COM 导出 `.pptx/.docx`，以减少中文路径导致的兼容问题。

如转换失败，请在 Office 中手动另存为 `.pptx/.docx` 后重试。
