import pytest
import yaml
from pathlib import Path
from core.privacy import PrivacyViolationError
from packs.continuous_contract.rules import ContinuousContractEvaluator, AnonymizedWorkerRecord

@pytest.fixture
def evaluator():
    pack_dir = Path(__file__).parent.parent
    with open(pack_dir / "scenarios.yaml", "r", encoding="utf-8") as f:
        scenarios = yaml.safe_load(f)
    with open(pack_dir / "assumptions.yaml", "r", encoding="utf-8") as f:
        assumptions = yaml.safe_load(f)
    return ContinuousContractEvaluator(scenarios, assumptions)

def test_k_anonymity_enforcement(evaluator):
    small_cohort = [
        AnonymizedWorkerRecord(f"ID_{i}", "Retail", 75.0, [18, 18, 18, 18])
        for i in range(4)
    ]
    with pytest.raises(PrivacyViolationError):
        evaluator.evaluate(small_cohort)

def test_418_boundary_evaluation(evaluator):
    cohort = [
        AnonymizedWorkerRecord("W0", "F&B", 70.0, [18, 18, 18, 18]),
        AnonymizedWorkerRecord("W1", "F&B", 70.0, [10, 20, 20, 18]),
        AnonymizedWorkerRecord("W2", "Retail", 65.0, [16, 17, 17, 17]),
        AnonymizedWorkerRecord("W3", "Logistics", 80.0, [15, 15, 15, 15]),
        AnonymizedWorkerRecord("W4", "Logistics", 80.0, [0, 0, 0, 0]),
    ]
    out = evaluator.evaluate(cohort)
    sc = out["scenarios_impact"]

    assert sc["current_status_quo"]["qualified_headcount"] == 1
    assert sc["proposed_scenario_68h"]["qualified_headcount"] == 2
    assert sc["proposed_scenario_60h"]["qualified_headcount"] == 4
