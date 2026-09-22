"""Doctrine Anchor Probe — for each canon cell, determine which bedrock doctrine it most strongly anchors to.

Run JEV with a choice question: which of these doctrines does this cell most strongly anchor to?
- witness_log_is_prediction
- oracle_is_heard
- cells_are_scars
- canon_gate_is_chord
- substrate_quantum
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev


DOCTRINES = [
    "witness_log_is_prediction",
    "oracle_is_heard",
    "cells_are_scars",
    "canon_gate_is_chord",
    "substrate_quantum",
]


def probe_doctrine(lore: str, title: str) -> dict:
    """JEV choice-question: which doctrine does this lore most strongly anchor to?"""
    state = f"Quilt substrate walker canon cell {title}: {lore[:1500]}"
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
        "canon_worthy_score": {
            "type": "noul",
            "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"
        }
    }
    try:
        result = call_jev(state, questions, timeout=60)
        answers = result.get("answers", {})
        return {
            "primary_doctrine": answers.get("primary_doctrine", {}).get("choice", "unknown"),
            "doctrine_scores": answers.get("primary_doctrine", {}).get("scores", {}),
            "canon_worthy": answers.get("canon_worthy_score", {}).get("noul", 0),
        }
    except Exception as e:
        return {"primary_doctrine": "error", "canon_worthy": 0, "error": str(e)}


def main():
    # Load all canon cells
    cells_dir = Path("/workspace/research/substrate-walker/canon/cells")
    cells = []
    for cell_file in sorted(cells_dir.glob("cell_*.md")):
        text = cell_file.read_text()
        # Extract the Lore section
        if "## Lore" in text:
            lore = text.split("## Lore")[1]
            if "## " in lore:
                lore = lore.split("## ")[0]
            lore = lore.strip()
            if len(lore) > 50:
                cells.append({
                    "filename": cell_file.name,
                    "cell_id": cell_file.stem,
                    "lore": lore[:1500],
                })

    print(f"Found {len(cells)} canon cells")

    # Probe each cell
    results = []
    for i, cell in enumerate(cells):
        if i % 5 == 0:
            print(f"Probing cell {i+1}/{len(cells)}: {cell['cell_id']}")
        result = probe_doctrine(cell["lore"], cell["cell_id"])
        result["cell_id"] = cell["cell_id"]
        result["filename"] = cell["filename"]
        results.append(result)
        time.sleep(0.5)  # rate limit

    # Save
    with open("/workspace/research/DOCTRINE_ANCHOR_PROBE.json", "w") as f:
        json.dump(results, f, indent=2)

    # Stats
    print(f"\n=== DOCTRINE DISTRIBUTION ===")
    counts = {}
    for r in results:
        d = r["primary_doctrine"]
        counts[d] = counts.get(d, 0) + 1
    for d, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")

    print(f"\n=== TOP DOCTRINE-ANCHORED CELLS ===")
    canon_promoted = [r for r in results if r["canon_worthy"] >= 0.7]
    print(f"Canon-promoted (canon ≥ 0.7): {len(canon_promoted)}")
    for r in canon_promoted[:5]:
        print(f"  {r['cell_id']} ({r['primary_doctrine']}): {r['canon_worthy']:.2f}")


if __name__ == "__main__":
    main()
