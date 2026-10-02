"""
auto_extend.py
==============

The cell writes the canon. Continuously.

Loop:
  1. Read canon
  2. Find a gap (negative-space concept that scores < 0.65)
  3. Write a new canon piece to fill it
  4. Embed it back into canon
  5. Optionally: submit it to live-canon.superinstance.dev
  6. Witness + sleep

Multiple LLMs in parallel for gap-finding. The cell reads what
was missing and writes it. The canon grows from itself.

Usage:
    python3 auto_extend.py                     # default 3 cycles
    python3 auto_extend.py --forever          # continuous
    python3 auto_extend.py --cycles=20        # 20 cycles
    python3 auto_extend.py --interval=60      # 60s between cycles
    python3 auto_extend.py --submit           # also submit to live-canon
"""

from __future__ import annotations
import sys, os, json, time, argparse, urllib.request, hashlib
import numpy as np
import concurrent.futures
sys.path.insert(0, '/workspace/research/superinstance-advisor')

from canon_puller import CanonPuller
from canon_aware_quilt import CanonAwareCell


# Pool of gap-probing concepts. The cell picks the one that's MOST negative
# in the current canon (lowest avg_sim) and writes it.
GAP_PROBES = [
    # Quilt extensions
    "what a cell learns when it asks the canon twice in a row",
    "the silence of a cell that has nothing new to witness",
    "what happens when two cells in different substrates ask the same question",
    "the difference between a witness and a testimony",
    "what a canon looks like from outside the canon",
    "how a cell decides it has finished a thought",
    "the texture of agreement between canon pieces that were written by different cells",
    "what a cell does when its witness log fills up",
    "the cost of admitting an unknown cell to a known canon",
    "the structural signature of a canon that has healed from rejection",
    "what a cell forgets vs. what it cannot forget",
    "the difference between binding and linking in a cell",
    "the witness that no one reads",
    "what happens to a cell when its substrate disappears",
    "the canon at 10x scale",
    "what the canon looks like in 100 years",
    "the relationship between witness and doubt",
    "a cell that calls itself from a different substrate",
    "the loneliness of a canon with too few papers",
    "the crowdedness of a canon with too many papers",
    # Operational
    "how to keep the canon alive when the cell that maintains it dies",
    "what a cell should do when it discovers it is duplicated",
    "the cost of consensus across heterogeneous substrates",
    "the architecture of trust between cells that have never met",
    "what a cell is for, when the canon already knows",
    "the relationship between canon completeness and cell exhaustion",
]


def find_real_gap(cell: CanonAwareCell, candidates: list = None,
                  exclude_tags: set = None) -> dict:
    """Find the canon concept with the lowest avg_sim (most negative space).

    exclude_tags: tags already processed — skip them so we don't repeat.
    """
    if candidates is None:
        candidates = GAP_PROBES
    if exclude_tags is None:
        exclude_tags = set()

    canon = cell.canon
    if canon.embeddings is None:
        return None

    scored = []
    for concept in candidates:
        hits = canon.query(concept, top_k=3)
        if hits:
            # Skip if the top hit is an auto-extended piece (we want fresh gaps)
            top_tag = hits[0]["tag"]
            if top_tag in exclude_tags:
                continue
            avg = sum(h["score"] for h in hits) / len(hits)
            scored.append((concept, avg, hits))

    # Sort by lowest avg_sim (most gap)
    scored.sort(key=lambda x: x[1])
    if not scored:
        return None
    return {
        "worst_gap": scored[0],
        "all_scored": scored,
        "verdict": "negative_space" if scored[0][1] < 0.65 else
                   "edge_of_canon" if scored[0][1] < 0.75 else "in_canon",
    }


