import pytest
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from core.parsers.pdf_parser import parse_pdf_layout_aware, extract_comprehensive_anchors
from core.diff.web_diff import semantic_html_diff
from core.snapshot_store import SnapshotStore
from core.evidence_ledger import EvidenceLedger

@pytest.fixture
def dual_column_pdf_stream() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # 左欄 (X: 50 ~ 250)
    c.drawString(50, height - 100, "第 57 章《僱傭條例》檢討報告")
    c.drawString(50, height - 120, "第 4 條(1) 連續受僱規定評估")
    c.drawString(50, height - 140, "附表 1 擬議修訂方案 A")

    # 右欄 (X: 350 ~ 550)
    c.drawString(350, height - 100, "Section 4 Statutory Benefits")
    c.drawString(350, height - 120, "Paragraph 3.2 Financial Impact")
    c.drawString(350, height - 140, "預期寬限期為 180 天")

    c.save()
    buf.seek(0)
    return buf.read()

def test_pdf_dual_column_absolute_geometry_parsing(dual_column_pdf_stream):
    res = parse_pdf_layout_aware(dual_column_pdf_stream)
    assert res["valid_pdf_format"] is True
    page = res["pages"][0]
    assert page["is_multi_column"] is True
    tokens = [c["anchor_token"] for c in page["citations"]]
    assert "第 57 章" in tokens
    assert "第 4 條(1)" in tokens
    assert "Section 4" in tokens

def test_chapter_pattern_statutory_short_circuit_in_large_document():
    blocks = [f"<p>這是日常營運事務常規指引說明段落編號 {i}。</p>" for i in range(400)]
    old_html = f"<html><body><div id='content'>{''.join(blocks)}<p>請遵照第 57 章規定辦理。</p></div></body></html>".encode("utf-8")
    new_html = f"<html><body><div id='content'>{''.join(blocks)}<p>請遵照第 58 章規定辦理。</p></div></body></html>".encode("utf-8")

    res = semantic_html_diff(old_html, new_html, {
        "css_selector": "#content",
        "min_change_ratio": 0.05,
        "min_absolute_blocks": 5
    })
    assert res.has_substantive_change is True
    assert res.has_critical_statutory_delta is True

def test_old_html_selector_failure_forces_substantive_change():
    # 修正：避免使用 b"..." 包裹非 ASCII 中文字元，改用 .encode("utf-8")
    old_html = "<html><body><div id='deprecated-id'>舊版公告</div></body></html>".encode("utf-8")
    new_html = "<html><body><div id='active-content'><p>新版公告</p></div></body></html>".encode("utf-8")

    res = semantic_html_diff(old_html, new_html, {"css_selector": "#active-content"})
    assert res.has_substantive_change is True
    assert res.error == "OLD_SELECTOR_NOT_FOUND"

def test_ledger_o1_head_sidecar_and_fsync_persistence(tmp_path):
    ledger_file = tmp_path / "audit_ledger.jsonl"
    ledger = EvidenceLedger(ledger_storage_path=str(ledger_file))

    b1 = ledger.append_evidence("legco", "statute", b"Version 1")
    b2 = ledger.append_evidence("legco", "statute", b"Version 2")

    head_file = tmp_path / "audit_ledger.head.json"
    assert head_file.exists()

    fast_ledger = EvidenceLedger(ledger_storage_path=str(ledger_file))
    assert fast_ledger.block_count == 2
    assert fast_ledger.last_block.chain_hash == b2.chain_hash

def test_snapshot_sequence_ordering_under_same_second(tmp_path):
    ledger = EvidenceLedger(ledger_storage_path=str(tmp_path / "ledger.jsonl"))
    store = SnapshotStore(base_dir=str(tmp_path / "snapshots"), ledger=ledger)
    sid = "same_sec_source"

    for i in range(102):
        store.save_snapshot(sid, f"Fast Data Content {i}".encode("utf-8"), ext="txt")

    archive_dir = tmp_path / "snapshots" / sid / "archive"
    assert archive_dir.exists()
    archived_files = list(archive_dir.glob("*.gz"))
    assert len(archived_files) >= 1
    assert "00000001_" in archived_files[0].name
