"""
Tycoon GAN — Deep Iteration
Focused on implementing existing ideas more thoroughly.
Each iteration goes deeper on the previous best idea.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, '/workspace/research/api-orchestra')
sys.path.insert(0, '.')
from multi_api import chat, parallel_chat
from tycoon_gan_loop import get_tycoon_context, _parse_idea, _parse_criticism

DEEP_PROMPT = """You are a game designer. Take this existing tycoon game idea and make it DEEPER:

Existing idea: {prev_idea}

Make it more:
- Specific (concrete numbers, timings, formulas)
- Substrate-integrated (uses cell-graph architecture)
- Emergent (arises from simple rules)
- Player-visible (immediate feedback)

Output format:
IDEA: [short title]
DESCRIPTION: [3-4 sentences, specific]
IMPLEMENTATION: [1-2 sentences on code structure]
IMPACT: HIGH/MEDIUM/LOW
CATEGORY: gameplay/visual/ai/economy/social/multiplayer"""


async def deep_iterate(prev_idea: Dict, iteration: int) -> Dict:
    """Go deeper on the previous best idea."""
    prompt = DEEP_PROMPT.format(prev_idea=prev_idea["raw"])

    idea_text = chat("deepinfra",
                     [{"role": "user", "content": prompt}],
                     model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                     max_tokens=300, temperature=0.85)

    new_idea = _parse_idea(idea_text, iteration)
    new_idea["parent"] = prev_idea.get("title", "?")
    new_idea["parent_score"] = prev_idea.get("total", 0)

    # Critique
    critic_prompt = f"""Rate this game design idea for cargo-line-tycoon.

Idea: {idea_text}

Rate 1-10 each:
NOVELTY: ...
FEASIBILITY: ...
ENGAGEMENT: ...
SUBSTRATE_FIT: ...

TOTAL: [sum]
COMMENT: [one sentence]"""

    critic_calls = [
        {"provider": "deepinfra", "messages": [{"role": "user", "content": critic_prompt}],
         "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "max_tokens": 200, "temperature": 0.4},
        {"provider": "deepinfra", "messages": [{"role": "user", "content": critic_prompt}],
         "model": "google/gemma-3-27b-it", "max_tokens": 200, "temperature": 0.4},
        {"provider": "deepseek", "messages": [{"role": "user", "content": critic_prompt}],
         "model": "deepseek-chat", "max_tokens": 200, "temperature": 0.4},
    ]

    responses = await parallel_chat(critic_calls)
    scores = [_parse_criticism(r) for r in responses]

    avg = {
        "novelty": sum(s["novelty"] for s in scores) / len(scores),
        "feasibility": sum(s["feasibility"] for s in scores) / len(scores),
        "engagement": sum(s["engagement"] for s in scores) / len(scores),
        "substrate_fit": sum(s["substrate_fit"] for s in scores) / len(scores),
    }
    avg["total"] = sum(v for k, v in avg.items() if k != "total")

    new_idea["critiques"] = scores
    new_idea["avg_scores"] = avg
    new_idea["total"] = avg["total"]
    return new_idea


async def deep_loop(seed_idea: Dict, iterations: int, output_dir: Path):
    """Deep iteration on an idea."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Tycoon Deep Iteration — {iterations} iterations on '{seed_idea.get('title', '?')}'")

    current = seed_idea
    history = [current]

    for i in range(iterations):
        print(f"\n--- Iteration {i+1}/{iterations} ---")
        new = await deep_iterate(current, i + 1)
        history.append(new)
        print(f"Idea: {new['title']}")
        print(f"Score: {new['total']:.1f}/40")
        print(f"Parent: {new.get('parent', '?')} ({new.get('parent_score', 0):.1f})")

        # Only evolve if better
        if new["total"] >= current["total"] * 0.9:  # Allow slight regression
            current = new

        with open(output_dir / "deep_history.json", "w") as f:
            json.dump(history, f, indent=2)

    # Final best
    best = max(history, key=lambda h: h.get("total", 0))
    print(f"\nBest iteration: {best['title']} (score {best['total']:.1f})")

    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-idea", type=str, required=True,
                        help="Path to JSON with seed idea")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output", type=str, default="tycoon_deep")
    args = parser.parse_args()

    with open(args.seed_idea) as f:
        seed = json.load(f)

    out_dir = Path("/workspace/research/tycoon-gan") / args.output
    asyncio.run(deep_loop(seed, args.iterations, out_dir))
