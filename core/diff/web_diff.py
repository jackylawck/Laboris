"""
Laboris Block-level Semantic Web Diff Engine
"""
from typing import Dict, Any, List
from dataclasses import dataclass
import difflib
import re
import logging
from bs4 import BeautifulSoup
from core.parsers.pdf_parser import COMBINED_ANCHOR_REGEX

logger = logging.getLogger("laboris.kernel.web_diff")

class SelectorNotFoundError(Exception):
    pass

@dataclass(frozen=True)
class SemanticDiffResult:
    has_substantive_change: bool
    added_blocks: List[str]
    removed_blocks: List[str]
    modified_blocks: List[Dict[str, str]]
    change_ratio: float
    change_count: int
    has_critical_statutory_delta: bool
    diff_summary: str
    error: str | None = None

def normalize_text_block(text: str) -> str:
    patterns = [
        r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}(?:日)?(?:\s*\d{1,2}:\d{2}(?::\d{2})?)?",
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
        r"更新於[:：]?\s*.*"
    ]
    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()

def clean_html_to_blocks(raw_html: bytes, css_selector: str) -> List[str]:
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    target = soup.select_one(css_selector)
    if not target:
        raise SelectorNotFoundError(f"Selector '{css_selector}' not found.")

    blocks = []
    target_tags = ["p", "h1", "h2", "h3", "h4", "li", "tr", "td", "th", "section", "article", "dd", "dt"]
    for el in target.find_all(target_tags):
        text = el.get_text(separator=" ", strip=True)
        cleaned = normalize_text_block(text)
        if len(cleaned) >= 6:
            blocks.append(cleaned)

    deduped = []
    for b in blocks:
        if not deduped or deduped[-1] != b:
            deduped.append(b)
    return deduped

def semantic_html_diff(old_html: bytes | None, new_html: bytes, config: Dict[str, Any]) -> SemanticDiffResult:
    selector = config.get("css_selector", "body")
    min_ratio_threshold = config.get("min_change_ratio", 0.02)
    min_absolute_blocks = config.get("min_absolute_blocks", 2)

    try:
        new_blocks = clean_html_to_blocks(new_html, selector)
    except SelectorNotFoundError as e:
        logger.error(f"[NEW HTML SELECTOR FAILURE] {e}")
        return SemanticDiffResult(
            has_substantive_change=False,
            added_blocks=[],
            removed_blocks=[],
            modified_blocks=[],
            change_ratio=0.0,
            change_count=0,
            has_critical_statutory_delta=False,
            diff_summary=f"CRITICAL SELECTOR ERROR: {str(e)}",
            error="NEW_SELECTOR_NOT_FOUND"
        )

    if not old_html:
        return SemanticDiffResult(
            has_substantive_change=True,
            added_blocks=new_blocks[:5],
            removed_blocks=[],
            modified_blocks=[],
            change_ratio=1.0,
            change_count=len(new_blocks),
            has_critical_statutory_delta=True,
            diff_summary="[INITIAL BASELINE] First ingestion captured."
        )

    try:
        old_blocks = clean_html_to_blocks(old_html, selector)
    except SelectorNotFoundError as e:
        logger.warning(f"[OLD SNAPSHOT SELECTOR FAILURE - FORCE BASELINE RESET] {e}")
        return SemanticDiffResult(
            has_substantive_change=True,
            added_blocks=new_blocks[:5],
            removed_blocks=[],
            modified_blocks=[],
            change_ratio=1.0,
            change_count=len(new_blocks),
            has_critical_statutory_delta=True,
            diff_summary="[OLD_SELECTOR_NOT_FOUND] Historical baseline selector failed. Forced baseline reset.",
            error="OLD_SELECTOR_NOT_FOUND"
        )

    matcher = difflib.SequenceMatcher(None, old_blocks, new_blocks)
    added, removed, modified = [], [], []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            added.extend(new_blocks[j1:j2])
        elif tag == "delete":
            removed.extend(old_blocks[i1:i2])
        elif tag == "replace":
            old_sub = " ".join(old_blocks[i1:i2])
            new_sub = " ".join(new_blocks[j1:j2])
            similarity = difflib.SequenceMatcher(None, old_sub, new_sub).ratio()
            if similarity > 0.5:
                modified.append({"from": old_sub[:80], "to": new_sub[:80], "similarity": round(similarity, 2)})
            else:
                removed.extend(old_blocks[i1:i2])
                added.extend(new_blocks[j1:j2])

    total_blocks = max(len(old_blocks), len(new_blocks), 1)
    change_count = len(added) + len(removed) + len(modified)
    change_ratio = round(change_count / total_blocks, 4)

    changed_text_corpus = " ".join(added + removed + [m["from"] + " " + m["to"] for m in modified])
    has_critical_statutory_delta = bool(COMBINED_ANCHOR_REGEX.search(changed_text_corpus))

    is_substantive = (
        has_critical_statutory_delta
        or (change_count >= min_absolute_blocks)
        or (change_ratio >= min_ratio_threshold and change_count > 0)
    )

    summary = f"Variance: {change_count} blocks changed ({change_ratio * 100}%). Critical Statutory: {has_critical_statutory_delta}"

    return SemanticDiffResult(
        has_substantive_change=is_substantive,
        added_blocks=added,
        removed_blocks=removed,
        modified_blocks=modified,
        change_ratio=change_ratio,
        change_count=change_count,
        has_critical_statutory_delta=has_critical_statutory_delta,
        diff_summary=summary
    )
