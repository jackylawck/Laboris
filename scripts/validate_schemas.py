import sys
import yaml
import json
from pathlib import Path
from jsonschema import validate, ValidationError

def run_validations():
    root = Path(__file__).parent.parent
    schemas_dir = root / "schemas"
    packs_dir = root / "packs"

    with open(schemas_dir / "pack.schema.json", "r", encoding="utf-8") as f:
        pack_schema = json.load(f)
    with open(schemas_dir / "scenario.schema.json", "r", encoding="utf-8") as f:
        scenario_schema = json.load(f)

    errors = 0
    for p_dir in packs_dir.iterdir():
        if not p_dir.is_dir() or p_dir.name.startswith("_"):
            continue

        pack_yaml_path = p_dir / "pack.yaml"
        scenarios_yaml_path = p_dir / "scenarios.yaml"

        try:
            if pack_yaml_path.exists():
                with open(pack_yaml_path, "r", encoding="utf-8") as f:
                    validate(instance=yaml.safe_load(f), schema=pack_schema)
            if scenarios_yaml_path.exists():
                with open(scenarios_yaml_path, "r", encoding="utf-8") as f:
                    validate(instance=yaml.safe_load(f), schema=scenario_schema)
            print(f"✅ Pack '{p_dir.name}' passed schema verification.")
        except ValidationError as e:
            print(f"❌ Schema validation failed in '{p_dir.name}': {e.message}")
            errors += 1

    if errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_validations()
