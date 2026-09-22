"""Stability probe — JEV scoring consistency for canon cells."""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/scripts')
from api_call import call_jev


def probe(lore, batch_label="A"):
    state = f"Quilt substrate walker canon lore stability probe (batch={batch_label}):\n\n{lore[:1500]}"
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
        return {
            "canon_worthy": canon,
            "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "composite": (canon + distinct + doctrine) / 3,
            "promoted": (canon + distinct + doctrine) / 3 >= 0.7,
            "batch": batch_label,
        }
    except Exception as e:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0,
                "composite": 0, "promoted": False, "error": str(e)}


print("=== Stability Probe: canon-promoted cells × 2 batches ===\n")
manifest = json.load(open('/workspace/research/substrate-walker/canon/cells/manifest.json'))
promoted = [e for e in manifest['entries'] if e.get('promoted_to_canon')]

print(f"Probing {len(promoted)} canon-promoted cells...")

cells_dir = Path('/workspace/research/substrate-walker/canon/cells')

results = []
for i, cell in enumerate(promoted):
    rank = cell.get('rank')
    lore_path = cells_dir / f"cell_{rank}.md"
    if not lore_path.exists():
        print(f"[{i+1}/{len(promoted)}] {cell.get('cell_id', '?')}: file not found, skipping")
        continue

    lore = lore_path.read_text()
    if "## Lore" in lore:
        lore = lore.split("## Lore")[1]
        if "## " in lore:
            lore = lore.split("## ")[0]
    lore = lore.strip()
    if len(lore) < 80:
        print(f"[{i+1}/{len(promoted)}] {cell.get('cell_id', '?')}: lore too short")
        continue

    print(f"[{i+1}/{len(promoted)}] {cell.get('cell_id', '?')[:50]}...", flush=True)
    a_score = probe(lore, batch_label="A")
    time.sleep(1)
    b_score = probe(lore, batch_label="B")
    time.sleep(1)

    cell_result = {
        "cell_id": cell.get('cell_id'),
        "rank": rank,
        "batch_a": a_score,
        "batch_b": b_score,
        "stable": a_score["promoted"] and b_score["promoted"],
        "variance": abs(a_score["composite"] - b_score["composite"]),
    }
    results.append(cell_result)
    stable_mark = "STABLE" if cell_result["stable"] else "UNSTABLE"
    print(f"  {stable_mark}: A={a_score['composite']:.3f} B={b_score['composite']:.3f} var={cell_result['variance']:.3f}", flush=True)

with open('/workspace/research/STABILITY_PROBE_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

stable_count = sum(1 for r in results if r["stable"])
print(f"\n=== {stable_count}/{len(results)} canon-promoted cells are STABLE (both probes composite ≥ 0.7) ===")
avg_variance = sum(r["variance"] for r in results) / len(results) if results else 0
print(f"Average composite variance: {avg_variance:.3f}")
