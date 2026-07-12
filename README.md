# 课堂文档转 Markdown

将 Word、PowerPoint、PDF 课堂资料转换为可复习的 Markdown 讲义，并尽量识别为 LaTeX 数学公式。

> 本项目仅在本机 `127.0.0.1` 启动网页界面。你的课件和 API Key 不会被上传到本项目仓库。

## 功能

- 支持 `.doc/.docx/.ppt/.pptx/.pdf`；旧式 `.doc/.ppt` 在 Windows 上通过已安装的 Office 转换。
- 提取标题、正文、表格、备注中的文本、图片与 Office 原生公式。
- 对图片公式使用可插拔视觉模型：OpenAI-compatible、Gemini、Claude；提供 DeepSeek V4 的文本处理选项。
- 无 API Key 也能生成本地提取结果，并输出 `pending_recognition.json` 供后续补识别。
- Streamlit 网页预览可实时渲染 LaTeX；交互式终端可通过方向键选择任务。

## 安装

```powershell
git clone https://github.com/<你的用户名>/course-md-converter.git
cd course-md-converter
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`，填写自己的模型设置。`.env` 已被 Git 忽略，**绝不要提交或截图其中的 Key**。

```ini
CMD_PROVIDER=openai_compatible
CMD_MODEL=your-vision-model
CMD_BASE_URL=https://your-compatible-api.example/v1
CMD_API_KEY=your-secret-key
```

### DeepSeek V4

网页中直接选择 `deepseek`，再选择 `deepseek-v4-pro`（质量优先）或 `deepseek-v4-flash`（速度与成本优先）。接口会自动填为 `https://api.deepseek.com`。也可以在 `.env` 中设置：

```ini
CMD_PROVIDER=deepseek
CMD_MODEL=deepseek-v4-pro
CMD_BASE_URL=https://api.deepseek.com
CMD_API_KEY=你的DeepSeek_API_Key
```

DeepSeek V4 是文本模型，因此本项目会自动关闭图片公式识别；文字、表格及 Office 原生公式的本地提取仍会正常执行。

网页与终端菜单都提供“仅本次运行使用”的 API Key 密码输入框，无需先创建 `.env`。该 Key 只在内存中传给当前转换任务，不会写入 Markdown、输出文件或项目配置。

## 使用

### 网页预览

```powershell
streamlit run app.py --server.address 127.0.0.1
```

浏览器会打开本地页面。选择文件后点击“开始转换”，即可查看渲染后的公式、原始 Markdown 和下载结果。

### VS Code 终端菜单

在 VS Code 的“运行和调试”中选择“启动交互式终端”，或执行：

```powershell
python main.py menu
```

### 命令行

```powershell
python main.py convert "D:\课件\示例.pptx" --output outputs
python main.py convert "D:\课件文件夹" --provider openai_compatible --model your-model
```

## 输出结构

```text
outputs/
  文档名/
    文档名-讲义.md
    manifest.json
    pending_recognition.json   # 无 Key、失败或低置信度时生成
    assets/
      page001_img01.png
```

`manifest.json` 保留逐页结构；Markdown 中通过注释保留原页映射。公式采用 `$...$` 或 `$$...$$`。

## 公式识别说明

1. 先读取 Office 的原生数学节点。
2. 对正文内明显数学表达式做安全的 LaTeX 符号规范化。
3. 对图片调用视觉模型；模型失败、未配置 Key 或置信度不足时不伪造结果，而是写入待复核清单。

建议重点复核矩阵、分式、上下标、求和符号与小字脚注。

## 隐私与安全

- 不提交课件、转换结果、日志、缓存、本地配置或 `.env`。
- 运行 `python scripts/secret_scan.py` 后再提交代码。
- 请使用环境变量或本地 `.env` 管理 Key；若误传 Key，应立即在服务商控制台撤销并重建。

更多说明见 [docs](docs/)。
