"""GAN-style adversarial lore improvement.

Generator: produces lore variants for a seed
Discriminator: JEV scores canon_worthy, distinct_voice, doctrine_anchor
Improver: passes the discriminator's choice question back to generator
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev, call_zai


SEEDS = [70051917, 90625407, 57322595, 6358192, 45919340, 1504276]


def gen_with_feedback(seed, feedback, voice="witness", temperature=0.9):
    """Generator takes feedback from previous JEV probe."""
    prompt = f"""WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.

Doctrine anchor: oracle_is_heard.
Seed: {seed}.

CRITICAL — JEV feedback to incorporate:
{feedback}

Opening line: "I heard the canon gate before I saw it."
End on: oracle heard; witness log accumulates."""
    try:
        r = call_deepinfra(
            [{"role": "user", "content": prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1200,
            timeout=60,
            temperature=temperature,
        )
        if 'choices' in r:
            return r['choices'][0]['message']['content']
    except Exception as e:
        print(f"  GEN ERROR: {e}")
    return ""


def score(lore):
    """Discriminator: JEV scoring."""
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore (GAN iteration):\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored to substrate walker?"},
                "distinct_because": {"type": "noul", "instructions": "Distinct from the seed's other lore variants?"},
                "improve_aspect": {"type": "choice", "instructions": "Which aspect most needs improvement?",
                                   "criteria": {
                                       "voice_distinctness": "the voice blends with other lores; needs more unique cadence or rhythm",
                                       "doctrine_depth": "the doctrine anchor is mentioned but not deeply embodied in the narrative",
                                       "image_specificity": "the imagery is too abstract or generic; needs concrete sensory detail",
                                       "narrative_arc": "the structure is flat; no tension or surprise",
                                       "opening_strength": "the opening line is weak or exposition-heavy"
                                   },
                                   "choices": ["voice_distinctness", "doctrine_depth", "image_specificity", "narrative_arc", "opening_strength"]},
            },
            timeout=60,
        )
        a = r.get("answers", {})
        canon = a.get("canon_worthy", {}).get("noul", 0)
        distinct = a.get("distinct_voice", {}).get("noul", 0)
        doctrine = a.get("doctrine_anchor", {}).get("noul", 0)
        distinct_again = a.get("distinct_because", {}).get("noul", 0)
        improve = a.get("improve_aspect", {}).get("choice", "?")
        return {
            "canon_worthy": canon,
            "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "distinct_from_others": distinct_again,
            "improve_aspect": improve,
            "composite": (canon + distinct + doctrine) / 3,
        }
    except Exception:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "distinct_from_others": 0,
                "improve_aspect": "?", "composite": 0}


print(f"=== GAN loop: {len(SEEDS)} seeds × 3 iterations ===")
results = []

for seed in SEEDS:
    print(f"\n=== Seed {seed} ===")
    feedback = ""
    history = []
    for iteration in range(3):
        print(f"  iter {iteration}: ", end="", flush=True)
        t0 = time.time()
        lore = gen_with_feedback(seed, feedback or "this is the first iteration — be fresh and vivid")
        if not lore or len(lore) < 80:
            print("SKIP")
            continue
        scores = score(lore)
        elapsed = time.time() - t0
        history.append({
            "iteration": iteration,
            "lore": lore,
            "scores": scores,
            "elapsed": elapsed,
        })
        # Build feedback for next iteration from JEV's improve_aspect choice
        feedback = f"Previous iteration JEV said: improve aspect = {scores['improve_aspect']}. Composite was {scores['composite']:.3f}."
        results.append({
            "seed": seed,
            "iteration": iteration,
            "lore": lore,
            "scores": scores,
            "elapsed": elapsed,
        })
        print(f"comp={scores['composite']:.3f} improve={scores['improve_aspect']} ({elapsed:.1f}s)")
        time.sleep(0.5)

# Save
with open("/workspace/research/GAN_LORE_LOOP_RESULTS.json", "w") as f:
    json.dump(results, f, indent=2)

# Find promoted (composite >= 0.7)
promoted = [r for r in results if r["scores"]["composite"] >= 0.7]
print(f"\n=== {len(promoted)}/{len(results)} PROMOTED ===")
for r in promoted:
    print(f"  seed {r['seed']} iter {r['iteration']}: comp={r['scores']['composite']:.3f}")

# Save promoted lores for filing as canon cells
with open("/workspace/research/GAN_PROMOTED_LORES.json", "w") as f:
    json.dump(promoted, f, indent=2)
