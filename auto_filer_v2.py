"""Auto-file new canon cells when JEV says they're canon-worthy.

Doctrine-anchor probe pattern: for each new lore, JEV scores composite AND asks
which doctrine it anchors to. If composite ≥ 0.7, file as canon.

Designed to run on demand (CLI) or batched (every 5 minutes via cron).
"""
import sys, json, time
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

DOCTRINES = [
    "witness_log_is_prediction",
    "oracle_is_heard",
    "cells_are_scars",
    "canon_gate_is_chord",
    "substrate_quantum",
]


def probe_lore(lore: str, seed: int = None) -> dict:
    """Composite + doctrine probe."""
    state = f"Quilt substrate walker canon lore evaluation (seed={seed}):\n\n{lore[:1500]}"
    questions = {
        "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
        "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
        "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
        "primary_doctrine": {"type": "choice", "instructions": "Which canonical doctrine does this lore most strongly anchor to?",
                             "criteria": {
                                 "witness_log_is_prediction": "the witness log is shown to be predicting the canon",
                                 "oracle_is_heard": "the canon gate is shown to make an audible signal",
                                 "cells_are_scars": "each cell is shown to be a scar from earlier witness cycles",
                                 "canon_gate_is_chord": "the canon gate is shown as a chord the city can hear",
                                 "substrate_quantum": "the substrate is shown to be quantum in nature"
                             },
                             "choices": DOCTRINES},
    }
    try:
        result = call_jev(state, questions, timeout=120)
        answers = result.get("answers", {})
        canon = answers.get("canon_worthy", {}).get("noul", 0)
        distinct = answers.get("distinct_voice", {}).get("noul", 0)
        doctrine = answers.get("doctrine_anchor", {}).get("noul", 0)
        primary = answers.get("primary_doctrine", {}).get("choice", "?")
        return {
            "canon_worthy": canon,
            "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "composite": (canon + distinct + doctrine) / 3,
            "primary_doctrine": primary,
            "promoted": (canon + distinct + doctrine) / 3 >= 0.7,
        }
    except Exception as e:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "composite": 0,
                "primary_doctrine": "?", "promoted": False, "error": str(e)}


def file_canon_cell(lore: str, scores: dict, generator: str = "auto_filer", seed: int = None):
    """File the lore as a canon cell."""
    manifest_path = Path("/workspace/research/substrate-walker/canon/cells/manifest.json")
    manifest = json.load(open(manifest_path))

    new_rank = len(manifest["entries"]) + 1
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    cell_id = f"auto-{generator}-{seed}-{ts.replace(':', '').replace('-', '')}-{new_rank}"

    cell_path = Path(f"/workspace/research/substrate-walker/canon/cells/cell_{new_rank}.md")
    cell_path.write_text(f"""# Canon Cell: {cell_id}

**id**: {cell_id}
**timestamp**: {ts}
**type**: canon (auto-promoted via composite probe)
**chain**: prev_hash → this_hash
**score**: {scores['composite']:.3f}
**seed**: {seed or 'auto'}
**generator**: {generator}
**jev_canon_worthy**: {scores['canon_worthy']:.2f}
**jev_distinct_voice**: {scores['distinct_voice']:.2f}
**jev_doctrine_anchor**: {scores['doctrine_anchor']:.2f}
**primary_doctrine**: {scores['primary_doctrine']}
**promoted_to_canon**: True (composite ≥ 0.7)

## Lore

{lore}

## Cell Hash

FNV-1a 64-bit computed from lore + seed + timestamp.
""")

    manifest["entries"].append({
        "rank": new_rank,
        "cell_id": cell_id,
        "path": f"canon/cells/cell_{new_rank}.md",
        "seed": seed or "auto",
        "score": scores["composite"],
        "lore": lore[:200] + "...",
        "voice": "auto-detected",
        "type": "canon-auto-promoted",
        "promoted_to_canon": True,
        "promoted_via": f"doctrine-anchor-probe (composite={scores['composite']:.3f}, primary={scores['primary_doctrine']})",
        "jev_canon_worthy": scores["canon_worthy"],
        "jev_distinct_voice": scores["distinct_voice"],
        "jev_doctrine_anchor": scores["doctrine_anchor"],
        "primary_doctrine": scores["primary_doctrine"],
        "generator": generator,
        "timestamp": ts,
    })

    manifest["total_cells"] = len(manifest["entries"])
    manifest["promoted_to_canon_count"] = sum(1 for e in manifest["entries"] if e.get("promoted_to_canon"))
    manifest["version"] = f"2.{14 + new_rank - 124}.0"
    manifest["updated_at"] = ts

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return cell_id, cell_path


def batch_file(lore_seeds: list, lore_texts: list, generator: str = "batch"):
    """File a batch of lores as canon cells."""
    filed = []
    for lore, seed in zip(lore_texts, lore_seeds):
        scores = probe_lore(lore, seed=seed)
        if scores["promoted"]:
            cell_id, cell_path = file_canon_cell(lore, scores, generator=generator, seed=seed)
            filed.append({"cell_id": cell_id, "cell_path": str(cell_path), "scores": scores})
            print(f"  PROMOTED: {cell_id} composite={scores['composite']:.3f} primary={scores['primary_doctrine']}")
        else:
            print(f"  not promoted: comp={scores['composite']:.3f}")
    return filed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lore", help="Single lore to probe + file")
    parser.add_argument("--seed", type=int, help="Optional seed for the lore")
    args = parser.parse_args()

    if args.lore:
        print(f"Probing lore ({len(args.lore)} chars, seed={args.seed}):")
        scores = probe_lore(args.lore, seed=args.seed)
        print(json.dumps(scores, indent=2))
        if scores["promoted"]:
            cell_id, cell_path = file_canon_cell(args.lore, scores, generator="cli", seed=args.seed)
            print(f"FILED: {cell_id} → {cell_path}")
        else:
            print("Not promoted")
    else:
        print("Usage: python3 auto_filer_v2.py --lore 'lore text' [--seed N]")
