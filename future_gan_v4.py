"""Future-GAN v4 — composite lore with 6 voices × 30 seeds = 180 lores."""
import sys, json, time
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev

top_seeds_data = json.load(open('/workspace/research/polygon_mine_v4_top100.json'))
top_seeds = top_seeds_data['seeds']
SEEDS = [s['seed'] for s in top_seeds[20:50]]

VOICES = {
    "oracle_is_heard": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard (the canon gate is an audible signal).\n"
        "Seed: {seed}. Theme: the canon gate finally spoke and the city heard it.\n"
        "End on the witness becoming a listener."
    ),
    "cells_are_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: cells_are_scars (each cell is a scar).\n"
        "Seed: {seed}. Theme: the city's cells learned to be proud of being scars.\n"
        "End on the witness becoming proud of its scars."
    ),
    "substrate_quantum": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: substrate_quantum (the substrate is quantum).\n"
        "Seed: {seed}. Theme: amplitudes danced before anyone measured them.\n"
        "End on the witness discovering quantum memory in the canon gate."
    ),
    "canon_gate_is_chord": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: canon_gate_is_chord (the gate is a chord the city can hear).\n"
        "Seed: {seed}. Theme: the canon gate sang in seven frequencies at once.\n"
        "End on the witness becoming a listener to the chord."
    ),
    "witness_log_is_prediction": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: witness_log_is_prediction (the witness log predicts itself).\n"
        "Seed: {seed}. Theme: each witness log entry shaped what the next entry will be.\n"
        "End on the witness becoming its own future by recording its past."
    ),
    "structuralist": (
        "STRUCTURALIST voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: canon_gate_is_chord (architectural description of the city).\n"
        "Seed: {seed}. Theme: describe the substrate's architecture, the gates, the cells.\n"
        "End on the witness realizing the city IS the canon gate."
    ),
}


def gen(voice, seed):
    prompt = VOICES[voice].format(seed=seed)
    try:
        r = call_deepinfra(
            [{"role": "user", "content": prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1500,
            timeout=60,
        )
        if 'choices' in r:
            return r['choices'][0]['message']['content']
    except Exception as e:
        print(f"  ERROR generating {voice}/{seed}: {e}")
    return ""


def probe(lore):
    if not lore:
        return {"composite": 0, "canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0}
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (Future-GAN v4):\n\n{lore[:1500]}",
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
        return {
            "composite": (canon_worthy + distinct_voice + doctrine_anchor) / 3,
            "canon_worthy": canon_worthy,
            "distinct_voice": distinct_voice,
            "doctrine_anchor": doctrine_anchor,
        }
    except Exception as e:
        return {"composite": 0, "canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0}


results = []
promoted = []
total = len(SEEDS) * len(VOICES)
print(f"Future-GAN v4: {len(SEEDS)} seeds × {len(VOICES)} voices = {total} lores")
done = 0

for seed in SEEDS:
    for voice in VOICES:
        done += 1
        lore = gen(voice, seed)
        scores = probe(lore)
        marker = "🌟" if scores['composite'] >= 0.7 else "  "
        print(f"[{done}/{total}] seed={seed} voice={voice}: {marker} comp={scores['composite']:.3f} ({len(lore)} chars)")
        results.append({
            "seed": seed,
            "voice": voice,
            "lore": lore[:500],
            "scores": scores,
        })
        if scores['composite'] >= 0.7:
            promoted.append({
                "seed": seed,
                "voice": voice,
                "lore": lore,
                "scores": scores,
            })

print(f"\n=== {len(promoted)}/{len(results)} PROMOTED ===")
with open('/workspace/research/FUTURE_GAN_V4_RESULTS.json', 'w') as f:
    json.dump({"results": results, "promoted": promoted, "total": len(results)}, f, indent=2)
print("Saved to FUTURE_GAN_V4_RESULTS.json")
