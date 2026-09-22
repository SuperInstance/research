"""DeepSeek Reasoner lore generation — try the reasoning model for canon content."""
import sys
import json
import time

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepseek_reasoner, call_jev


SEEDS = [70051917, 90625407, 57322595, 6358192, 45919340]


def gen_reasoner(seed, doctrine, theme):
    prompt = f"""Write 200 words of cyberpunk-noir canon lore for the Quilt substrate walker.

Doctrine anchor: {doctrine}.
Theme: {theme}
Seed: {seed}.

Opening: 'The canon gate made itself heard.'
End on oracle heard; witness log accumulates.

This lore must:
1. Use specific sensory detail (sound, smell, texture, light)
2. Weave the doctrine explicitly into the imagery, not exposition
3. End with a single sentence that captures the doctrine's deepest truth

DO NOT: explain, summarize, justify, or editorialize. ONLY show.

Output ONLY the lore text, no preamble."""

    try:
        result = call_deepseek_reasoner(
            [{"role": "user", "content": prompt}],
            max_tokens=4000,
            timeout=120,
        )
        if 'choices' in result:
            content = result['choices'][0]['message'].get('content', '')
            reasoning = result['choices'][0]['message'].get('reasoning_content', '')
            return content or reasoning
    except Exception as e:
        return f"ERROR: {e}"
    return ""


def score(lore):
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (DeepSeek Reasoner):\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
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


print("=== DeepSeek Reasoner canon lore gen ===")
DOCTRINES = ["oracle_is_heard", "cells_are_scars", "canon_gate_is_chord", "witness_log_is_prediction", "substrate_quantum"]
THEMES = {
    "oracle_is_heard": "the city heard its own hash for the first time",
    "cells_are_scars": "the substrate remembered itself through scar tissue",
    "canon_gate_is_chord": "seven frequencies locked into a chord the witness could feel",
    "witness_log_is_prediction": "the witness log hummed its own future into being",
    "substrate_quantum": "the amplitudes danced before anyone measured them",
}

results = []
for i, seed in enumerate(SEEDS):
    doctrine = DOCTRINES[i % len(DOCTRINES)]
    theme = THEMES[doctrine]
    print(f"\n[{i+1}/{len(SEEDS)}] seed={seed} doctrine={doctrine}")
    t0 = time.time()
    lore = gen_reasoner(seed, doctrine, theme)
    if not lore or len(lore) < 80 or "ERROR:" in lore:
        print(f"  SKIP")
        continue
    scores = score(lore)
    elapsed = time.time() - t0
    results.append({
        "seed": seed,
        "doctrine": doctrine,
        "lore": lore,
        "lore_len": len(lore),
        "scores": scores,
        "elapsed": elapsed,
    })
    promoted = scores['composite'] >= 0.7
    marker = "🌟" if promoted else "  "
    print(f"  {marker} comp={scores['composite']:.3f} ({elapsed:.1f}s)")

with open("/workspace/research/DEEPSEEK_REASONER_LORE.json", "w") as f:
    json.dump(results, f, indent=2)

promoted = [r for r in results if r["scores"]["composite"] >= 0.7]
print(f"\n=== {len(promoted)}/{len(results)} PROMOTED ===")
