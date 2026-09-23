"""
Laboris Statutory Generic Adapter (Idempotent Pipeline)
結合 Hash 防重、Snapshot-Ledger 綁定與 Selector 失效斷路。
"""
from typing import Dict, Any
from dataclasses import dataclass
import logging
from core.crypto_audit import compute_sha256_bytes
from core.snapshot_store import SnapshotStore
from core.diff.web_diff import semantic_html_diff
from core.parsers.pdf_parser import parse_pdf_layout_aware

logger = logging.getLogger("laboris.kernel.adapter")

@dataclass(frozen=True)
class IngestionPayload:
    source_id: str
    evidence_level: str
    sha256_fingerprint: str
    is_mock: bool
    normalized_data: Dict[str, Any]
    has_changed: bool
    is_duplicate: bool = False

class GenericStatutoryAdapter:
    def __init__(self, source_id: str, config: Dict[str, Any], snapshot_store: SnapshotStore | None = None):
        self.source_id = source_id
        self.config = config
        self.snapshot_store = snapshot_store or SnapshotStore()

    def execute_ingestion(self, simulated_stream: bytes | None = None) -> IngestionPayload:
        is_mock = self.config.get("is_mock", False)

        if is_mock or simulated_stream is not None:
            raw_bytes = simulated_stream or b"%PDF-1.5 Mock Statutory Document"
        else:
            import urllib.request
            url = f"{self.config['base_url']}{self.config.get('endpoint', '')}"
            req = urllib.request.Request(url, headers={"User-Agent": "Laboris-Auditor/4.0"})
            # nosec B310: Audit sandbox controlled URL fetch
            with urllib.request.urlopen(req, timeout=self.config.get("timeout_sec", 15)) as resp:  # nosec B310
                raw_bytes = resp.read()

        current_hash = compute_sha256_bytes(raw_bytes)
        previous_bytes = self.snapshot_store.get_latest_snapshot(self.source_id)

        # 冪等性檢查：若最新快照 Hash 完全一致，直接跳過重入
        if previous_bytes and compute_sha256_bytes(previous_bytes) == current_hash:
            return IngestionPayload(
                source_id=self.source_id,
                evidence_level=self.config.get("evidence_level", "statutory"),
                sha256_fingerprint=current_hash,
                is_mock=is_mock,
                normalized_data={"status": "IDEMPOTENT_SKIPPED"},
                has_changed=False,
                is_duplicate=True
            )

        parser_type = self.config.get("parser")
        has_substantive_delta = True
        normalized = {}

        if parser_type == "html_semantic":
            diff_res = semantic_html_diff(previous_bytes, raw_bytes, self.config)
            has_substantive_delta = diff_res.has_substantive_change
            normalized = {
                "diff_summary": diff_res.diff_summary,
                "change_ratio": diff_res.change_ratio,
                "error": diff_res.error
            }
        elif parser_type == "pdf_layout_aware":
            normalized = parse_pdf_layout_aware(raw_bytes, self.config)
            has_substantive_delta = True

        # 只有在真正檢測到實質法規異動且無致命解析錯誤時，才寫入快照與證據鏈
        if has_substantive_delta and not normalized.get("error"):
            ext = "pdf" if parser_type == "pdf_layout_aware" else "html"
            self.snapshot_store.save_snapshot(
                source_id=self.source_id,
                content=raw_bytes,
                ext=ext,
                evidence_level=self.config.get("evidence_level", "statutory")
            )

        return IngestionPayload(
            source_id=self.source_id,
            evidence_level=self.config.get("evidence_level", "statutory"),
            sha256_fingerprint=current_hash,
            is_mock=is_mock,
            normalized_data=normalized,
            has_changed=has_substantive_delta,
            is_duplicate=False
        )
