from dataclasses import dataclass
from typing import List, Dict, Any
import hashlib
import json
from core.privacy import verify_k_anonymity

@dataclass(frozen=True)
class AnonymizedWorkerRecord:
    worker_pseudonym: str
    job_family: str
    hourly_rate: float
    weekly_hours_cycle: List[float]

class ContinuousContractEvaluator:
    def __init__(self, scenarios_config: Dict[str, Any], assumptions_config: Dict[str, Any]):
        self.scenarios = scenarios_config.get("scenarios", {})
        self.assumptions = assumptions_config.get("actuarial_loadings", {})

    def evaluate(self, cohort: List[AnonymizedWorkerRecord]) -> Dict[str, Any]:
        verify_k_anonymity(len(cohort), k_threshold=5)

        cohort_data_repr = json.dumps([w.__dict__ for w in cohort], sort_keys=True)
        cohort_sha = hashlib.sha256(cohort_data_repr.encode("utf-8")).hexdigest()

        results = {
            "meta": {
                "cohort_size": len(cohort),
                "data_integrity_sha256": cohort_sha
            },
            "scenarios_impact": {}
        }

        for sc_id, sc in self.scenarios.items():
            rule_type = sc["rule_type"]
            qualified_count = 0
            monthly_payroll_impacted = 0.0

            for w in cohort:
                hours = w.weekly_hours_cycle
                is_eligible = False

                if rule_type == "consecutive_weekly_minimum":
                    is_eligible = all(h >= sc["weekly_minimum_hours"] for h in hours)
                elif rule_type == "aggregate_window_total":
                    is_eligible = sum(hours) >= sc["aggregate_minimum_hours"]

                if is_eligible:
                    qualified_count += 1
                    month_equiv = (sum(hours) * w.hourly_rate) * (52 / 12 / 4)
                    monthly_payroll_impacted += month_equiv

            low_rate = self.assumptions["low_scenario"]["composite_loading_factor"]
            base_rate = self.assumptions["base_scenario"]["composite_loading_factor"]
            high_rate = self.assumptions["high_scenario"]["composite_loading_factor"]

            results["scenarios_impact"][sc_id] = {
                "name": sc["name"],
                "qualified_headcount": qualified_count,
                "qualification_ratio": round(qualified_count / len(cohort), 4),
                "monthly_base_payroll_qualified": round(monthly_payroll_impacted, 2),
                "annual_cost_band": {
                    "low": round(monthly_payroll_impacted * low_rate * 12, 2),
                    "base": round(monthly_payroll_impacted * base_rate * 12, 2),
                    "high": round(monthly_payroll_impacted * high_rate * 12, 2)
                }
            }

        return results
