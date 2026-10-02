"""JEV stability probe on the recently promoted lore_inbox cells."""
import sys, json, time
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

manifest = json.load(open('/workspace/research/substrate-walker/canon/cells/manifest.json'))
recent_cells = [e for e in manifest['entries'] if e.get('rank', 0) >= 160 and e.get('rank', 0) <= 168]
print(f"Probing {len(recent_cells)} recent cells for stability...")

results = []
for cell in recent_cells:
    rank = cell['rank']
    lore = cell.get('lore', '')
    if not lore:
        continue
    
    scores = []
    for probe in [1, 2]:
        try:
            r = call_jev(
                f"Quilt substrate walker canon lore (stability probe cell {rank}):\n\n{lore[:1500]}",
                {
                    "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                    "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                    "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
                },
                timeout=30,
            )
            a = r.get("answers", {})
            scores.append((a.get("canon_worthy", {}).get("noul", 0) +
                          a.get("distinct_voice", {}).get("noul", 0) +
                          a.get("doctrine_anchor", {}).get("noul", 0)) / 3)
        except Exception as e:
            scores.append(0)
    
    composite_1 = scores[0] if scores else 0
    composite_2 = scores[1] if len(scores) > 1 else 0
    stable = composite_1 >= 0.7 and composite_2 >= 0.7
    variance = abs(composite_1 - composite_2)
    marker = "★" if stable else " "
    print(f"{marker} Cell {rank}: comp1={composite_1:.3f} comp2={composite_2:.3f} stable={stable}")
    results.append({
        "rank": rank,
        "voice": cell.get('voice'),
        "composite_1": composite_1,
        "composite_2": composite_2,
        "stable": stable,
        "variance": variance,
    })
    time.sleep(1)

stable_count = sum(1 for r in results if r['stable'])
print(f"\n{stable_count}/{len(results)} canon-stable on twin-probe")

with open('/workspace/research/STABILITY_PROBE_RECENT.json', 'w') as f:
    json.dump({"results": results, "stable_count": stable_count, "total": len(results)}, f, indent=2)