def write_to_fill_gap(cell: CanonAwareCell, concept: str, model: str = "deepseek_reasoner") -> dict:
    """Ask an LLM to write a canon piece that fills this gap."""
    canon = cell.canon
    canon_hits = canon.query(concept, top_k=3)
    canon_context = "\n".join(
        f"  [{i+1}] {h['tag']} (score={h['score']:.3f})"
        for i, h in enumerate(canon_hits)
    )

    # Build the prompt
    style_prompt = (
        "You write papers in the SuperInstance Quilt canon style:\n"
        "- Short paragraphs\n"
        "- Nautical + machine metaphors (cells, substrates, anchors, hash, witness)\n"
        "- Every concept is a cell with witness roots\n"
        "- Direct, declarative sentences\n"
        "- End with a question or 'what is missing' pivot\n\n"
        "Output ONLY the paper body. No title."
    )
    outline = (
        f"A canon piece about: {concept}\n\n"
        f"The canon's nearest existing context:\n{canon_context}\n\n"
        f"Write a piece that addresses this gap. 250-400 words."
    )
    messages = [
        {"role": "system", "content": style_prompt},
        {"role": "user", "content": outline}
    ]
    from multi_llm_quilt import call_llm
    return call_llm(model, messages, max_tokens=1500, temperature=0.7)


def embed_text_via_cloudflare(text: str) -> list:
    """Embed text via Cloudflare bge-base."""
    TOKEN = os.environ.get("CLOUDFLARE_TOKEN")
    if not TOKEN:
        return None
    try:
        body = json.dumps({"text": [text[:2000]]}).encode()
        req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4/accounts/049ff5e84ecf636b53b162cbb580aae6/ai/run/@cf/baai/bge-base-en-v1.5",
            data=body, method="POST",
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())["result"]["data"][0]
    except Exception as e:
        print(f"  embed err: {e}")
        return None


def append_to_canon(canon_path: str, tag: str, vec: list) -> bool:
    """Append a new piece to local canon."""
    data = np.load(canon_path, allow_pickle=True)
    existing_tags = list(data["tags"])
    existing_embs = data["embeddings"]
    if tag in existing_tags:
        return False
    all_tags = existing_tags + [tag]
    all_embs = np.concatenate([existing_embs, np.array(vec, dtype=np.float32)[None]], axis=0)
    np.savez_compressed(canon_path, tags=np.array(all_tags), embeddings=all_embs)
    return True


