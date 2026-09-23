"""
Laboris Access Logger (Lazy Initialization)
修復模組載入時建立目錄之副作用，支援日誌輪轉。
"""
import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_security_logger = None

def get_security_logger():
    global _security_logger
    if _security_logger is not None:
        return _security_logger

    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("laboris.security.audit")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "security_access.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        formatter = logging.Formatter('{"timestamp": "%(asctime)s", "event": %(message)s}')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _security_logger = logger
    return _security_logger

def log_security_event(action: str, resource: str, actor: str = "SYSTEM_USER", status: str = "SUCCESS", details: dict = None):
    payload = {
        "actor": actor,
        "action": action,
        "resource": resource,
        "status": status,
        "details": details or {},
        "timestamp_utc": time.time(),
        "pid": os.getpid()
    }
    logger = get_security_logger()
    logger.info(json.dumps(payload, ensure_ascii=False))
