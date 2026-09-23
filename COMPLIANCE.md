# Laboris Global Compliance & Regulatory Applicability Ledger
# 全球法規適用性與治理合規清冊

Last Updated: September 2026 | Version: 1.0.0-pilot  
Jurisdiction Primary Anchor: Hong Kong Special Administrative Region (HKSAR)

---

## 1. Executive Summary & Legal Characterization / 執行摘要與系統定性

Laboris (勞則) is an open-source, deterministic statutory ledger and actuarial decision engine designed for Hong Kong Cap. 57 Employment Ordinance continuous contract stress-testing. 

**Core Technical Reality:**  
Laboris operates strictly as a **Zero-Server, Client-Side Deterministic Calculator**. No personal identity data is ingested, transmitted, processed, or retained on any remote server.

「勞則 (Laboris)」為針對香港法例第 57 章《僱傭條例》連續性合約修訂之開源確定性總帳與精算決策引擎。  
**核心架構事實：** 本系統為**無伺服器、純客戶端本機運算沙盒**。任何個人身分資料均不曾上傳、傳輸、處理或保存於任何遠端伺服器。

---

## 2. Global AI Governance Scoping & Exemption / 人工智能治理法規豁免裁定

### 2.1 EU Artificial Intelligence Act (EU AI Act) — **NOT APPLICABLE**
* **Statutory Determination:** Laboris does **NOT** contain, deploy, or interface with any Artificial Intelligence, Machine Learning (ML), Large Language Models (LLMs), neural networks, or autonomous algorithmic models.
* **Legal Ground:** Under Article 3(1) of the EU AI Act, an "AI system" requires machine-based inference capabilities with varying levels of autonomy. Laboris executes pure, rule-based, deterministic arithmetic formulas derived directly from statutory ordinances. Therefore, Laboris falls entirely outside the scope of the EU AI Act.

### 2.2 ISO/IEC 42001:2023 (Artificial Intelligence Management System) — **NOT APPLICABLE**
* Laboris does not develop, procure, or operate AI systems. Any assertion of ISO/IEC 42001 certification would constitute misrepresentation. Laboris disclaims any formal claim to ISO/IEC 42001 certification.

### 2.3 CAC Algorithmic & Generative AI Provisions (國家網信辦) — **NOT APPLICABLE**
* Laboris does not generate synthetic content, operate algorithmic recommendation engines, or process cross-border data transfer involving Mainland China. It is not subject to the Provisions on the Management of Algorithmic Recommendations or the Interim Measures for the Management of Generative AI Services.

---

## 3. Data Protection & Privacy Governance / 個人資料私隱保護合規

### 3.1 Hong Kong Cap. 486 Personal Data (Privacy) Ordinance (PDPO) — **COMPLIANT BY DESIGN**
Laboris strictly adheres to the Six Data Protection Principles (DPPs) of the PDPO:
1. **DPP 1 (Purpose and manner of collection):** Zero data collection. Timesheet processing executes exclusively within the ephemeral memory of the user's browser.
2. **DPP 2 (Accuracy and retention):** Data is purged upon browser session termination. No persistent records are stored remotely.
3. **DPP 3 (Use of data):** Data is used solely for on-the-fly mathematical aggregation.
4. **DPP 4 (Data security):** Mandatory client-side $k$-anonymity enforcement ($k \ge 5$). The engine actively blocks calculation and rendering if cohort size is below 5, eliminating re-identification risks.
5. **DPP 5 (Information openness):** Source code and formulas are open-source and auditable.
6. **DPP 6 (Access and correction):** Users retain full custody of local CSV inputs.

### 3.2 EU General Data Protection Regulation (GDPR) — **SAFE HARBOR / EXEMPTION**
* Under Recital 26 of the GDPR, the principles of data protection do not apply to anonymous information. Since Laboris enforces local $k$-anonymity and does not process data identifiable to natural persons, nor transfers data across borders, GDPR cross-border transfer obligations (Chapter V) are not triggered.

---

## 4. Information Security Controls (ISO/IEC 27001:2022 Alignment) / 資訊安全控制對標

Laboris makes **no formal claim** of accredited third-party ISO/IEC 27001 certification, but implements defense-in-depth controls aligned with its control domains:

| Control Domain | Architectural Implementation in Laboris |
|---|---|
| **A.8.7 Protection against malware** | Supply chain integrity: Dependencies hash-pinned; automated `pip-audit` CVE checks in CI pipeline. |
| **A.8.9 Configuration management** | Declarative configuration (`registry.yaml`, `sources.yaml`) with strict JSON Schema v2.0.0 validation gates. |
| **A.8.25 Secure development life cycle** | SAST security scans (Bandit) integrated into GitHub Actions gate prior to artifact build. |
| **A.8.28 Secure coding** | Strict Content Security Policy (`default-src 'none'`), no inline script execution, anti-clickjacking headers, and DOM injection defense (`createSafeElement`). |
| **A.8.15 Logging and monitoring** | Local structured audit logger (`core/access_logger.py`) with `RotatingFileHandler` and immutable append-only JSONL ledgers. |
