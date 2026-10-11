"""pytest 全局配置

必须在任何 `src.*` 被 import 之前完成两件事：
1. 把仓库根加进 sys.path（否则 `import src.utils...` 失败）
2. 把可写目录重定向到临时沙箱 —— `src.utils.application` 在 import 期就会
   创建 data/ log/ models/ 并被 config.log 打开真实日志文件，
   不隔离的话跑一次 pytest 就会读写开发者真实的用户数据。
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent

sys.path.insert(0, str(_REPO_ROOT))

# 固定值而不是 tmp_path：application 在 import 期读环境变量，
# 而 session 级 fixture 要到 pytest_configure 之后才可用
_SANDBOX = Path(tempfile.gettempdir()) / "OnmyojiDesktopAssistant-tests"
_SANDBOX.mkdir(parents=True, exist_ok=True)
os.environ["ODAGUI_DATA_ROOT"] = str(_SANDBOX)
