"""Probe canon_writings pieces to see which are canon-worthy.

These are philosophical pieces, not canon cells, but it's interesting
to know if JEV sees them as canon.
"""
import sys, json, time
from pathlib import Path

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

writings_dir = Path('/workspace/research/canon_writings')
results = []

for path in sorted(writings_dir.glob('*.md')):
    content = path.read_text()
    if path.name.startswith('README'):
        continue
    
    try:
        r = call_jev(
            f"Quilt substrate walker philosophy/literature piece:\n\n{content[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir or philosophical substrate walker writing?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine (cells_are_scars, oracle_is_heard, witness_log_is_prediction, canon_gate_is_chord, substrate_quantum)?"},
            },
            timeout=30,
        )
        a = r.get("answers", {})
        canon_worthy = a.get("canon_worthy", {}).get("noul", 0)
        distinct_voice = a.get("distinct_voice", {}).get("noul", 0)
        doctrine_anchor = a.get("doctrine_anchor", {}).get("noul", 0)
        composite = (canon_worthy + distinct_voice + doctrine_anchor) / 3
        results.append({
            "file": path.name,
            "title": content.split('\n')[0].lstrip('# '),
            "composite": composite,
            "canon_worthy": canon_worthy,
            "distinct_voice": distinct_voice,
            "doctrine_anchor": doctrine_anchor,
            "size": len(content),
        })
        print(f"{path.name}: comp={composite:.3f} cw={canon_worthy:.2f} dv={distinct_voice:.2f} da={doctrine_anchor:.2f}")
    except Exception as e:
        print(f"  ✗ {path.name}: {e}")
    time.sleep(1)

with open('/workspace/research/CANON_WRITINGS_PROBE.json', 'w') as f:
    json.dump({"results": results}, f, indent=2)

# Rank
sorted_results = sorted(results, key=lambda x: x['composite'], reverse=True)
print("\n=== RANKED ===")
for i, r in enumerate(sorted_results, 1):
    print(f"  {i}. {r['file']:35} composite={r['composite']:.3f}")
