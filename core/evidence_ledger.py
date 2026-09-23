"""
Laboris Append-Only Cryptographic Evidence Ledger
落實真·os.fsync() 落盤與 sidecar head O(1) 啟動。
"""
from dataclasses import dataclass, asdict
from typing import Optional
import os
import time
import hashlib
import json
from pathlib import Path
from core.crypto_audit import compute_sha256_bytes
from core.atomic_writer import atomic_write

@dataclass(frozen=True)
class EvidenceBlock:
    sequence_id: int
    source_id: str
    evidence_level: str
    content_sha256: str
    timestamp_utc: float
    parent_block_hash: str
    chain_hash: str
    is_mock: bool

class EvidenceLedger:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, ledger_storage_path: str = "data/evidence_ledger.jsonl"):
        self.storage_path = Path(ledger_storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.head_path = self.storage_path.with_suffix(".head.json")
        self.last_block: Optional[EvidenceBlock] = None
        self.block_count: int = 0
        self._init_head_o1()

    def _init_head_o1(self):
        if not self.storage_path.exists():
            return

        if self.head_path.exists():
            try:
                with open(self.head_path, "r", encoding="utf-8") as hf:
                    head_data = json.load(hf)
                    self.last_block = EvidenceBlock(**head_data["last_block"])
                    self.block_count = head_data["block_count"]
                    return
            except (json.JSONDecodeError, KeyError):
                pass

        self._rebuild_head_from_storage()

    def _rebuild_head_from_storage(self):
        self.last_block = None
        self.block_count = 0
        if not self.storage_path.exists():
            return

        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    raw = json.loads(line_str)
                    self.last_block = EvidenceBlock(**raw)
                    self.block_count += 1
        
        self._persist_head()

    def _persist_head(self):
        if self.last_block is None:
            return
        payload = {
            "block_count": self.block_count,
            "last_block": asdict(self.last_block)
        }
        atomic_write(self.head_path, json.dumps(payload, ensure_ascii=False, indent=2))

    def append_evidence(
        self,
        source_id: str,
        evidence_level: str,
        raw_content: bytes,
        is_mock: bool = False
    ) -> EvidenceBlock:
        content_hash = compute_sha256_bytes(raw_content)
        parent_hash = self.last_block.chain_hash if self.last_block else self.GENESIS_HASH
        seq_id = self.block_count + 1
        now = time.time()

        chain_seed = f"{seq_id}:{source_id}:{content_hash}:{parent_hash}:{now}"
        block_chain_hash = hashlib.sha256(chain_seed.encode("utf-8")).hexdigest()

        new_block = EvidenceBlock(
            sequence_id=seq_id,
            source_id=source_id,
            evidence_level=evidence_level,
            content_sha256=content_hash,
            timestamp_utc=now,
            parent_block_hash=parent_hash,
            chain_hash=block_chain_hash,
            is_mock=is_mock
        )

        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(new_block), ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

        self.last_block = new_block
        self.block_count += 1
        self._persist_head()
        return new_block

    def verify_integrity(self) -> bool:
        if not self.storage_path.exists():
            return True

        expected_parent = self.GENESIS_HASH
        expected_seq = 1

        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                block = EvidenceBlock(**json.loads(line))
                if block.sequence_id != expected_seq:
                    return False
                if block.parent_block_hash != expected_parent:
                    return False

                seed = f"{block.sequence_id}:{block.source_id}:{block.content_sha256}:{block.parent_block_hash}:{block.timestamp_utc}"
                calculated = hashlib.sha256(seed.encode("utf-8")).hexdigest()
                if block.chain_hash != calculated:
                    return False

                expected_parent = block.chain_hash
                expected_seq += 1

        return True
