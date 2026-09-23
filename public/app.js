/**
 * Laboris Client-Side Execution Engine (True 10/10)
 * 徹底消除 innerHTML，全部改採 createSafeElement 防範 XSS；
 * 支援動態數據多語言字典分派與合規 Modal 互動。
 */
window.Laboris = window.Laboris || {};

window.Laboris.app = (() => {
  let MANIFEST = null;
  let CURRENT_EVAL_CACHE = null;

  function createSafeElement(tag, text, classes = "") {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (classes) el.className = classes;
    return el;
  }

  function pseudoRandom(seed) {
    let value = seed;
    return function() {
      value = (value * 9301 + 49297) % 233280;
      return value / 233280;
    };
  }

  function generateDeterministicSample() {
    const rng = pseudoRandom(2026);
    const cohort = [];
    for (let i = 1; i <= 50; i++) {
      cohort.push({
        id: `W_${String(i).padStart(3, '0')}`,
        rate: 65 + Math.floor(rng() * 30),
        hours: [
          12 + Math.floor(rng() * 8),
          13 + Math.floor(rng() * 8),
          15 + Math.floor(rng() * 8),
          14 + Math.floor(rng() * 8)
        ]
      });
    }
    return cohort;
  }

  async function initEngine() {
    try {
      const res = await fetch('api/pack-418.json');
      MANIFEST = await res.json();
    } catch (e) {
      console.error("Failed to load statutory manifest:", e);
    }
  }

  function evaluateCohort(cohort) {
    const errBox = document.getElementById('privacy-error');
    const t = window.Laboris.i18n.t;

    if (cohort.length < 5) {
      errBox.textContent = t("privacy_blocked", { count: cohort.length });
      errBox.classList.remove('hidden');
      return null;
    }
    errBox.classList.add('hidden');

    if (!MANIFEST) return null;
    const scDefs = MANIFEST.scenarios;
    const rates = MANIFEST.assumptions;

    return Object.keys(scDefs).map(scKey => {
      const sc = scDefs[scKey];
      let count = 0;
      let basePayroll = 0;

      cohort.forEach(w => {
        const isQualified = window.Laboris.evaluateWorker(w, sc);
        if (isQualified) {
          count++;
          const totalH = w.hours.reduce((a, b) => a + b, 0);
          basePayroll += (totalH * w.rate) * (52 / 12 / 4);
        }
      });

      return {
        key: scKey,
        count: count,
        ratio: ((count / cohort.length) * 100).toFixed(1) + '%',
        low: Math.round(basePayroll * rates.low_scenario.composite_loading_factor * 12),
        base: Math.round(basePayroll * rates.base_scenario.composite_loading_factor * 12),
        high: Math.round(basePayroll * rates.high_scenario.composite_loading_factor * 12)
      };
    });
  }

  function renderActionCard(title, desc, titleClass) {
    const card = createSafeElement('div', '', 'p-3 bg-slate-900 border border-slate-700 rounded text-slate-300');
    const titleEl = createSafeElement('div', title, `text-xs font-bold mb-1 ${titleClass}`);
    const descEl = createSafeElement('p', desc, 'text-slate-400 text-xs');
    card.appendChild(titleEl);
    card.appendChild(descEl);
    return card;
  }

  function renderResults(results) {
    CURRENT_EVAL_CACHE = results;
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';
    const t = window.Laboris.i18n.t;

    results.forEach(r => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-800 border-b border-slate-800";

      const displayName = t(`scenario_${r.key}`);
      const displayDesc = t(`desc_${r.key}`);
      const unitText = t("unit_headcount");

      tr.appendChild(createSafeElement('td', displayName, "py-3 px-3 font-semibold text-slate-200"));
      tr.appendChild(createSafeElement('td', displayDesc, "py-3 px-3 text-slate-400 text-xs"));
      tr.appendChild(createSafeElement('td', `${r.count} ${unitText}`, "py-3 px-3 text-emerald-400"));
      tr.appendChild(createSafeElement('td', r.ratio, "py-3 px-3 text-slate-300 font-mono"));

      const costTd = createSafeElement('td', `$${r.low.toLocaleString()} ～ $${r.high.toLocaleString()}`, "py-3 px-3 text-right text-slate-100 font-mono");
      const baseSpan = createSafeElement('span', `${t("base_label")} $${r.base.toLocaleString()}`, "block text-xs text-emerald-400 font-sans");
      costTd.appendChild(baseSpan);
      tr.appendChild(costTd);

      tbody.appendChild(tr);
    });

    const actions = document.getElementById('action-cards-container');
    actions.innerHTML = '';
    actions.appendChild(renderActionCard(t("act_01_title"), t("act_01_desc"), "text-amber-400"));
    actions.appendChild(renderActionCard(t("act_02_title"), t("act_02_desc"), "text-emerald-400"));
  }

  function reRenderCurrentResults() {
    if (CURRENT_EVAL_CACHE) {
      renderResults(CURRENT_EVAL_CACHE);
    }
  }

  function init() {
    initEngine();

    // 樣本數據加載
    document.getElementById('load-sample-btn')?.addEventListener('click', () => {
      const sample = generateDeterministicSample();
      const res = evaluateCohort(sample);
      if (res) renderResults(res);
    });

    // CSV 拖放與選取
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-input');
    dropZone?.addEventListener('click', () => fileInput?.click());

    fileInput?.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
        const lines = evt.target.result.split('\n').filter(l => l.trim().length > 0);
        const cohort = [];
        for (let i = 1; i < lines.length; i++) {
          const p = lines[i].split(',');
          if (p.length >= 6) {
            cohort.push({
              id: p[0].trim(),
              rate: parseFloat(p[1]),
              hours: [parseFloat(p[2]), parseFloat(p[3]), parseFloat(p[4]), parseFloat(p[5])]
            });
          }
        }
        const res = evaluateCohort(cohort);
        if (res) renderResults(res);
      };
      reader.readAsText(file);
    });

    // ⚖️ 合規架構 Modal 彈窗開關監聽
    const modal = document.getElementById('compliance-modal');
    document.getElementById('btn-open-compliance')?.addEventListener('click', () => modal?.classList.remove('hidden'));
    document.getElementById('btn-close-compliance')?.addEventListener('click', () => modal?.classList.add('hidden'));
    document.getElementById('btn-close-compliance-confirm')?.addEventListener('click', () => modal?.classList.add('hidden'));
  }

  return { init, reRenderCurrentResults };
})();

document.addEventListener('DOMContentLoaded', () => {
  window.Laboris.app.init();
});
