"""Probe ALL canon cells with doctrine-anchor probe.

For each canon cell, determine which doctrine it most strongly anchors to.
This gives us a complete doctrine distribution.
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/scripts')
from api_call import call_jev


DOCTRINES = [
    "witness_log_is_prediction",
    "oracle_is_heard",
    "cells_are_scars",
    "canon_gate_is_chord",
    "substrate_quantum",
]


def probe_doctrine(lore, cell_id):
    state = f"Quilt substrate walker canon cell doctrine probe ({cell_id}):\n\n{lore[:1500]}"
    questions = {
        "primary_doctrine": {
            "type": "choice",
            "instructions": "Which canonical doctrine does this lore most strongly anchor to?",
            "criteria": {
                "witness_log_is_prediction": "the witness log is shown to be predicting the canon",
                "oracle_is_heard": "the canon gate is shown to make an audible signal",
                "cells_are_scars": "each cell is shown to be a scar from earlier witness cycles",
                "canon_gate_is_chord": "the canon gate is shown as a chord the city can hear",
                "substrate_quantum": "the substrate is shown to be quantum in nature"
            },
            "choices": DOCTRINES
        },
        "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
        "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
        "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"}
    }
    try:
        result = call_jev(state, questions, timeout=120)
        answers = result.get("answers", {})
        return {
            "primary_doctrine": answers.get("primary_doctrine", {}).get("choice", "?"),
            "doctrine_probabilities": answers.get("primary_doctrine", {}).get("probabilities", {}),
            "canon_worthy": answers.get("canon_worthy", {}).get("noul", 0),
            "distinct_voice": answers.get("distinct_voice", {}).get("noul", 0),
            "doctrine_anchor": answers.get("doctrine_anchor", {}).get("noul", 0),
        }
    except Exception as e:
        return {"primary_doctrine": "?", "canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "error": str(e)}


print("=== FULL DOCTRINE-ANCHOR PROBE (all 133 cells) ===")
manifest = json.load(open('/workspace/research/substrate-walker/canon/cells/manifest.json'))

cells_dir = Path('/workspace/research/substrate-walker/canon/cells')
results = []
for i, cell in enumerate(manifest['entries']):
    rank = cell.get('rank')
    if not rank or rank <= 0:
        continue
    cell_path = cells_dir / f"cell_{rank}.md"
    if not cell_path.exists():
        continue

    lore = cell_path.read_text()
    if "## Lore" in lore:
        lore = lore.split("## Lore")[1]
        if "## " in lore:
            lore = lore.split("## ")[0]
    lore = lore.strip()
    if len(lore) < 50:
        continue

    print(f"[{i+1}/{len(manifest['entries'])}] rank={rank}", flush=True)
    result = probe_doctrine(lore, cell.get("cell_id", f"cell_{rank}"))
    result["rank"] = rank
    result["cell_id"] = cell.get("cell_id", f"cell_{rank}")
    results.append(result)
    time.sleep(0.5)

with open("/workspace/research/FULL_DOCTRINE_PROBE.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n=== Doctrinal Distribution ===")
counts = {}
for r in results:
    d = r.get("primary_doctrine", "?")
    counts[d] = counts.get(d, 0) + 1
for d, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c}")
