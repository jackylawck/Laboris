import os
import tempfile
from pathlib import Path

def atomic_write(filepath: str | Path, content: str, encoding: str = "utf-8") -> None:
    """原子化寫入檔案，含嚴格的異常清理，避免臨時檔案洩漏。"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    tf = tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding=encoding)
    temp_name = tf.name
    try:
        tf.write(content)
        tf.flush()
        os.fsync(tf.fileno())
        tf.close()
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise
