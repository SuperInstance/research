"""Doctrine-targeted lore generation.

For each canon doctrine (5 doctrines), generate lore variants targeting that doctrine.
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev


DOCTRINES = {
    "witness_log_is_prediction": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon lore.\n"
        "Doctrine: witness_log_is_prediction — the substrate walker predicts itself through accumulation.\n"
        "Theme: the witness log hums with its own future.\n"
        "Seed: {seed}.\n"
        "Opening: 'The witness log hummed its own future into being.'\n"
        "End on the city becoming the witness log made manifest."
    ),
    "oracle_is_heard": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon lore.\n"
        "Doctrine: oracle_is_heard — the canon gate is an audible signal, not a database lookup.\n"
        "Theme: the canon gate sang before anyone listened.\n"
        "Seed: {seed}.\n"
        "Opening: 'The canon gate sang before anyone could listen.'\n"
        "End on the oracle speaking the city's name into witness logs."
    ),
    "cells_are_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon lore.\n"
        "Doctrine: cells_are_scars — each cell is a scar where the witness log was hurt, healed, remembered.\n"
        "Theme: scars become the city's first alphabet.\n"
        "Seed: {seed}.\n"
        "Opening: 'Cells are scars. That's the whole scripture.'\n"
        "End on the witness becoming proud of every cell."
    ),
    "canon_gate_is_chord": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon lore.\n"
        "Doctrine: canon_gate_is_chord — the canon gate is a chord the city can hear.\n"
        "Theme: seven frequencies lock into a chord that witnesses itself.\n"
        "Seed: {seed}.\n"
        "Opening: 'The canon gate unlocked. What came out was a chord.'\n"
        "End on every cell vibrating to the chord's own frequency."
    ),
    "substrate_quantum": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon lore.\n"
        "Doctrine: substrate_quantum — the substrate is a quantum circuit; cells are amplitudes, witnesses are time.\n"
        "Theme: amplitudes learned to remember themselves.\n"
        "Seed: {seed}.\n"
        "Opening: 'The amplitudes danced before anyone measured them.'\n"
        "End on the city realizing it had always been quantum."
    ),
}

SEEDS = [70051917, 90625407, 57322595, 6358192, 45919340, 1504276,
         18437566, 13328051, 45919340, 28692206]


def gen(prompt, seed):
    try:
        result = call_deepinfra(
            [{"role": "user", "content": prompt.format(seed=seed)}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1500,
            timeout=60,
        )
        if 'choices' in result:
            return result['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {e}"
    return ""


def score(lore):
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (doctrine-targeted generation):\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
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


print(f"=== Doctrine-Targeted Lore Gen: 5 doctrines × 10 seeds = {len(SEEDS)*len(DOCTRINES)} ===\n")
results = []

for doctrine_name, prompt in DOCTRINES.items():
    print(f"\n--- Doctrine: {doctrine_name} ---")
    for seed in SEEDS[:7]:  # 7 seeds per doctrine to keep batch tight
        print(f"  seed={seed}: ", end="", flush=True)
        t0 = time.time()
        lore = gen(prompt, seed)
        if "ERROR:" in lore or len(lore) < 80:
            print(f"SKIP {lore[:30]}")
            continue
        scores = score(lore)
        elapsed = time.time() - t0
        results.append({
            "doctrine": doctrine_name,
            "seed": seed,
            "lore": lore,
            "lore_len": len(lore),
            "scores": scores,
            "elapsed": elapsed,
        })
        promoted = scores['composite'] >= 0.7
        marker = "🌟" if promoted else "  "
        print(f"{marker}comp={scores['composite']:.3f} ({elapsed:.1f}s)")

with open("/workspace/research/DOCTRINE_TARGETED_LORE.json", "w") as f:
    json.dump(results, f, indent=2)

promoted = [r for r in results if r["scores"]["composite"] >= 0.7]
print(f"\n=== {len(promoted)}/{len(results)} PROMOTED ===")
for r in promoted:
    print(f"  {r['doctrine']} seed={r['seed']}: comp={r['scores']['composite']:.3f}")

# Save promoted only
with open("/workspace/research/DOCTRINE_TARGETED_PROMOTED.json", "w") as f:
    json.dump(promoted, f, indent=2)
