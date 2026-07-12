"""提交前的轻量密钥扫描，不向网络发送任何内容。"""
from __future__ import annotations

import re
import subprocess
import sys

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
    # Assignment checks are deliberately conservative: provider/config variable
    # names such as `api_key = "openai_compatible"` are not credentials.
    re.compile(r"(?:api[_-]?key|token)\s*[=:]\s*['\"](?=[^'\"]{20,}['\"])(?=[^'\"]*[0-9_-])[^'\"]+", re.I),
]

result = subprocess.run(["git", "diff", "--cached", "--", "."], capture_output=True)
# Git diffs can contain Chinese course-related documentation; decode explicitly
# instead of relying on the Windows console code page.
text = result.stdout.decode("utf-8", errors="replace")
hits = [pattern.pattern for pattern in PATTERNS if pattern.search(text)]
if hits:
    print("检测到疑似密钥，已阻止提交：", ", ".join(hits), file=sys.stderr)
    raise SystemExit(1)
print("密钥扫描通过：暂存区未发现常见 API Key 模式。")
