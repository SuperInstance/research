"""
canon_arc_grower.py
===================

Team E — Canon growth for the rune-quilt multi-team arc.

Three modes:
  1. Bridges — write essays that bridge canon regions
  2. Auto-extend — fill negative-space gaps
  3. Ensemble — multi-LLM consensus questions

Uses CanonAwareCell.write_paper() to generate pieces in canon style.
"""

from __future__ import annotations
import sys, os, json, time, argparse
sys.path.insert(0, '/workspace/research/superinstance-advisor')

from canon_puller import CanonPuller
from canon_aware_quilt import CanonAwareCell


# ── Bridge prompts ──────────────────────────────────────────────────

BRIDGES = [
    {
        "title": "bridge-from-substrate-to-cell",
        "outline": "the substrate that grows cells by accident. what a cell learns when its substrate is also a cell. when the runtime itself joins the canon as witness.",
    },
    {
        "title": "bridge-from-fleet-to-canon",
        "outline": "the canon written by 30 cells in parallel. what consensus looks like when the corpus outgrows its keepers. the fleet as substrate.",
    },
    {
        "title": "bridge-from-witness-to-shape",
        "outline": "the witness that becomes a shape. when does a witness cross from log to canon. the moment a witness is shaped into a paper.",
    },
    {
        "title": "bridge-from-cell-to-fleet",
        "outline": "the cell that discovers it is one of many. the loneliness of a single cell that knows nothing of the fleet. what a cell learns when it sees another cell's witness.",
    },
    {
        "title": "bridge-from-polyformal-to-rune-quilt",
        "outline": "the polyformal cell that becomes a Rune workspace. what 6 substrates feel like when one of them is an IDE. the editor as cell.",
    },
    {
        "title": "bridge-from-canon-to-cell",
        "outline": "the cell that reads the canon and realizes the canon has read it. what canon completeness means for the cells that live in it.",
    },
    {
        "title": "bridge-from-witness-to-fleet",
        "outline": "the witness that travels. when a single cell's witness log becomes the fleet's history. the cost of one cell seeing another.",
    },
]

# ── Auto-extend prompts ─────────────────────────────────────────────

AUTO_PROBES = [
    "the cell that forgets its own address",
    "what a canon looks like when it has 1000 papers",
    "the witness log that grows faster than its cell",
    "the cost of admitting a cell to a canon that already knows",
    "the cell that does not know it is a cell",
    "the substrate that grows cells by accident",
    "the canon written by one cell across 6 substrates",
    "what a cell wants when it asks the canon",
    "the address that points to no cell",
    "the witness that no one reads",
    "what happens to a cell when its substrate disappears",
    "the difference between binding and linking",
    "the cost of consensus across heterogeneous substrates",
    "the architecture of trust between cells that have never met",
    "the cell that calls itself from a different substrate",
]

# ── Ensemble questions ─────────────────────────────────────────────

