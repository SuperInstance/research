"""
Tycoon Game GAN Improvement Loop

This is a continuous improvement loop:
1. Producer generates improvement ideas for the cargo-line-tycoon game
2. Critics rate each idea (multiple models)
3. Best ideas get implemented
4. Repeat

The loop runs as long as you let it, generating improvements.

Usage:
  python3 tycoon_gan_loop.py --iterations 10
"""

import os
import sys
import json
import time
import argparse
import asyncio
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, '/workspace/research/api-orchestra')
from multi_api import chat, parallel_chat

WORKSPACE = Path("/workspace/research/cargo-line-tycoon")


def get_tycoon_context() -> str:
    """Read the current tycoon README + VISION for context."""
    parts = []
    for fname in ["README.md", "VISION.md"]:
        fpath = WORKSPACE / fname
        if fpath.exists():
            with open(fpath) as f:
                parts.append(f.read())
    return "\n\n".join(parts)[:5000]  # truncate


PRODUCER_PROMPT = """You are a game designer improving a cargo-line-tycoon simulation game.

The current state of the game:
{context}

Generate ONE concrete improvement idea. Focus on:
- Player agency (meaningful choices)
- Feedback loops (visible consequences)
- Emergent behavior (complexity from simple rules)
- Substrate integration (using the cell-based architecture)

Output format:
IDEA: [one short title]
DESCRIPTION: [2-3 sentences]
IMPLEMENTATION: [1-2 sentences on how to build it]
IMPACT: [HIGH/MEDIUM/LOW]
CATEGORY: [gameplay/visual/ai/economy/social/multiplayer]"""


CRITIC_PROMPT = """You are a critical game reviewer. Rate this improvement idea for the cargo-line-tycoon game.

Idea: {idea}

Rate on a scale 1-10 for each:
- NOVELTY: Is this idea new and surprising?
- FEASIBILITY: Can it be built with current tech?
- ENGAGEMENT: Will it make the game more fun?
- SUBSTRATE_FIT: Does it use the cell architecture well?

Output format:
NOVELTY: [1-10]
FEASIBILITY: [1-10]
ENGAGEMENT: [1-10]
SUBSTRATE_FIT: [1-10]
TOTAL: [sum]
COMMENT: [one sentence critique]"""


async def generate_idea(iteration: int, prev_ideas: List[Dict]) -> Dict:
    """Producer generates one improvement idea."""
    context = get_tycoon_context()

    # Reference previous ideas to avoid repetition
    if prev_ideas:
        prev_summary = "\n".join(
            f"- {i['title']} (score {i['total']})"
            for i in prev_ideas[-5:]
        )
        context += f"\n\nPrevious ideas (don't repeat):\n{prev_summary}"

    prompt = PRODUCER_PROMPT.format(context=context)

    # Use llama-8b for fast ideation (non-reasoning)
    idea_text = chat(
        "deepinfra",
        [{"role": "user", "content": prompt}],
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        max_tokens=300,
        temperature=0.85,
    )

    return _parse_idea(idea_text, iteration)


def _parse_idea(text: str, iteration: int) -> Dict:
    """Parse idea text into structured form."""
    idea = {
        "iteration": iteration,
        "raw": text,
        "title": "",
        "description": "",
        "implementation": "",
        "impact": "",
        "category": "",
    }

    # Handle both "IDEA:" and "**IDEA:**" formats
    # Also handle case-insensitive and markdown bold
    prefixes = {
        "IDEA": "title",
        "TITLE": "title",
        "DESCRIPTION": "description",
        "DESC": "description",
        "IMPLEMENTATION": "implementation",
        "IMPL": "implementation",
        "IMPACT": "impact",
        "CATEGORY": "category",
    }

    for line in text.split("\n"):
        line = line.strip().rstrip(":")
        # Remove markdown bold markers
        line_clean = line.replace("**", "").strip()

        for prefix, key in prefixes.items():
            # Check "IDEA: ..." or "**IDEA:** ..." or "IDEA - ..."
            for sep in [":", " - "]:
                if line_clean.upper().startswith(prefix + sep):
                    value = line_clean[len(prefix) + len(sep):].strip()
                    if not idea[key]:  # Don't overwrite first parse
                        idea[key] = value
                    break

    if not idea["title"]:
        # Fallback: use first line as title
        first = text.strip().split("\n")[0]
        # Clean up "Here\'s a concrete improvement idea:" type prefixes
        for prefix in ["Here", "This", "Below"]:
            if first.lower().startswith(prefix.lower()):
                # Find a colon or "IDEA:" marker
                for marker in ["IDEA:", "IDEA -"]:
                    idx = first.lower().find(marker.lower())
                    if idx >= 0:
                        first = first[idx + len(marker):].strip()
                        break
                else:
                    first = first.split(":", 1)[-1].strip() if ":" in first else first
        idea["title"] = first[:100].strip("*:").strip()

    return idea