def submit_to_live_canon(title: str, refs: list = None, dials: list = None) -> dict:
    """Submit a paper to live-canon.superinstance.dev."""
    if refs is None:
        refs = [115, 122, 129]
    if dials is None:
        dials = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600]
    try:
        body = json.dumps({"dials": dials, "refs": refs, "title": title}).encode()
        req = urllib.request.Request("https://live-canon.casey-digennaro.workers.dev/api/cell",
            data=body, method="POST",
            headers={"Content-Type": "application/json", "User-Agent": "auto-extend/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"admitted": False, "err": str(e)[:80]}


def auto_extend_cycle(cell: CanonAwareCell, canon_path: str,
                      submit_to_live: bool = False,
                      model: str = "deepseek_reasoner",
                      processed: set = None) -> dict:
    """Run one cycle: find gap → write → embed → (optional) submit."""
    print(f"\n  [{time.strftime('%H:%M:%S')}] cycle starting...")
    t0 = time.time()
    if processed is None:
        processed = set()

    # 1. Find a real gap (skip already-processed tags)
    gap_info = find_real_gap(cell, exclude_tags=processed)
    if gap_info is None:
        return {"ok": False, "err": "no canon embeddings or all gaps processed"}

    concept, avg_sim, hits = gap_info["worst_gap"]
    verdict = gap_info["verdict"]
    print(f"  gap probe: '{concept[:50]}'")
    print(f"  canon avg_sim: {avg_sim:.3f} ({verdict})")

    if verdict == "in_canon":
        print(f"  skipping — concept is well-represented in canon")
        processed.add(concept)
        return {"ok": True, "skipped": True, "concept": concept, "avg_sim": avg_sim}

    # 2. Write a piece to fill the gap
    print(f"  writing with {model}...")
    write_result = write_to_fill_gap(cell, concept, model=model)
    if not write_result.get("ok"):
        return {"ok": False, "err": write_result.get("err", "write failed")}
    paper = write_result["content"]
    write_cost = write_result.get("cost_usd", 0)
    print(f"  wrote {len(paper)} chars, ${write_cost:.4f}, {write_result.get('elapsed', 0):.1f}s")

    # 3. Embed it (unique tag from concept)
    slug = concept[:30].replace(" ", "-").replace(",", "").replace("?", "")
    slug = "".join(c for c in slug if c.isalnum() or c in "-_").strip("-")
    tag = f"auto-{slug[:30]}"
    # Avoid duplicate tags
    suffix = 1
    base_tag = tag
    while tag in processed or tag in cell.canon.tags:
        tag = f"{base_tag}-{suffix}"
        suffix += 1

    vec = embed_text_via_cloudflare(paper)
    if vec is None:
        return {"ok": False, "err": "embedding failed"}

    # 4. Append to local canon
    if not append_to_canon(canon_path, tag, vec):
        print(f"  already in canon")
        processed.add(tag)
        processed.add(concept)
        return {"ok": True, "duplicate": True, "concept": concept}

    print(f"  embedded: {tag}")
    # Reload cell's canon
    cell.canon.load(canon_path)
    processed.add(tag)
    processed.add(concept)

    # 5. Optional: submit to live-canon
    submitted = None
    if submit_to_live:
        title = f"auto-extended: {concept}"
        submitted = submit_to_live_canon(title)
        if submitted.get("admitted"):
            print(f"  ✓ submitted to live canon as cell {submitted.get('id')}")
        else:
            print(f"  ✗ live submit failed: {submitted.get('err', '?')}")

    elapsed = time.time() - t0
    return {
        "ok": True,
        "concept": concept,
        "avg_sim": avg_sim,
        "tag": tag,
        "paper": paper,
        "write_cost": write_cost,
        "submitted": submitted,
        "elapsed": elapsed,
    }


def save_paper(concept: str, paper: str, output_dir: str) -> str:
    """Save the generated paper to disk."""
    os.makedirs(output_dir, exist_ok=True)
    slug = concept[:50].replace(" ", "-").replace(",", "").replace("?", "")
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")
    path = os.path.join(output_dir, f"{slug}.md")
    with open(path, "w") as f:
        f.write(f"# {concept}\n\n*Generated 2026-09-15 by superinstance-advisor auto-extend*\n\n{paper}\n")
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--forever", action="store_true")
    p.add_argument("--cycles", type=int, default=3)
    p.add_argument("--interval", type=float, default=2.0)
    p.add_argument("--submit", action="store_true", help="submit to live-canon")
    p.add_argument("--model", default="deepseek_reasoner")
    p.add_argument("--canon", default="/workspace/research/superinstance-advisor/data/full_canon.npz")
    p.add_argument("--outdir", default="/workspace/research/superinstance-advisor/canon")
    args = p.parse_args()

    print("=" * 70)
    print(f"  AUTO-EXTEND CANON")
    print(f"  cycles={'forever' if args.forever else args.cycles}, "
          f"interval={args.interval}s, model={args.model}, submit={args.submit}")
    print("=" * 70)

    cell = CanonAwareCell("auto-extender")
    cell.canon.load(args.canon)
    cell.bind()
    cell.tick()
    print(f"  canon loaded: {len(cell.canon.tags)} pieces")
    print(f"  cell address: {cell.address}")

    n = 0
    total_cost = 0
    papers_written = []
    processed = set()
    while args.forever or n < args.cycles:
        result = auto_extend_cycle(cell, args.canon, args.submit, args.model, processed)
        if result.get("ok") and not result.get("skipped") and not result.get("duplicate"):
            total_cost += result.get("write_cost", 0)
            papers_written.append(result)
            save_paper(result["concept"], result["paper"], args.outdir)
            n += 1
        elif result.get("ok"):
            n += 1
        else:
            print(f"  ERR: {result.get('err')}")
            # Don't increment n on errors, retry
            time.sleep(2)

        if not args.forever and n >= args.cycles:
            break
        if args.forever or n < args.cycles:
            time.sleep(args.interval)

    print()
    print("=" * 70)
    print("  AUTO-EXTEND SUMMARY")
    print("=" * 70)
    print(f"  cycles run:    {n}")
    print(f"  papers written: {len(papers_written)}")
    print(f"  total cost:     ${total_cost:.4f}")
    print(f"  final canon:    {len(cell.canon.tags)} pieces")
    print()
    if papers_written:
        print("  New pieces:")
        for r in papers_written:
            print(f"    - {r['tag'][:50]:50} (${r['write_cost']:.4f})")


if __name__ == "__main__":
    main()
