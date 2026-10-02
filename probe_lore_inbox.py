"""Probe all lore_inbox files with JEV (now using curl-based api_call)."""
import sys, json, time, os
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

lore_dir = '/workspace/research/lore_inbox'
results = []

# Skip the canon_gate_chord_first_rain.md and oracle_is_heard_canon_gate.md etc which are hand-written canon
# Probe all auto-generated lore
for fname in sorted(os.listdir(lore_dir)):
    if not fname.endswith('.md'):
        continue
    if not fname.startswith('lore_seed'):
        continue
    
    path = os.path.join(lore_dir, fname)
    with open(path) as f:
        content = f.read()
    
    if '\n\n' in content:
        lore = content.split('\n\n', 1)[1].strip()
    else:
        lore = content
    
    if len(lore) < 100:
        continue
    
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore:\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
            },
            timeout=30,
        )
        a = r.get("answers", {})
        canon_worthy = a.get("canon_worthy", {}).get("noul", 0)
        distinct_voice = a.get("distinct_voice", {}).get("noul", 0)
        doctrine_anchor = a.get("doctrine_anchor", {}).get("noul", 0)
        composite = (canon_worthy + distinct_voice + doctrine_anchor) / 3
        results.append({
            "file": fname,
            "composite": composite,
            "canon_worthy": canon_worthy,
            "distinct_voice": distinct_voice,
            "doctrine_anchor": doctrine_anchor,
        })
        marker = "🌟" if composite >= 0.7 else "  "
        print(f"{marker} {fname}: comp={composite:.3f}")
    except Exception as e:
        print(f"  ✗ {fname}: {e}")
    
    time.sleep(0.5)

promoted = sum(1 for r in results if r['composite'] >= 0.7)
print(f"\n=== {promoted}/{len(results)} PROMOTED ===")

with open('/workspace/research/LORE_INBOX_PROBE.json', 'w') as f:
    json.dump({"results": results, "promoted": promoted, "total": len(results)}, f, indent=2)
