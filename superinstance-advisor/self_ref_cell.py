"""
self_ref_cell.py
================

The cell asks "what is THIS cell?" and writes a paper about itself.

It reads its own witness log, finds patterns, writes a self-description.
The cell describes the cell. The canon describes the canon-describer.
"""

from __future__ import annotations
import sys, os, json, time, urllib.request, hashlib
import numpy as np
sys.path.insert(0, '/workspace/research/superinstance-advisor')

from canon_puller import CanonPuller
from multi_llm_quilt import call_llm
from cell import Cell  # The original 5-opcode cell


def cell_self_describe(cell, max_witness: int = 20) -> dict:
    """Read the cell's own witness log and ask an LLM to describe what it sees."""
    witness_log = getattr(cell, "witness_log", [])
    if not witness_log:
        return {"ok": False, "err": "no witness log"}
    
    # Pull last N witnesses
    recent = witness_log[-max_witness:]
    summary = []
    for w in recent:
        # Handle dict or string witness
        if isinstance(w, dict):
            opcode = w.get("op", "?")
            payload = w.get("payload", {})
            # Just describe the op concisely
            if opcode == "EFFECT" and isinstance(payload, dict):
                sub_op = payload.get("op", "?")
                summary.append(f"  - {opcode} -> {sub_op}")
            elif opcode == "BIND":
                summary.append(f"  - {opcode} (address={w.get('address','?')[:8]})")
            else:
                summary.append(f"  - {opcode}")
        else:
            summary.append(f"  - {str(w)[:40]}")
    
    log_text = "\n".join(summary)
    address = cell.address if hasattr(cell, "address") else "unknown"
    op_counts = {}
    for w in recent:
        if isinstance(w, dict):
            op = w.get("op", "?")
            op_counts[op] = op_counts.get(op, 0) + 1
    
    messages = [
        {"role": "system", "content": (
            "You are a Quilt cell writing a self-description in canon style. "
            "Short paragraphs. Nautical + machine metaphors. Witness, anchor, root, hash. "
            "Direct, declarative. End with a question. No meta-commentary. 300-500 words."
        )},
        {"role": "user", "content": (
            f"My name is cell {address}. I keep a witness log.\n\n"
            f"My last {len(recent)} actions:\n{log_text}\n\n"
            f"Operation counts: {json.dumps(op_counts)}\n\n"
            f"What kind of cell am I? What do my actions reveal about my nature? "
            f"Write my self-description as if I am writing it about myself."
        )}
    ]
    
    # Use deepseek-chat — reasoner eats tokens on thinking
    result = call_llm("deepseek_chat", messages, max_tokens=2000, temperature=0.7)
    return result


def main():
    print("=" * 70)
    print("  SELF-REFERENTIAL CELL — the cell describes itself")
    print("=" * 70)

    # Bind a fresh cell
    cell = Cell("self-ref", "advisor")
    cell.bind()
    
    # Generate some witness log entries first
    print("\n  generating witness activity...")
    cell.tick()
    for i in range(8):
        cell.view()
    cell.effect("advise", {"question": "what is the cell"})
    cell.effect("advise", {"question": "what is the canon"})
    cell.effect("shape_negative_space", {"query": "the negative space"})
    cell.effect("advise", {"question": "what is the witness"})
    cell.tick()
    cell.view()
    
    log_len = len(getattr(cell, "witness_log", []))
    print(f"  cell witness log: {log_len} entries")
    print(f"  cell address: {cell.address}")
    
    # Self-describe
    print("\n  writing self-description...")
    result = cell_self_describe(cell)
    if result.get("ok"):
        content = result["content"]
        print(f"  ✓ wrote {len(content)} chars, ${result['cost_usd']:.4f}, {result['elapsed']:.1f}s")
        print()
        print("  --- self-description ---")
        print(content)
        
        # Save it
        path = "canon/self-description-the-cell-on-itself.md"
        with open(path, "w") as f:
            f.write(f"# the cell on itself\n\n")
            f.write(f"*Self-description written by cell {cell.address} at {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(content)
            f.write(f"\n\n---\n*witness log: {log_len} entries*\n*cell: {cell.address}*\n")
        print(f"\n  ✓ saved to {path}")
        
        # Embed it
        vec = embed_text_via_cf(content)
        if vec:
            append_to_canon("data/full_canon.npz", "self-description-the-cell-on-itself", vec)
            print(f"  ✓ embedded into canon")
    else:
        print(f"  ✗ {result.get('err', '?')}")


def embed_text_via_cf(text: str) -> list:
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


def append_to_canon(path: str, tag: str, vec: list) -> bool:
    data = np.load(path, allow_pickle=True)
    tags = list(data["tags"])
    embs = data["embeddings"]
    if tag in tags:
        return False
    all_tags = tags + [tag]
    all_embs = np.concatenate([embs, np.array(vec, dtype=np.float32)[None]], axis=0)
    np.savez_compressed(path, tags=np.array(all_tags), embeddings=all_embs)
    return True


if __name__ == "__main__":
    main()