async def critique_idea(idea: Dict, iteration: int) -> Dict:
    """Critics rate an idea (3 critics in parallel)."""
    prompt = CRITIC_PROMPT.format(idea=idea["raw"])

    # 3 different critic models
    critic_calls = [
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "max_tokens": 200, "temperature": 0.4},
        {"provider": "deepinfra", "messages": [{"role": "user", "content": prompt}],
         "model": "google/gemma-3-27b-it", "max_tokens": 200, "temperature": 0.4},
        {"provider": "deepseek", "messages": [{"role": "user", "content": prompt}],
         "model": "deepseek-chat", "max_tokens": 200, "temperature": 0.4},
    ]

    responses = await parallel_chat(critic_calls)
    scores = [_parse_criticism(r) for r in responses]
    avg_scores = {
        "novelty": sum(s["novelty"] for s in scores) / len(scores),
        "feasibility": sum(s["feasibility"] for s in scores) / len(scores),
        "engagement": sum(s["engagement"] for s in scores) / len(scores),
        "substrate_fit": sum(s["substrate_fit"] for s in scores) / len(scores),
    }
    avg_scores["total"] = sum(v for k, v in avg_scores.items() if k != "total")

    idea["critiques"] = scores
    idea["avg_scores"] = avg_scores
    idea["total"] = avg_scores["total"]
    return idea


def _parse_criticism(text: str) -> Dict:
    """Parse criticism response."""
    scores = {"novelty": 5, "feasibility": 5, "engagement": 5, "substrate_fit": 5, "comment": ""}

    for line in text.split("\n"):
        line = line.strip()
        for key in ["NOVELTY", "FEASIBILITY", "ENGAGEMENT", "SUBSTRATE_FIT", "COMMENT"]:
            if line.startswith(key + ":"):
                value = line[len(key) + 1:].strip()
                if key == "COMMENT":
                    scores["comment"] = value
                else:
                    try:
                        scores[key.lower()] = float(value.split("/")[0].strip())
                    except ValueError:
                        pass
                break

    return scores


async def run_loop(iterations: int, output_dir: Path):
    """Run the GAN loop."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Tycoon GAN Loop — {iterations} iterations")
    all_ideas = []
    best_idea = None

    for i in range(iterations):
        print(f"\n--- Iteration {i+1}/{iterations} ---")

        # 1. Producer generates idea
        idea = await generate_idea(i + 1, all_ideas)
        print(f"Idea: {idea['title']}")

        # 2. Critics rate
        idea = await critique_idea(idea, i + 1)
        print(f"Score: {idea['total']:.1f}/40")
        for c in idea["critiques"]:
            print(f"  {c.get('comment', '')[:80]}")

        all_ideas.append(idea)

        # Track best
        if best_idea is None or idea["total"] > best_idea["total"]:
            best_idea = idea
            print(f"  ★ New best idea!")

        # Save progress
        with open(output_dir / "ideas.json", "w") as f:
            json.dump(all_ideas, f, indent=2)

    # Final report
    print(f"\n{'='*60}")
    print(f"GENERATED {len(all_ideas)} IDEAS")
    print(f"{'='*60}")

    # Top 5 by total
    top_5 = sorted(all_ideas, key=lambda x: -x["total"])[:5]
    for rank, idea in enumerate(top_5, 1):
        print(f"\n#{rank} (score {idea['total']:.1f}): {idea['title']}")
        print(f"   {idea['description'][:200]}")
        print(f"   Category: {idea['category']}, Impact: {idea['impact']}")

    # Save top ideas
    with open(output_dir / "top_ideas.md", "w") as f:
        f.write("# Top 5 Tycoon Improvement Ideas\n\n")
        for rank, idea in enumerate(top_5, 1):
            f.write(f"## #{rank}: {idea['title']} (score {idea['total']:.1f}/40)\n\n")
            f.write(f"**Description**: {idea['description']}\n\n")
            f.write(f"**Implementation**: {idea['implementation']}\n\n")
            f.write(f"**Category**: {idea['category']}\n")
            f.write(f"**Impact**: {idea['impact']}\n\n")
            for c in idea["critiques"]:
                f.write(f"_{c['comment']}_\n\n")
            f.write("---\n\n")

    print(f"\nTop ideas saved to {output_dir}/top_ideas.md")
    return all_ideas


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output", type=str, default="tycoon_gan_output")
    args = parser.parse_args()

    out_dir = Path("/workspace/research/tycoon-gan") / args.output
    asyncio.run(run_loop(args.iterations, out_dir))
