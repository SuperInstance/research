"""Retry JEV probes on lore_inbox files until they succeed."""
import sys, json, time, os
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_jev

lore_dir = '/workspace/research/lore_inbox'
results = []
processed_marker = '/workspace/research/lore_inbox/.processed'

# Load processed
processed = set()
if os.path.exists(processed_marker):
    processed = set(json.load(open(processed_marker)))

for fname in sorted(os.listdir(lore_dir)):
    if not fname.endswith('.md'):
        continue
    if fname in processed:
        continue

    with open(os.path.join(lore_dir, fname)) as f:
        content = f.read()

    # Extract lore
    if '## Lore' in content:
        lore = content.split('## Lore', 1)[1].strip()
    elif '\n\n' in content:
        lore = content.split('\n\n', 1)[1].strip()
    else:
        lore = content

    if len(lore) < 100:
        print(f"  Skip {fname} (too short)")
        processed.add(fname)
        continue

    # Try probe with retries
    success = False
    for attempt in range(3):
        try:
            r = call_jev(
                f"Quilt substrate walker canon lore:\n\n{lore[:1500]}",
                {
                    "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                    "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                    "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
                },
                timeout=60,
            )
            a = r.get("answers", {})
            canon_worthy = a.get("canon_worthy", {}).get("noul", 0)
            distinct_voice = a.get("distinct_voice", {}).get("noul", 0)
            doctrine_anchor = a.get("doctrine_anchor", {}).get("noul", 0)
            composite = (canon_worthy + distinct_voice + doctrine_anchor) / 3
            results.append({
                "file": fname,
                "lore": lore[:300],
                "composite": composite,
                "canon_worthy": canon_worthy,
                "distinct_voice": distinct_voice,
                "doctrine_anchor": doctrine_anchor,
            })
            marker = "🌟" if composite >= 0.7 else "  "
            print(f"{marker} {fname}: comp={composite:.3f}")
            success = True
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(10)
    
    if not success:
        print(f"  ✗ {fname}: skipped after 3 attempts")
    
    processed.add(fname)
    
    # Save processed marker
    with open(processed_marker, 'w') as f:
        json.dump(sorted(processed), f, indent=2)
    
    time.sleep(2)

with open('/workspace/research/JEV_RETRY_PROBE_RESULTS.json', 'w') as f:
    json.dump({"results": results, "total": len(results), "promoted": sum(1 for r in results if r['composite'] >= 0.7)}, f, indent=2)

promoted = sum(1 for r in results if r['composite'] >= 0.7)
print(f"\n=== {promoted}/{len(results)} PROMOTED ===")
