"""Stability probe for the latest auto-promoted cells 144, 145."""
import sys, json, time
sys.path.insert(0, '/workspace/research/substrate-walker/scripts')
from api_call import call_jev


def probe(lore, batch='A'):
    state = f"Stability probe batch {batch}: {lore[:1500]}"
    questions = {
        "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
        "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
        "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
    }
    try:
        result = call_jev(state, questions, timeout=60)
        a = result.get("answers", {})
        canon = a.get("canon_worthy", {}).get("noul", 0)
        distinct = a.get("distinct_voice", {}).get("noul", 0)
        doctrine = a.get("doctrine_anchor", {}).get("noul", 0)
        composite = (canon + distinct + doctrine) / 3
        return {"composite": composite, "canon": canon, "distinct": distinct, "doctrine": doctrine, "promoted": composite >= 0.7}
    except Exception:
        return {"composite": 0}


print("=== Stability probe for cells 144-145 ===")
cells = [144, 145]
for rank in cells:
    lore = open(f'/workspace/research/substrate-walker/canon/cells/cell_{rank}.md').read()
    if '## Lore' in lore:
        lore = lore.split('## Lore')[1]
        if '## ' in lore:
            lore = lore.split('## ')[0]
    lore = lore.strip()

    a = probe(lore, batch='A')
    time.sleep(1)
    b = probe(lore, batch='B')
    print(f"rank {rank}: A={a['composite']:.3f} B={b['composite']:.3f} {'STABLE' if a['promoted'] and b['promoted'] else 'UNSTABLE'}")

with open('/workspace/research/CELLS_144_145_STABILITY.json', 'w') as f:
    json.dump({"cells": [{"rank": r, "A": probe(lore, 'A'), "B": probe(lore, 'B')} for r in cells for lore in [None]}, f, indent=2)
