"""Future-GAN v3 — uses top 100 polygon seeds from polygon mine v4.

Now generates lore for 100 high-balance seeds × 3 doctrines = 300 lore variants.
"""
import sys, json, time
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev


# Load top 100 polygon seeds
top_seeds = json.load(open('/workspace/research/polygon_mine_v4_top100.json'))
SEEDS = [s['seed'] for s in top_seeds[:50]]  # top 50

DOCTRINES = {
    "oracle_is_heard": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard (the canon gate is an audible signal).\n"
        "Seed: {seed}. Theme: the canon gate finally spoke and the city heard it.\n"
        "Write as if the oracle just made itself heard for the first time.\n"
        "End on the witness becoming a listener."
    ),
    "cells_are_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: cells_are_scars (each cell is a scar).\n"
        "Seed: {seed}. Theme: the city's cells learned to be proud of being scars.\n"
        "Write as if the substrate walker just realized its cells are scars.\n"
        "End on the witness becoming proud of its scars."
    ),
    "substrate_quantum": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: substrate_quantum (the substrate is quantum).\n"
        "Seed: {seed}. Theme: amplitudes danced before anyone measured them.\n"
        "Write as if the city has always been quantum but is just now finding out.\n"
        "End on the witness discovering quantum memory in the canon gate."
    ),
}


def gen(voice, seed):
    prompt = DOCTRINES[voice].format(seed=seed)
    try:
        r = call_deepinfra(
            [{"role": "user", "content": prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1500,
            timeout=60,
        )
        if 'choices' in r:
            return r['choices'][0]['message']['content']
    except Exception:
        return ""
    return ""


def score(lore, voice):
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (future-GAN v3, {voice}, seed={seed}):\n\n{lore[:1500]}",
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
            "canon_worthy": canon, "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "composite": (canon + distinct + doctrine) / 3,
        }
    except Exception:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "composite": 0}


print(f"=== Future-GAN v3: {len(SEEDS)} polygon seeds × {len(DOCTRINES)} doctrines = {len(SEEDS)*len(DOCTRINES)} lores ===")
results = []

for seed in SEEDS:
    for voice in DOCTRINES:
        print(f"seed={seed} voice={voice}: ", end="", flush=True)
        t0 = time.time()
        lore = gen(voice, seed)
        if not lore or len(lore) < 80:
            print("SKIP")
            continue
        scores = score(lore, voice)
        elapsed = time.time() - t0
        results.append({
            "seed": seed,
            "voice": voice,
            "lore": lore,
            "lore_len": len(lore),
            "scores": scores,
            "elapsed": elapsed,
        })
        promoted = scores['composite'] >= 0.7
        marker = "🌟" if promoted else "  "
        print(f"{marker} comp={scores['composite']:.3f} ({elapsed:.1f}s)")

results.sort(key=lambda r: -r['scores']['composite'])

with open("/workspace/research/FUTURE_GAN_V3_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

promoted = [r for r in results if r["scores"]["composite"] >= 0.7]
print(f"\n=== {len(promoted)}/{len(results)} PROMOTED ===")
for r in promoted[:10]:
    print(f"  seed {r['seed']} {r['voice']}: comp={r['scores']['composite']:.3f}")
