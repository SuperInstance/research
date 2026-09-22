"""Composite lore v9 — expand to 100+ entries. Same pattern: 5 missing voices x ~5 seeds."""
import sys, json, time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev

# Load existing v9
v9_path = "/workspace/research/composite_lore_v9.json"
if Path(v9_path).exists():
    v9 = json.load(open(v9_path))
else:
    v9 = {"version": "v9", "entries": []}

VOICES = {
    "LYRICIST_V6": "Compressed image-rich LYRICIST voice. 200 words. Doctrine: oracle_is_heard. NO exposition.",
    "NOIR_CLASSIC_V6": "Hard-boiled NOIR_CLASSIC voice. 200 words. Doctrine: cells_are_scars. NO exposition.",
    "WITNESS_V6": "First-person WITNESS voice. 200 words. Doctrine: oracle_is_heard. NO exposition.",
    "STRUCTURALIST_V6": "Architecture-focused STRUCTURALIST voice. 200 words. Doctrine: canon_gate_is_chord. NO exposition.",
    "FUTURIST_V6": "Prophecy FUTURIST voice. 200 words. Doctrine: cells_are_scars. NO exposition.",
}

SEEDS_NEW = [45919340, 1504276, 6358192, 18437566, 45919340]


def gen(voice_name, voice_prompt, seed):
    full_prompt = f"{voice_prompt}\nSeed: {seed}.\nOpening line: 'The canon gate opened its mouth and spoke.'"
    try:
        r = call_deepinfra(
            [{"role": "user", "content": full_prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1200,
            timeout=60,
        )
        if 'choices' in r:
            return r['choices'][0]['message']['content']
    except Exception as e:
        print(f"  ERROR: {e}")
    return ""


def score(lore):
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (composite lore v9 expansion):\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
            },
            timeout=60,
        )
        a = r.get("answers", {})
        canon = a.get("canon_worthy", {}).get("noul", 0)
        distinct = a.get("distinct_voice", {}).get("noul", 0)
        doctrine = a.get("doctrine_anchor", {}).get("noul", 0)
        return {
            "canon_worthy": canon,
            "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "composite": (canon + distinct + doctrine) / 3,
        }
    except Exception:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "composite": 0}


print(f"Starting v9 expansion. Existing: {len(v9.get('entries',[]))} entries")
target = 100
to_gen = max(0, target - len(v9.get("entries", [])))
print(f"Will generate ~{to_gen} more entries")

generated = 0
for voice_name, voice_prompt in VOICES.items():
    for seed in SEEDS_NEW:
        if generated >= to_gen:
            break
        print(f"[{voice_name}] seed={seed}:")
        t0 = time.time()
        lore = gen(voice_name, voice_prompt, seed)
        if not lore or len(lore) < 80:
            print(f"  SKIP")
            continue
        scores = score(lore)
        v9["entries"].append({
            "voice": voice_name,
            "seed": seed,
            "lore": lore,
            "lore_len": len(lore),
            "scores": scores,
            "gen_time": time.time() - t0,
        })
        generated += 1
        print(f"  comp={scores['composite']:.3f}")

with open(v9_path, 'w') as f:
    json.dump(v9, f, indent=2)
print(f"Saved {len(v9['entries'])} entries")