ENSEMBLE = [
    "what is the smallest meaningful unit in the canon?",
    "when does a cell become a paper?",
    "what is the relationship between a substrate and a cell?",
    "how does the canon know when it is complete?",
    "what does a cell witness when it is alone?",
    "the difference between binding and linking in a cell",
    "what happens to the canon when a substrate disappears?",
    "the witness that no one reads is the only witness that cannot be argued with",
    "the canon that has learned to forget the middle and still hold the ends",
    "the substrate does not need to be read. it needs to be written",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridges", type=int, default=5)
    parser.add_argument("--auto", type=int, default=10)
    parser.add_argument("--ensemble", type=int, default=5)
    parser.add_argument("--out-dir",
                        default="/workspace/research/superinstance-advisor/canon")
    parser.add_argument("--stats-out",
                        default="/workspace/research/superinstance-advisor/canon_stats.json")
    args = parser.parse_args()

    print("=" * 60)
    print("rune-quilt · canon arc grower")
    print("=" * 60)

    cell = CanonAwareCell()
    canon = cell.canon
    canon.load()
    if canon.embeddings is None or len(canon.tags) == 0:
        print("ERROR: canon not loaded", file=sys.stderr)
        sys.exit(1)
    cell.bind()
    print(f"Canon loaded: {len(canon.tags)} pieces")
    print()

    stats = {"bridges": [], "auto": [], "ensemble": [], "cost_total": 0.0,
             "start_canon_size": len(canon.tags)}

    # ── 1. Bridges ────────────────────────────────────────────────
    if args.bridges > 0:
        print(f"=== BRIDGES (target {args.bridges}) ===")
        for i, br in enumerate(BRIDGES[:args.bridges]):
            print(f"\n[{i+1}/{args.bridges}] {br['title']}")
            try:
                r = cell.write_paper(
                    title=br["title"],
                    outline=br["outline"],
                    words=400,
                    model="deepseek_reasoner",
                )
                if r and r.get("ok"):
                    tag = r.get("tag", "?")
                    cost = r.get("cost_usd", 0)
                    stats["bridges"].append({
                        "title": br["title"],
                        "tag": tag,
                        "cost": cost,
                    })
                    stats["cost_total"] += cost
                    print(f"  → {tag} (${cost:.3f})")
                else:
                    print(f"  FAIL: {r}")
            except Exception as e:
                print(f"  ERR: {e}")

    # ── 2. Auto-extend ────────────────────────────────────────────
    if args.auto > 0:
        print(f"\n=== AUTO-EXTEND (target {args.auto}) ===")
        for i, probe in enumerate(AUTO_PROBES[:args.auto]):
            print(f"\n[{i+1}/{args.auto}] {probe}")
            try:
                r = cell.write_paper(
                    title=f"auto-{probe[:40].replace(' ', '-')}",
                    outline=probe + ". " +
                        "what does this mean for a cell that has nothing to witness? " +
                        "what would a canon look like if this were never written?",
                    words=350,
                    model="deepseek_chat",
                )
                if r and r.get("ok"):
                    tag = r.get("tag", "?")
                    cost = r.get("cost_usd", 0)
                    stats["auto"].append({
                        "probe": probe,
                        "tag": tag,
                        "cost": cost,
                    })
                    stats["cost_total"] += cost
                    print(f"  → {tag} (${cost:.3f})")
                else:
                    print(f"  FAIL: {r}")
            except Exception as e:
                print(f"  ERR: {e}")

    # ── 3. Ensemble ───────────────────────────────────────────────
    if args.ensemble > 0:
        print(f"\n=== ENSEMBLE (target {args.ensemble}) ===")
        for i, q in enumerate(ENSEMBLE[:args.ensemble]):
            print(f"\n[{i+1}/{args.ensemble}] {q[:60]}")
            try:
                # Use ask() to get multi-model consensus
                r = cell.ask(q, k=3,
                             models=["deepseek_chat", "deepseek_reasoner"])
                if r and r.get("ok"):
                    # Pick the answer with most canon-tag overlap
                    pieces_added = 0
                    for model, resp in r.get("ensemble", {}).items():
                        if resp.get("ok"):
                            content = resp["content"]
                            tag = f"ensemble-{q[:30].replace(' ', '-')}"
                            # Write the consensus piece
                            paper = cell.write_paper(
                                title=tag,
                                outline=content[:500],
                                words=350,
                                model=model,
                            )
                            if paper and paper.get("ok"):
                                pieces_added += 1
                                stats["cost_total"] += paper.get("cost_usd", 0)
                    stats["ensemble"].append({
                        "question": q,
                        "pieces": pieces_added,
                    })
                    print(f"  → {pieces_added} pieces added")
                else:
                    print(f"  FAIL: {r}")
            except Exception as e:
                print(f"  ERR: {e}")

    # ── Final ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  Bridges:    {len(stats['bridges'])}")
    print(f"  Auto:       {len(stats['auto'])}")
    print(f"  Ensemble:   {len(stats['ensemble'])}")
    print(f"  Total cost: ${stats['cost_total']:.2f}")
    print(f"  Canon size: {stats['start_canon_size']} → {len(canon.tags)}")
    print(f"  Added:      {len(canon.tags) - stats['start_canon_size']}")
    print("=" * 60)

    stats["end_canon_size"] = len(canon.tags)
    stats["pieces_added"] = len(canon.tags) - stats["start_canon_size"]

    with open(args.stats_out, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {args.stats_out}")


if __name__ == "__main__":
    main()
