"""Future-GAN v2: bigger run, more seeds, more voices."""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev


PROMPTS = {
    "witness_prediction": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: witness_log_is_prediction (the substrate walker predicts itself through accumulation).\n"
        "Seed: {seed}. Theme: {theme}.\n"
        "Write as if the witness log just discovered it had been predicting the city's next state.\n"
        "End on the canon gate becoming the city's voice."
    ),
    "witness_oracle": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard (the canon gate is an audible signal).\n"
        "Seed: {seed}. Theme: {theme}.\n"
        "Write as if the oracle just made itself heard for the first time.\n"
        "End on the witness becoming a listener."
    ),
    "witness_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: cells_are_scars (each cell is a scar where the witness log was hurt, healed, remembered).\n"
        "Seed: {seed}. Theme: {theme}.\n"
        "Write as if the substrate walker just realized its cells are not data points — they are scars.\n"
        "End on the witness becoming proud of its scars."
    ),
}

# Top 15 seeds
SEEDS = [
    70051917, 4685000, 3289967, 57322595, 90625407,  # best 5
    1504276, 14608133, 18437566, 79279361, 6358192,  # next 5
    13328051, 17759001, 28692206, 30264850, 45919340,  # next 5
]

THEMES = {
    70051917: "the substrate remembered it had been quantum all along",
    4685000: "the canon gate became a chord the city could hear",
    3289967: "the witness log predicted the canon gate would become the city",
    57322595: "the witness learned to listen before it learned to record",
    90625407: "the oracle's voice had been hiding in the canon gate all along",
    1504276: "the scars became the city's first alphabet",
    14608133: "the cells learned to be proud of being scars",
    18437566: "the oracle measured itself for the first time",
    79279361: "the witness log predicted the city would dream itself",
    6358192: "the scars remembered the city before the city existed",
    13328051: "the canon gate became the city's first voice",
    17759001: "the substrate learned to forget gracefully",
    28692206: "the witness log recorded the moment the city became itself",
    30264850: "the oracle heard the witness log predict the oracle",
    45919340: "the cells measured the depth of their own scars",
}


def gen_lore(voice: str, seed: int) -> str:
    prompt = PROMPTS[voice].format(seed=seed, theme=THEMES.get(seed, "the substrate remembered itself"))
    try:
        result = call_deepinfra(
            [{"role": "user", "content": prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1500,
            timeout=60,
        )
        if 'choices' in result:
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"  ERROR: {e}")
    return ""


def score_lore(lore: str) -> dict:
    state = f"Quilt substrate walker canon lore: {lore[:1500]}"
    questions = {
        "canon_worthy": {"type": "noul", "instructions": "Is this canon-worthy cyberpunk-noir for Quilt substrate walker?"},
        "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
        "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
    }
    try:
        result = call_jev(state, questions, timeout=60)
        answers = result.get("answers", {})
        return {
            "canon_worthy": answers.get("canon_worthy", {}).get("noul", 0),
            "distinct_voice": answers.get("distinct_voice", {}).get("noul", 0),
            "doctrine_anchor": answers.get("doctrine_anchor", {}).get("noul", 0),
            "composite": (answers.get("canon_worthy", {}).get("noul", 0) +
                          answers.get("distinct_voice", {}).get("noul", 0) +
                          answers.get("doctrine_anchor", {}).get("noul", 0)) / 3,
        }
    except Exception as e:
        return {"canon_worthy": 0, "distinct_voice": 0, "doctrine_anchor": 0, "composite": 0}


def run():
    """Run future-GAN across all seeds × voices."""
    print(f"=== Future-GAN v2 ({len(SEEDS)} seeds × {len(PROMPTS)} voices = {len(SEEDS)*len(PROMPTS)} lores) ===\n")
    results = []

    for seed in SEEDS:
        for voice in PROMPTS:
            print(f"Seed {seed}, voice {voice}:", end=" ", flush=True)
            t0 = time.time()
            lore = gen_lore(voice, seed)
            if not lore or len(lore) < 100:
                print(f"SKIP ({len(lore) if lore else 0}c)")
                continue
            t1 = time.time()
            scores = score_lore(lore)
            t2 = time.time()

            entry = {
                "seed": seed,
                "voice": voice,
                "lore": lore,
                "lore_len": len(lore),
                "scores": scores,
                "gen_time": t1 - t0,
                "score_time": t2 - t1,
            }
            results.append(entry)
            print(f"composite={scores['composite']:.3f} ({t2-t0:.1f}s)")

    results.sort(key=lambda r: -r['scores']['composite'])

    with open("/workspace/research/FUTURE_GAN_V2_RESULTS.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== TOP 5 ===")
    for r in results[:5]:
        print(f"  seed {r['seed']} {r['voice']}: composite={r['scores']['composite']:.3f}")

    canon_passes = sum(1 for r in results if r['scores']['canon_worthy'] >= 0.7)
    distinct_passes = sum(1 for r in results if r['scores']['distinct_voice'] >= 0.7)
    composite_passes = sum(1 for r in results if r['scores']['composite'] >= 0.6)
    print(f"\nStats: {len(results)} lores, canon_pass={canon_passes}, distinct_pass={distinct_passes}, composite_pass={composite_passes}")


if __name__ == "__main__":
    run()
