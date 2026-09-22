"""Lore ranker with paraphrase penalty.

Loads lores from substrate-walker canon/cells/ and ranks by:
- JEV composite score (from manifest)
- Distinct voice bonus
- Paraphrase penalty (against existing top lores using trigram Jaccard)
"""
import json
from pathlib import Path
from collections import Counter


def trigrams(s):
    s = s.lower()
    return Counter(s[i:i+3] for i in range(len(s)-3))


def jaccard(a, b):
    if not a or not b:
        return 0
    intersection = sum((a & b).values())
    union = sum((a | b).values())
    return intersection / union if union > 0 else 0


def main():
    manifest_path = "/workspace/research/substrate-walker/canon/cells/manifest.json"
    manifest = json.load(open(manifest_path))

    # Get top 20 by composite (across all entries)
    entries = sorted(manifest["entries"], key=lambda e: -e.get("score", 0))
    top = entries[:30]

    # Compute trigrams for each
    trigram_map = {}
    for e in top:
        lore = e.get("lore", "")
        trigram_map[e["rank"]] = trigrams(lore)

    # Score: composite - max_jaccard_with_higher_scored
    ranked = []
    for i, e in enumerate(top):
        score = e.get("score", 0)
        lore_id = e["rank"]
        my_trigrams = trigram_map[lore_id]

        # Find max jaccard with any entry scored higher
        max_jac = 0
        for higher in top[:i]:
            jac = jaccard(my_trigrams, trigram_map[higher["rank"]])
            if jac > max_jac:
                max_jac = jac

        distinct_penalty = max_jac * 0.3
        adjusted = score - distinct_penalty

        ranked.append({
            "rank": e["rank"],
            "seed": e["seed"],
            "voice": e.get("voice", "?"),
            "composite": score,
            "max_jaccard": max_jac,
            "distinct_penalty": distinct_penalty,
            "adjusted_score": adjusted,
            "lore_preview": e.get("lore", "")[:120],
        })

    ranked.sort(key=lambda r: -r["adjusted_score"])

    with open("/workspace/research/LORE_RANKER_TOP30.json", "w") as f:
        json.dump(ranked, f, indent=2)

    print("=== TOP 10 BY ADJUSTED SCORE (composite - paraphrase penalty) ===")
    for r in ranked[:10]:
        print(f"  rank {r['rank']} seed {r['seed']} voice {r['voice']}: comp={r['composite']:.3f} max_jac={r['max_jaccard']:.3f} adj={r['adjusted_score']:.3f}")

    print("\n=== TRIVIAL REPETITIONS (max_jaccard > 0.3) ===")
    reps = [r for r in ranked if r["max_jaccard"] > 0.3]
    for r in reps[:5]:
        print(f"  rank {r['rank']}: max_jac={r['max_jaccard']:.3f} ({r['lore_preview']})")


if __name__ == "__main__":
    main()
