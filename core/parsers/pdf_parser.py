"""
Laboris Statutory PDF Layout-Aware Extraction Engine
"""
from typing import Dict, Any, List, Optional
import io
import re
import pdfplumber
import logging

logger = logging.getLogger("laboris.kernel.pdf_parser")

STATUTORY_ANCHOR_PATTERNS = [
    r"第\s*[0-9A-Za-z]+\s*章",
    r"第\s*[0-9A-Za-z]+\s*條(?:\s*\([0-9a-zA-Z]+\))*",
    r"附表\s*[0-9A-Za-z]+",
    r"第\s*\([0-9a-zA-Z]+\)\s*款",
    r"第\s*\([ivxIVX]+\)\s*項",
    r"段落\s*[0-9]+(?:\.[0-9]+)*",
    r"Cap\.\s*[0-9A-Za-z]+",
    r"Section\s*[0-9A-Za-z]+(?:\s*\([0-9a-zA-Z]+\))*",
    r"Schedule\s*[0-9A-Za-z]+",
    r"Paragraph\s*[0-9]+(?:\.[0-9]+)*",
    r"Clause\s*[0-9A-Za-z]+",
    r"^\s*\([0-9a-zA-Z]+\)",
    r"^\s*\([ivxIVX]+\)",
    r"^\s*[0-9]+\.[0-9]+"
]

COMBINED_ANCHOR_REGEX = re.compile("|".join(STATUTORY_ANCHOR_PATTERNS), re.MULTILINE)

def extract_comprehensive_anchors(page_text: str, page_num: int) -> List[Dict[str, Any]]:
    anchors = []
    lines = page_text.splitlines()
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        for match in COMBINED_ANCHOR_REGEX.finditer(line_clean):
            token = match.group(0).strip()
            if token:
                anchors.append({
                    "page": page_num,
                    "line_index": idx,
                    "anchor_token": token,
                    "snippet": line_clean[:100]
                })
    return anchors

def detect_column_split(words: List[Dict[str, Any]], page_width: float) -> Optional[float]:
    """
    幾何佈局雙欄檢測：
    1. 詞彙數 >= 12
    2. 左半區與右半區均有詞彙分佈
    3. 頁面中央過渡帶詞彙密度低於兩側
    """
    if len(words) < 12:
        return None

    mid_start = page_width * 0.40
    mid_end = page_width * 0.60

    left_words = [w for w in words if w.get("x1", 0) <= mid_end]
    right_words = [w for w in words if w.get("x0", 0) >= mid_start]

    # 確保兩欄都有足夠內容分佈
    if len(left_words) < 3 or len(right_words) < 3:
        return None

    # 中央過渡區詞彙
    mid_words = [w for w in words if not (w.get("x1", 0) < mid_start or w.get("x0", 0) > mid_end)]
    
    # 只要跨中線的詞彙比例低於 15%，即判定為雙欄結構
    if (len(mid_words) / len(words)) <= 0.15:
        return page_width / 2.0

    return None

def extract_page_text_geometry(page) -> str:
    words = page.extract_words()
    split_x = detect_column_split(words, page.width)
    y_top = page.height * 0.04
    y_bottom = page.height * 0.96

    if split_x:
        left_box = (0, y_top, split_x, y_bottom)
        right_box = (split_x, y_top, page.width, y_bottom)
        left_text = (page.crop(left_box).extract_text(layout=True) or "").strip()
        right_text = (page.crop(right_box).extract_text(layout=True) or "").strip()
        return f"{left_text}\n\n--- COLUMN BREAK ---\n\n{right_text}"
    else:
        full_box = (0, y_top, page.width, y_bottom)
        return (page.crop(full_box).extract_text(layout=True) or "").strip()

def parse_pdf_layout_aware(raw_content: bytes, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not raw_content.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF payload: Missing %PDF- magic header")

    extracted_pages = []
    total_tables_count = 0
    all_citations = []
    full_text_buffer = []

    with pdfplumber.open(io.BytesIO(raw_content)) as pdf:
        meta = pdf.metadata or {}
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            page_text = extract_page_text_geometry(page)
            full_text_buffer.append(page_text)

            tables = page.extract_tables() or []
            total_tables_count += len(tables)

            page_citations = extract_comprehensive_anchors(page_text, page_num)
            all_citations.extend(page_citations)

            extracted_pages.append({
                "page_number": page_num,
                "text_length": len(page_text),
                "is_multi_column": "--- COLUMN BREAK ---" in page_text,
                "tables_found": len(tables),
                "tables": tables,
                "citations": page_citations
            })

        combined_text = "\n".join(full_text_buffer)
        statutory_matches = re.findall(r"(連續性合約|最低工資|附表\s*1|418|468|Cap\.\s*\d+)", combined_text)

        return {
            "valid_pdf_format": True,
            "page_count": len(pdf.pages),
            "metadata": {
                "title": meta.get("Title", "Official Statutory Paper"),
                "author": meta.get("Author", "HKSAR Government / LegCo"),
                "creation_date": meta.get("CreationDate", "")
            },
            "total_tables_extracted": total_tables_count,
            "statutory_keywords": list(set(statutory_matches)),
            "citation_anchors_count": len(all_citations),
            "pages": extracted_pages
        }
