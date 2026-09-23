# Laboris | 勞則
> **Hong Kong Statutory Workforce & Regulatory Liability Ledger**  
> 香港法定勞動力政策總帳與精算決策引擎（審計級開源治理生態系）

[繁體中文](#繁體中文) | [English](#english)

---

<div align="center">

[![Pages Deployment](https://github.com/jackylawck/Laboris/actions/workflows/static.yml/badge.svg)](https://github.com/jackylawck/Laboris/actions/workflows/static.yml)
[![Regulatory Architecture Audit](https://github.com/jackylawck/Laboris/actions/workflows/audit.yml/badge.svg)](https://github.com/jackylawck/Laboris/actions/workflows/audit.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Security: Client-Side Isolated](https://img.shields.io/badge/Security-Zero--Server%20Sandbox-blue.svg)](PRIVACY.md)
[![Privacy: PDPO Aligned](https://img.shields.io/badge/Privacy-PDPO%20k--Anonymity-success.svg)](PRIVACY.md)
[![Compliance: Deterministic Code](https://img.shields.io/badge/Compliance-Deterministic%20(No%20AI)-emerald.svg)](COMPLIANCE.md)

**🌐 Live Regulatory Sandbox / 線上精算沙盒**:  
[https://jackylawck.github.io/Laboris/](https://jackylawck.github.io/Laboris/)

</div>

---

## 繁體中文

### 📖 專案宗旨 (Mission Statement)
**「勞則 (Laboris)」** 取意「勞動則例」，對標香港普通法章號（Cap.）體系，是專為香港企業人力資本治理打造的**審計級勞動力政策總帳與確定性精算決策引擎**。

系統針對香港法例第 57 章《僱傭條例》附表 1 關於「418」連續性合約（擬由每週不少於 18 小時放寬至 4 週累計 68 / 60 小時）之法定修訂，提供企業級的財務衝擊敏感度測算、預算準備金撥備評估以及董事會級行動卡（Action Playbook）。

---

### 🧭 雙層架構導讀 (Two-Tier Architecture)
為兼顧終端用戶零延遲的瀏覽器沙盒體驗與企業級擴展底座，本專案採用明確的兩層架構：

```text
laboris/
├── 🟢 Tier 1: 核心輕量沙盒 (Active Pilot MVP - 10 核心檔案)
│   ├── public/                      # 純客戶端雙語儀表板 (本機運算，PDPO 零資料上傳)
│   ├── packs/continuous_contract/   # 418 連續性合約法規情境與確定性精算規則
│   ├── scripts/build_manifest.py    # 單一事實 YAML -> JSON 編譯器
│   └── requirements.txt             # 極簡核心運行依賴
│
└── 🔵 Tier 2: 審計級後台底座 (Enterprise Ready - 詳見 docs/PHASE2.md)
    ├── core/                        # 密碼學存證總帳 (JSONL)、快照歸檔、PDF 雙欄幾何解析、語意 Diff
    ├── schemas/                     # JSON Schema v2.0.0 規範約束
    └── tests/                       # 進階幾何排版與密碼學測試套件

```

---

### 🛡️ 企業級安全與合規實踐 (Governance & InfoSec)

1. **香港私隱條例 (Cap. 486 PDPO) 零外洩防護**：
* **純客戶端沙盒 (Zero-Server Architecture)**：所有工時 CSV 檔案僅於瀏覽器本機記憶體解析，伺服器不接收、不記錄任何員工檔案。
* **強制 $k$-匿名保護 ($k \ge 5$)**：若匯入之樣本數小於 5，系統強制阻斷計算與渲染，杜絕個別員工重識別風險。


2. **全球 AI 法規豁免裁定 (AI Governance Negative Clearance)**：
* 本系統為**純規則驅動之確定性精算代碼（Deterministic Code）**，完全不包含任何 AI、機器學習或大語言模型。
* 依據歐盟《人工智能法案》(EU AI Act) 第 3 條規定，本系統**不屬於** AI 系統範疇，亦明確排除 ISO/IEC 42001 之適用。


3. **ISO/IEC 27001 資訊安全控制對標**：
* **嚴格內容安全策略 (CSP)**：禁止非同源腳本，防範跨站腳本攻擊 (XSS) 與資料外流。
* **供應鏈安全與靜態掃描**：CI/CD 整合 Bandit SAST 安全掃描與 `pip-audit` 漏洞稽核。
* **防篡改審計鏈**：後台提供以 `os.fsync()` 落盤的 Append-Only JSONL 密碼學證據總帳。



---

### 🚀 快速上手 (Quick Start)

#### 1. 本地啟動前端沙盒

無需安裝後端資料庫或複雜環境，直接透過靜態伺服器開啟：

```bash
# Clone 儲存庫
git clone [https://github.com/jackylawck/Laboris.git](https://github.com/jackylawck/Laboris.git)
cd Laboris

# 啟動本地伺服器
cd public
python3 -m http.server 8080
# 瀏覽器開啟 http://localhost:8080

```

#### 2. 本地執行合規審計與單元測試

```bash
# 安裝開發依賴
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# 驗證 Schema 契約與編譯 Manifest
python scripts/validate_schemas.py
python scripts/build_manifest.py

# 執行全量架構單元測試
pytest tests/ packs/ --verbose

```

---

### ⚠️ 法定免責聲明 (Statutory Disclaimer)

本系統所有計算模型、敏感度分析、衝擊矩陣與行動卡均屬企業營運風險管理與預算模擬輔助情資，**絕不構成香港法例或其他司法管轄區之正式法律、精算、稅務或專業財務諮詢意見**。涉及具體法定權利義務與合約修訂，請諮詢香港執業常年法律顧問。本專案受中華人民共和國香港特別行政區法律管轄（詳見 [LEGAL_DISCLAIMER.md](https://www.google.com/search?q=LEGAL_DISCLAIMER.md&utm_source=gemini)）。

---

## English

### 📖 Mission Statement

**"Laboris" (勞則)**, inspired by the statutory chapter (Cap.) system of Hong Kong Common Law, is an **audit-grade statutory workforce ledger and deterministic actuarial decision engine** designed for corporate human capital governance.

Specifically addressing Schedule 1 of the Hong Kong Employment Ordinance (Cap. 57) regarding the proposed relaxation of the "418" continuous contract threshold (transitioning from 18 hours/week to 68 or 60 aggregate hours per 4-week window), Laboris provides enterprise-grade financial stress-testing, statutory accrual budgeting, and board-level Action Cards.

---

### 🧭 Two-Tier Architecture

To balance zero-latency client-side browser performance with enterprise-grade extensibility, Laboris is organized into a clean, two-tier model:

```text
laboris/
├── 🟢 Tier 1: Lightweight Client Sandbox (Active Pilot MVP - 10 Core Files)
│   ├── public/                      # Zero-server client-side dashboard (Local compute, PDPO aligned)
│   ├── packs/continuous_contract/   # Cap. 57 continuous contract scenarios & actuarial rules
│   ├── scripts/build_manifest.py    # Single Source of Truth YAML -> JSON manifest compiler
│   └── requirements.txt             # Minimal runtime dependency footprint
│
└── 🔵 Tier 2: Enterprise Audit Foundation (Detailed in docs/PHASE2.md)
    ├── core/                        # Append-only cryptographic ledger, snapshot store, layout-aware PDF parser, web diff
    ├── schemas/                     # JSON Schema v2.0.0 validation contracts
    └── tests/                       # Geometry and cryptographic unit test suite

```

---

### 🛡️ Governance & Information Security

1. **Hong Kong PDPO (Cap. 486) Zero-Leakage Privacy Protection**:
* **Zero-Server Client Architecture**: All timesheet CSV processing executes exclusively within client-side browser memory. No employee payroll data is transmitted, processed, or retained on remote servers.
* **Mandatory $k$-Anonymity Enforcement ($k \ge 5$)**: The engine terminates calculation and rendering if a cohort contains fewer than 5 records, mathematically preventing re-identification risks.


2. **Global AI Governance Scoping & Exemption**:
* Laboris consists entirely of **deterministic, rule-based mathematical models** and does not incorporate AI, Machine Learning, or Large Language Models (LLMs).
* Pursuant to Article 3(1) of the **EU Artificial Intelligence Act (EU AI Act)**, Laboris is **explicitly out of scope** of AI regulations, and disclaims ISO/IEC 42001 applicability (see [COMPLIANCE.md](https://www.google.com/search?q=COMPLIANCE.md&utm_source=gemini)).


3. **ISO/IEC 27001 InfoSec Alignment**:
* **Strict Content Security Policy (CSP)**: Disallows unauthorized external scripts and inline execution to thwart cross-site scripting (XSS) and data exfiltration.
* **Supply Chain Security**: Hash-pinned dependencies with automated SAST (Bandit) and CVE scanning (`pip-audit`) enforced in CI pipelines.
* **Append-Only Evidence Provenance**: Backend features an `os.fsync()`-backed cryptographic JSONL ledger maintaining SHA-256 parent-child block hash chains.



---

### 🚀 Quick Start

#### 1. Running the Sandbox Locally

Laboris requires no database or backend servers. Launch instantly via any static file server:

```bash
# Clone the repository
git clone [https://github.com/jackylawck/Laboris.git](https://github.com/jackylawck/Laboris.git)
cd Laboris

# Start a local static server
cd public
python3 -m http.server 8080
# Open http://localhost:8080 in your browser

```

#### 2. Running Schema Audits and Unit Tests

```bash
# Set up development virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Validate JSON Schema compliance & generate manifest
python scripts/validate_schemas.py
python scripts/build_manifest.py

# Run deterministic evaluator test suite
pytest tests/ packs/ --verbose

```

---

### ⚠️ Statutory Disclaimer

All models, calculations, sensitivity matrices, and action cards generated by Laboris are designed solely for corporate risk governance and internal budgetary planning. **They DO NOT constitute formal legal, actuarial, tax, or financial advice** under the laws of Hong Kong or any other jurisdiction. Organizations must consult qualified legal counsel for binding statutory compliance decisions. Governed by the laws of the Hong Kong Special Administrative Region (see [LEGAL_DISCLAIMER.md](https://www.google.com/search?q=LEGAL_DISCLAIMER.md&utm_source=gemini)).

---

### 📄 License

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE&utm_source=gemini).
