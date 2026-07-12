# 隐私与安全

- 将 Key 放入 `.env` 或系统环境变量，不要写入源码。
- 保持 `.gitignore` 中的 `inputs/`、`outputs/`、`work/`、`.env` 条目。
- 提交前执行 `python scripts/secret_scan.py`。
- 公开仓库只使用合成样例，不使用真实学生信息、课件或模型响应。
