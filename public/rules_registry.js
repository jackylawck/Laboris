/**
 * Laboris Client-side Rule Engine Registry
 */
window.Laboris = window.Laboris || {};

window.Laboris.rules = {
  consecutive_weekly_minimum: (worker, scenarioConfig) => {
    return worker.hours.every(h => h >= scenarioConfig.weekly_minimum_hours);
  },
  aggregate_window_total: (worker, scenarioConfig) => {
    const total = worker.hours.reduce((acc, cur) => acc + cur, 0);
    return total >= scenarioConfig.aggregate_minimum_hours;
  }
};

window.Laboris.evaluateWorker = function(worker, scenarioConfig) {
  const ruleFn = window.Laboris.rules[scenarioConfig.rule_type];
  if (!ruleFn) {
    throw new Error(`[RULE REGISTRY ERROR] Unregistered rule_type: ${scenarioConfig.rule_type}`);
  }
  return ruleFn(worker, scenarioConfig);
};
