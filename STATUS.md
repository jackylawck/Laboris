# Laboris 試運行狀態聲明 (Pilot Sandbox Status)

**當前版本：** v0.1.0-pilot | **評估時間：** 2026 年 9 月

---

## 一、 已就緒功能 (Production-Ready in Pilot)
* **純客戶端本地隱私沙盒 (Client-Side Privacy Sandbox)**：工時 CSV 於瀏覽器本機內存計算，強制落實 $k \ge 5$ 匿名防禦。
* **418 連續性合約確定性模型**：現行基準 vs 68h 共識 vs 60h 放寬方案之法定福利增額敏感度測算。
* **審計存證底座**：Append-Only JSONL 證據鏈（含 `os.fsync` 落盤）、雙欄幾何 PDF 解析與區塊級 Web Diff 引擎。
* **動態雙語切換**：繁體中文（香港法定則例術語）與全英文（上市公司董事會術語）無縫即時切換。

---

## 二、 試運行階段已知限制 (Known Sandbox Scope)
1. **外部情報端點狀態**：`sources.yaml` 內之香港立法會與勞工處端點暫以 Mock / Stub 數據運行，用於驗證管線與前端流轉；真實網絡採集與定期 Cron 排程預計於 Phase 2 正式接入。
2. **存儲加密狀態**：若環境變數未注入 `LABORIS_STORAGE_KEY`，本地快照存儲將以明文形式保存並記錄警告日誌。
3. **系統整合**：目前僅提供一頁式 CHRO Markdown / 畫面預覽，Jira / ServiceNow / HRIS 工單雙向聯動列入後續路線圖。
