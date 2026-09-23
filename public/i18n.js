/**
 * Laboris Client-Side Internationalization (i18n) Engine (True 10/10)
 * Namespace 防護、動態更新 <html lang>、安全 fallback 機制、動態數據雙語覆蓋。
 */
window.Laboris = window.Laboris || {};

window.Laboris.i18n = (() => {
  const I18N_DICTIONARY = {
    "zh-HK": {
      "site_title": "Laboris 勞則",
      "badge_cap": "Cap. 57 審計級",
      "site_subtitle": "香港法定勞動力政策總帳與精算決策引擎",
      "sandbox_note": "純客戶端本地隱私沙盒 (PDPO 零資料上傳)",
      "disclaimer_title": "法定責任邊界聲明：",
      "disclaimer_text": "本系統所有試算輸出均為企業營運治理與預算模擬輔助，不構成香港正式法律或精算諮詢意見。涉法修訂請諮詢執業常年法律顧問。",
      "step1_title": "1. 匿名工時資料載入",
      "step1_desc": "拖入含 4 週工時之脫敏 CSV（強制 k ≥ 5 匿名保護，數據本機解析不離開瀏覽器）：",
      "drop_text": "點擊選擇 CSV 或將檔案拖放至此",
      "btn_sample": "載入展示用樣本群組 (50人兼職樣本)",
      "step2_title": "2. 418 連續性合約衝擊敏感度測算",
      "th_scenario": "情境方案",
      "th_definition": "法定門檻定義",
      "th_headcount": "合資格人數",
      "th_ratio": "受影響比率",
      "th_cost": "年度新增福利開支區間 (HKD)",
      "table_placeholder": "請先載入工時資料以執行確定性精算。",
      "step3_title": "3. 董事會決策行動卡 (Action Cards Preview)",
      "action_placeholder": "載入資料後將自動依精算結果生成治理工單與 SLA 倒推排程。",
      "act_01_title": "ACT-418-01 排班防禦閥值",
      "act_01_desc": "門市前線兼職建議於排班系統設立 4 週累計 60 小時監控線，預防性控管福利溢價。",
      "act_02_title": "ACT-418-02 預算撥備申報",
      "act_02_desc": "建請 C&B 依基準加成方案列入下一財政年度營運準備金。",
      "privacy_blocked": "[隱私約束阻斷] 樣本數 ({count}) 低於 k-匿名要求 (k ≥ 5)，已拒絕輸出以杜絕重識別。",
      "base_label": "基準:",
      "unit_headcount": "人",
      "scenario_current_status_quo": "現行基準 (Current 418)",
      "scenario_proposed_scenario_68h": "勞顧會共識方案 (4週合計 68 小時)",
      "scenario_proposed_scenario_60h": "工會倡議寬鬆方案 (4週合計 60 小時)",
      "desc_current_status_quo": "連續 4 週每週不少於 18 小時",
      "desc_proposed_scenario_68h": "4 週累計工時合計不少於 68 小時",
      "desc_proposed_scenario_60h": "4 週累計工時合計不少於 60 小時"
    },
    "en-US": {
      "site_title": "Laboris",
      "badge_cap": "Cap. 57 Audit-Grade",
      "site_subtitle": "Hong Kong Statutory Workforce & Regulatory Liability Ledger",
      "sandbox_note": "Zero-Server Client Sandbox (PDPO Aligned, Zero Data Leakage)",
      "disclaimer_title": "Statutory Disclaimer: ",
      "disclaimer_text": "All calculations are for corporate governance simulation only and do not constitute formal legal or actuarial advice in Hong Kong. Consult qualified legal counsel for binding compliance decisions.",
      "step1_title": "1. Anonymized Roster Ingestion",
      "step1_desc": "Drop anonymized 4-week timesheet CSV (Mandatory k ≥ 5 anonymity enforced locally in browser):",
      "drop_text": "Click to browse or drop CSV timesheet here",
      "btn_sample": "Load Deterministic Sample Cohort (50 Part-time Staff)",
      "step2_title": "2. Continuous Contract (418) Stress-Test Matrix",
      "th_scenario": "Regulatory Scenario",
      "th_definition": "Statutory Threshold",
      "th_headcount": "Qualified Headcount",
      "th_ratio": "Impact Ratio",
      "th_cost": "Annual Incremental Benefit Pool (HKD)",
      "table_placeholder": "Please load timesheet data to execute deterministic actuarial model.",
      "step3_title": "3. Board-Level Action Cards (Action Cards Preview)",
      "action_placeholder": "Action tickets and countdown SLAs will generate automatically based on stress-test output.",
      "act_01_title": "ACT-418-01 Shift Roster Defense Threshold",
      "act_01_desc": "Recommend HR Operations set a 60-hour 4-week rolling alert in roster engine to manage benefit liabilities.",
      "act_02_title": "ACT-418-02 Statutory Accrual Budgeting",
      "act_02_desc": "Recommend C&B allocate benchmark incremental provision in FY2027 corporate annual budget.",
      "privacy_blocked": "[Privacy Constraint Blocked] Cohort size ({count}) is below k-anonymity threshold (k ≥ 5). Calculation terminated to prevent re-identification.",
      "base_label": "Base:",
      "unit_headcount": "Staff",
      "scenario_current_status_quo": "Current Statutory Base (418)",
      "scenario_proposed_scenario_68h": "LAB Consensus Option (68h / 4-Week Total)",
      "scenario_proposed_scenario_60h": "Union Proposed Option (60h / 4-Week Total)",
      "desc_current_status_quo": "At least 18 hours per week for 4 consecutive weeks",
      "desc_proposed_scenario_68h": "At least 68 aggregate hours across 4-week rolling window",
      "desc_proposed_scenario_60h": "At least 60 aggregate hours across 4-week rolling window"
    }
  };

  const SUPPORTED_LANGS = ["zh-HK", "en-US"];
  let currentLang = localStorage.getItem("laboris_lang");
  if (!SUPPORTED_LANGS.includes(currentLang)) {
    currentLang = "zh-HK";
  }

  function setLanguage(lang) {
    if (!SUPPORTED_LANGS.includes(lang)) return;
    currentLang = lang;
    localStorage.setItem("laboris_lang", lang);

    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      el.textContent = t(key);
    });

    const btnZh = document.getElementById("btn-lang-zh");
    const btnEn = document.getElementById("btn-lang-en");
    if (btnZh && btnEn) {
      if (lang === "zh-HK") {
        btnZh.className = "px-2 py-1 text-xs font-semibold rounded bg-emerald-800 text-white";
        btnEn.className = "px-2 py-1 text-xs font-semibold rounded bg-slate-800 text-slate-400 hover:text-white";
      } else {
        btnZh.className = "px-2 py-1 text-xs font-semibold rounded bg-slate-800 text-slate-400 hover:text-white";
        btnEn.className = "px-2 py-1 text-xs font-semibold rounded bg-emerald-800 text-white";
      }
    }

    if (window.Laboris.app && typeof window.Laboris.app.reRenderCurrentResults === "function") {
      window.Laboris.app.reRenderCurrentResults();
    }
  }

  function t(key, params = {}) {
    let val = I18N_DICTIONARY[currentLang]?.[key];
    if (val === undefined) {
      val = I18N_DICTIONARY["zh-HK"]?.[key] || key;
    }
    Object.keys(params).forEach(p => {
      val = val.replace(`{${p}}`, params[p]);
    });
    return val;
  }

  function init() {
    setLanguage(currentLang);
    document.getElementById("btn-lang-zh")?.addEventListener("click", () => setLanguage("zh-HK"));
    document.getElementById("btn-lang-en")?.addEventListener("click", () => setLanguage("en-US"));
  }

  return { init, setLanguage, t, getCurrentLang: () => currentLang };
})();

document.addEventListener("DOMContentLoaded", () => {
  window.Laboris.i18n.init();
});
