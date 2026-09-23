"""
Laboris Statutory Snapshot Store
- 依據 sequence_id 正確歸檔，不依賴時間戳字串。
- 快照與 EvidenceLedger 強制綁定。
"""
import os
import gzip
import time
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.crypto_audit import compute_sha256_bytes
from core.evidence_ledger import EvidenceLedger
from core.crypto_storage import StorageEncryptor

class SnapshotStore:
    def __init__(self, base_dir: str = "data/snapshots", ledger: EvidenceLedger | None = None):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_dir / "snapshot_index.jsonl"
        self.ledger = ledger or EvidenceLedger()
        self.encryptor = StorageEncryptor()
        self._latest_cache: Dict[str, Dict[str, Any]] = {}
        self._source_history: Dict[str, List[Dict[str, Any]]] = {}
        self._init_cache()

    def _init_cache(self):
        if not self.index_path.exists():
            return
        with open(self.index_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                meta = json.loads(line)
                sid = meta["source_id"]
                self._latest_cache[sid] = meta
                if sid not in self._source_history:
                    self._source_history[sid] = []
                self._source_history[sid].append(meta)

    def save_snapshot(
        self,
        source_id: str,
        content: bytes,
        ext: str = "bin",
        evidence_level: str = "raw_snapshot"
    ) -> Dict[str, Any]:
        latest_meta = self._latest_cache.get(source_id)
        if latest_meta and latest_meta["sha256"] == compute_sha256_bytes(content):
            return {"status": "SKIPPED_DUPLICATE", "sha256": latest_meta["sha256"]}

        source_dir = self.base_dir / source_id
        source_dir.mkdir(parents=True, exist_ok=True)

        now = int(time.time())
        sha256 = compute_sha256_bytes(content)

        evidence_block = self.ledger.append_evidence(
            source_id=source_id,
            evidence_level=evidence_level,
            raw_content=content,
            is_mock=False
        )

        seq_id = evidence_block.sequence_id
        filename = f"{seq_id:08d}_{now}_{sha256[:12]}.{ext}.gz"
        file_path = source_dir / filename

        # 認證加密保護
        stored_bytes = self.encryptor.encrypt(content)
        with gzip.open(file_path, "wb") as gz:
            gz.write(stored_bytes)

        snapshot_meta = {
            "schema_version": "2.0.0",
            "source_id": source_id,
            "sequence_id": seq_id,
            "timestamp": now,
            "filename": filename,
            "sha256": sha256,
            "byte_size": len(content),
            "ext": ext,
            "archived": False,
            "evidence_chain_hash": evidence_block.chain_hash,
            "evidence_sequence_id": seq_id
        }

        with open(self.index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot_meta, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

        self._latest_cache[source_id] = snapshot_meta
        if source_id not in self._source_history:
            self._source_history[source_id] = []
        self._source_history[source_id].append(snapshot_meta)

        active_snapshots = [s for s in self._source_history[source_id] if not s["archived"]]
        if len(active_snapshots) > 100:
            active_snapshots.sort(key=lambda s: s["sequence_id"])
            oldest = active_snapshots[0]
            self._archive_specific_snapshot(source_id, oldest)

        return {"status": "COMMITTED", "meta": snapshot_meta}

    def _archive_specific_snapshot(self, source_id: str, meta: Dict[str, Any]):
        source_dir = self.base_dir / source_id
        archive_dir = source_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        target_file = source_dir / meta["filename"]
        if target_file.exists():
            shutil.move(str(target_file), str(archive_dir / meta["filename"]))
            meta["archived"] = True

    def get_latest_snapshot(self, source_id: str) -> Optional[bytes]:
        meta = self._latest_cache.get(source_id)
        if not meta:
            return None

        file_path = self.base_dir / source_id / meta["filename"]
        if not file_path.exists():
            file_path = self.base_dir / source_id / "archive" / meta["filename"]
            if not file_path.exists():
                return None

        with gzip.open(file_path, "rb") as gz:
            raw = gz.read()
            return self.encryptor.decrypt(raw)

    def list_history(self, source_id: str) -> List[Dict[str, Any]]:
        return self._source_history.get(source_id, [])
