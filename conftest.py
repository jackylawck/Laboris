"""
Laboris Root Conftest
確保專案根目錄自動注入 sys.path，解決 CI 與本地測試的模組導入問題。
"""
import sys
from pathlib import Path

# 將專案根目錄加入模組搜尋路徑首位
ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
