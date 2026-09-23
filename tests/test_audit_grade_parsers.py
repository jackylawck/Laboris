import pytest
import io
from pathlib import Path
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

    # 左欄 (X: 40 ~ 220)：高密度獨立詞彙，包含法規錨點
    left_lines = [
        "Cap 57 Employment Ordinance Comprehensive Review Report",
        "Section 4 Statutory Assessment Briefing Guidance Note",
        "Schedule 1 Continuous Contract Evaluation Practice Rules",
        "Statutory Threshold Analysis For Hong Kong Employers",
        "Audit Trail Evidence Verification Logic Framework",
        "Deterministic Formula Calculations for Enterprise Human Resources",
        "Compliance Architecture Board Action Playbook Preview",
        "第 57 章 《 僱傭條例 》 檢討 報告 法律 分析",
        "第 4 條(1) 連續 受僱 規定 評估 準則 說明",
        "附表 1 擬議 修訂 方案 實施 原則 指引",
        "前線 兼職 員工 福利 保障 評估 會議 紀錄",
        "勞工處 勞顧會 共識 方案 工時 計算 標準",
    ]
    y = height - 60
    for line in left_lines:
        c.drawString(40, y, line)
        y -= 20

    # 右欄 (X: 360 ~ 560)：中央保持清晰空隙 (Gutter: 220 ~ 360)
    right_lines = [
        "Section 4 Statutory Benefits Entitlement Summary Table",
        "Paragraph 3.2 Financial Impact Provision Modeling Study",
        "Grace Period Schedule Forecast 180 Calendar Days",
        "Operational Guidance for Corporate Employers Compliance",
        "Continuous Contract Working Hours Threshold Evaluation",
        "Composite Loading Factor Calculations for Budgeting Pool",
        "Actuarial Sensitivity Matrix Baseline Scenario Comparison",
        "Corporate Risk Management Guidelines Boardroom Briefing",
        "法定 權益 衝擊 敏感度 試算 成果 摘要 表格",
        "精算 模型 基準 情境 預算 提撥 評估 報告",
        "預期 寬限期 為 180 天 執行 整備 藍圖",
        "企業 人力 資本 治理 實務 指南 與 檢核 項目",
    ]
    y = height - 60
    for line in right_lines:
        c.drawString(360, y, line)
        y -= 20

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
    archived_files = sorted(list(archive_dir.glob("*.gz")), key=lambda p: p.name)
    assert len(archived_files) >= 1
    assert "00000001_" in archived_files[0].name
