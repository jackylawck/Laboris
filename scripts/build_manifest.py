import yaml
import json
from pathlib import Path

def build():
    root = Path(__file__).parent.parent
    pack_dir = root / "packs" / "continuous_contract"
    
    with open(pack_dir / "pack.yaml", "r", encoding="utf-8") as f:
        pack_meta = yaml.safe_load(f)
    with open(pack_dir / "scenarios.yaml", "r", encoding="utf-8") as f:
        scenarios = yaml.safe_load(f)
    with open(pack_dir / "assumptions.yaml", "r", encoding="utf-8") as f:
        assumptions = yaml.safe_load(f)
    with open(root / "registry.yaml", "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    public_api = root / "public" / "api"
    public_api.mkdir(parents=True, exist_ok=True)

    manifest = {
        "pack_meta": pack_meta,
        "scenarios": scenarios["scenarios"],
        "assumptions": assumptions["actuarial_loadings"],
        "registry": registry["packs"]
    }

    with open(public_api / "pack-418.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("Build manifest generated at public/api/pack-418.json")

if __name__ == "__main__":
    build()
