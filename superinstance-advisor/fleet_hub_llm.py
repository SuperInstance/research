"""
fleet_hub_llm.py
================

A multi-cell fleet hub where each cell uses a different LLM.

Cells in the fleet:
    1. cell.deepseek    → uses deepseek-chat (fast, general)
    2. cell.zai         → uses zai_coding (prepaid, deep reasoning)
    3. cell.bd_mini     → uses seed_mini (cheap, with reasoning)
    4. cell.deepr       → uses deepseek-reasoner (deep thinking)
    5. cell.bd_code     → uses seed_code (code specialist)

Each cell asks the canon. The hub detects consensus and gaps.
A gap is when multiple cells disagree on a question.

When consensus is high → the canon is stable.
When disagreement is high → the canon is missing context. The hub surfaces this.
"""

from __future__ import annotations
import sys, os, json, time, concurrent.futures, argparse
sys.path.insert(0, '/workspace/research/superinstance-advisor')

import numpy as np
from canon_aware_quilt import CanonAwareCell


def cell_ask(cell_id: str, provider: str, question: str, canon_path: str) -> dict:
    """One cell asks the canon + its assigned LLM."""
    cell = CanonAwareCell(cell_id, canon=None)
    cell.canon.load(canon_path)

    # Use only this cell's LLM
    result = cell.ask(question, k=3, models=[provider])

    canon_hits = result["canon_hits"]
    top = canon_hits[0] if canon_hits else None
    llm_resp = result["ensemble"].get(provider, {})
    content = llm_resp.get("content", "") if llm_resp.get("ok") else None

    return {
        "cell": cell_id,
        "provider": provider,
        "top_canon_tag": top["tag"] if top else None,
        "top_canon_score": top["score"] if top else None,
        "llm_content": content,
        "llm_cost": llm_resp.get("cost_usd", 0) if llm_resp.get("ok") else 0,
        "llm_elapsed": llm_resp.get("elapsed", 0) if llm_resp.get("ok") else 0,
    }


# Questions the fleet rotates through
FLEET_QUESTIONS = [
    "what is the substrate",
    "what is the cell",
    "what is the witness",
    "what is the canon",
    "what is the cost of consensus",
    "what is the fleet",
    "what does a cell know about other cells",
    "what is the difference between bind and link",
    "what is the difference between effect and view",
    "what is negative space",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cycles", type=int, default=10)
    p.add_argument("--interval", type=float, default=2.0)
    p.add_argument("--canon", default="/workspace/research/superinstance-advisor/data/full_canon.npz")
    args = p.parse_args()

    # Define fleet
    fleet = [
        ("cell.deepseek", "deepseek_chat"),
        ("cell.zai", "zai_coding"),
        ("cell.bd_mini", "seed_mini"),
        ("cell.deepr", "deepseek_reasoner"),
        ("cell.bd_code", "seed_code"),
    ]

    print("=" * 70)
    print(f"  FLEET HUB — {len(fleet)} cells, {args.cycles} cycles, {args.interval}s interval")
    print("=" * 70)
    for cid, prov in fleet:
        print(f"  {cid:20} -> {prov}")

    print()
    findings = []
    consensus_runs = 0
    total_cost = 0
    start = time.time()

    for cycle in range(args.cycles):
        question = FLEET_QUESTIONS[cycle % len(FLEET_QUESTIONS)]
        print(f"\n[{cycle:3d}] Q: {question}")

        # Run all 5 cells in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(fleet)) as ex:
            futures = {
                ex.submit(cell_ask, cid, prov, question, args.canon): (cid, prov)
                for cid, prov in fleet
            }
            responses = []
            for f in concurrent.futures.as_completed(futures):
                try:
                    responses.append(f.result())
                except Exception as e:
                    responses.append({"err": str(e)[:80], "cell": futures[f][0]})

        # Check consensus: did all cells agree on top canon piece?
        top_tags = [r.get("top_canon_tag") for r in responses if r.get("top_canon_tag")]
        if top_tags:
            unique_top = set(top_tags)
            if len(unique_top) == 1:
                consensus_runs += 1
                consensus_msg = f"CONSENSUS ({top_tags[0][:40]}, score={responses[0].get('top_canon_score', 0):.3f})"
            else:
                consensus_msg = f"DISAGREE ({len(unique_top)} different top pieces)"
                findings.append({
                    "cycle": cycle,
                    "question": question,
                    "responses": responses,
                })

            total_cost += sum(r.get("llm_cost", 0) for r in responses)
            elapsed = max(r.get("llm_elapsed", 0) for r in responses)
            print(f"  {consensus_msg} | {elapsed:.1f}s | ${sum(r.get('llm_cost', 0) for r in responses):.4f}")

        if cycle < args.cycles - 1:
            time.sleep(args.interval)

    elapsed = time.time() - start
    print()
    print("=" * 70)
    print("  FLEET SUMMARY")
    print("=" * 70)
    print(f"  duration:       {elapsed:.1f}s")
    print(f"  cycles:         {args.cycles}")
    print(f"  consensus runs: {consensus_runs}/{args.cycles}")
    print(f"  findings:       {len(findings)} (disagreements)")
    print(f"  total cost:     ${total_cost:.4f}")
    print()
    if findings:
        print("  FINDINGS (cells disagreed):")
        for f in findings:
            print(f"    cycle {f['cycle']}: {f['question']}")
            seen = set()
            for r in f["responses"]:
                tag = r.get("top_canon_tag", "?")
                if tag not in seen:
                    seen.add(tag)
                    print(f"      [{r['cell']:18}] → {tag[:50]} (score={r.get('top_canon_score', 0):.3f})")


if __name__ == "__main__":
    main()
