# 贡献指南

欢迎提交 Issue 和 Pull Request。

1. 从 `main` 创建分支。
2. 安装依赖后运行 `python -m pytest`。
3. 运行 `python scripts/secret_scan.py`，确认没有密钥、课件或生成结果。
4. 不要提交 `.env`、真实课件、真实转换结果或模型响应日志。
5. 新增格式或模型适配器时，请补充最小测试和文档。
