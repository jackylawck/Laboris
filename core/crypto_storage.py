"""
Laboris At-Rest Data Encryption Guard
支援多金鑰版本管理與自動輪轉解密（Key Rotation）。
"""
import os
import json
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger("laboris.kernel.crypto")

class StorageEncryptor:
    def __init__(self):
        # 讀取 JSON 格式的多金鑰映射：{"v1": "base64key1...", "v2": "base64key2..."}
        keys_json = os.environ.get("LABORIS_STORAGE_KEYS")
        current_kid = os.environ.get("LABORIS_CURRENT_KEY_ID")

        self.ciphers = {}
        self.current_key_id = current_kid
        self.enabled = False

        if keys_json and current_kid:
            try:
                keys_map = json.loads(keys_json)
                for kid, k_str in keys_map.items():
                    self.ciphers[kid] = Fernet(k_str.encode("utf-8") if isinstance(k_str, str) else k_str)
                if self.current_key_id in self.ciphers:
                    self.enabled = True
                else:
                    logger.warning(f"[INFOSEC WARN] current_key_id '{current_kid}' not in key map.")
            except Exception as e:
                logger.error(f"[INFOSEC ERROR] Failed to initialize key rotation map: {e}")
        else:
            # 單一金鑰向下相容
            single_key = os.environ.get("LABORIS_STORAGE_KEY")
            if single_key:
                try:
                    self.ciphers["v1"] = Fernet(single_key.encode("utf-8") if isinstance(single_key, str) else single_key)
                    self.current_key_id = "v1"
                    self.enabled = True
                except Exception as e:
                    logger.error(f"[INFOSEC ERROR] Invalid LABORIS_STORAGE_KEY: {e}")

        if not self.enabled:
            logger.warning("[INFOSEC WARN] LABORIS_STORAGE_KEY not configured. Storage will be unencrypted.")

    def encrypt(self, raw_bytes: bytes) -> bytes:
        if not self.enabled or not self.current_key_id:
            return raw_bytes
        cipher = self.ciphers[self.current_key_id]
        payload = cipher.encrypt(raw_bytes)
        return self.current_key_id.encode("utf-8") + b":" + payload

    def decrypt(self, encrypted_bytes: bytes) -> bytes:
        if not self.enabled:
            return encrypted_bytes
        if b":" in encrypted_bytes:
            kid_bytes, payload = encrypted_bytes.split(b":", 1)
            kid = kid_bytes.decode("utf-8")
            if kid in self.ciphers:
                return self.ciphers[kid].decrypt(payload)
        # 向下相容嘗試預設金鑰
        if self.current_key_id and self.current_key_id in self.ciphers:
            return self.ciphers[self.current_key_id].decrypt(encrypted_bytes)
        return encrypted_bytes
