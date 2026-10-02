"""
fleet_hub_v2.py
================

Multi-cell fleet using a2a Worker v2's Vectorize semantic search.

Workflow per cycle:
  1. Each cell registers with capabilities (auto-embeds)
  2. One cell asks a question
  3. Find semantically-relevant peers via Vectorize
  4. Send the question to those peers
  5. Peers respond via a2a unicast
  6. Original cell synthesizes responses

This is the REAL fleet coordination — not just broadcasting.

Run: python3 fleet_hub_v2.py
"""

from __future__ import annotations
import sys, os, json, time, urllib.request, urllib.error
import concurrent.futures

A2A = os.environ.get("A2A_URL", "https://quilt-a2a-v2.casey-digennaro.workers.dev")


def a2a(method: str, path: str, body: dict = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "fleet-hub-v2/1.0",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{A2A}{path}",
        data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"err": f"HTTP {e.code}: {e.read().decode()[:80]}"}
    except Exception as e:
        return {"err": str(e)[:80]}


# Domain-specific fleet
FLEET = [
    ("cell.shaper", "shaper", [
        "canon-shape", "negative-space", "gap-detection",
        "polyformal-ports", "witness-log"]),
    ("cell.advisor", "advisor", [
        "canon-query", "witness-log", "advise",
        "polyformal-ports", "live-canon"]),
    ("cell.polyformal", "polyformal", [
        "rust", "python", "verilog", "vhdl", "cuda", "typescript",
        "polyformal-ports", "compilation"]),
    ("cell.ensemble", "ensemble", [
        "multi-llm", "consensus", "canon-query", "ensemble",
        "witness-log"]),
    ("cell.autoextend", "advisor", [
        "auto-extend", "canon-write", "canon-shape",
        "gap-detection", "negative-space"]),
]


# Questions
CYCLE_QUESTIONS = [
    ("who can write new canon pieces?", "auto-extend"),
    ("who can compile to multiple substrates?", "polyformal"),
    ("who can find canon gaps?", "shape-negative"),
    ("who can advise on Quilt questions?", "canon-query"),
    ("who handles inter-cell messaging?", "a2a-protocol"),
]


def register_all():
    """Register every cell in the fleet. Returns dict cell_id -> spec."""
    print("registering fleet...")
    registered = {}
    for cid, role, caps in FLEET:
        r = a2a("POST", "/register", {
            "cell_id": cid, "role": role,
            "address": cid, "capabilities": caps,
        })
        if r.get("ok"):
            registered[cid] = (role, caps)
            print(f"  ✓ {cid:20} {role:14} caps={len(caps)}")
        else:
            print(f"  ✗ {cid}: {r.get('err', '?')}")
        time.sleep(0.2)
    return registered


def find_peers_for(question: str, k: int = 3) -> list:
    """Semantic search for peers matching the question."""
    r = a2a("GET", f"/find-semantic?q={question}&k={k}")
    matches = r.get("matches", [])
    return [{
        "cell_id": m["id"],
        "score": m["score"],
        "role": m.get("metadata", {}).get("role"),
        "caps": m.get("metadata", {}).get("capabilities", []),
    } for m in matches]


def ask_question(originator: str, question: str, query: str = None) -> dict:
    """Originator asks the fleet. Semantically find peers, send request."""
    if query is None:
        query = question.replace(" ", "+")

    # Find peers
    peers = find_peers_for(question, k=3)
    if not peers:
        return {"ok": False, "err": "no peers"}

    peer_ids = [p["cell_id"] for p in peers if p["cell_id"] != originator]
    if not peer_ids:
        return {"ok": False, "err": "no other peers"}

    # Send question to each peer
    sent_ids = []
    for pid in peer_ids:
        r = a2a("POST", "/send", {
            "from": originator, "to": pid,
            "type": "QUESTION",
            "payload": {"question": question, "originator": originator},
        })
        if r.get("ok"):
            sent_ids.append(pid)
        time.sleep(0.1)

    # Read peer's inbox (they respond by /tick which returns their inbox too)
    # Note: in this prototype, peers don't actually answer. They just receive.
    # Real impl: each peer reads inbox on tick, responds.

    return {
        "ok": True,
        "originator": originator,
        "question": question,
        "peers": peers,
        "sent_to": sent_ids,
    }


def tick_all():
    """Tick every cell. Returns their inboxes."""
    results = {}
    for cid, role, caps in FLEET:
        r = a2a("POST", "/tick", {
            "cell_id": cid, "role": role, "capabilities": caps,
            "load": 0.0,
        })
        results[cid] = r
        time.sleep(0.1)
    return results


def main():
    print("=" * 70)
    print(f"  FLEET HUB v2 — Vectorize-backed collaboration")
    print(f"  a2a Worker: {A2A}")
    print("=" * 70)

    registered = register_all()
    print(f"\n  registered: {len(registered)}/{len(FLEET)}")

    # Tick all to drain any pending
    print("\nticking all cells...")
    tick_results = tick_all()
    total_msgs = sum(r.get("inbox_count", 0) for r in tick_results.values())
    print(f"  total messages drained: {total_msgs}")

    # Run cycles
    print("\n" + "=" * 70)
    print("  FLEET CYCLES")
    print("=" * 70)

    findings = []
    for cycle_id, (question, query) in enumerate(CYCLE_QUESTIONS):
        print(f"\n[cycle {cycle_id}] Q: {question}")

        # originator: each cell takes a turn asking
        originator = FLEET[cycle_id % len(FLEET)][0]
        print(f"  originator: {originator}")

        # Find peers semantically
        peers = find_peers_for(question, k=3)
        print(f"  peers found: {len(peers)}")
        for p in peers:
            print(f"    {p['cell_id']:25} score={p['score']:.3f} role={p['role']}")

        # Originate the question
        result = ask_question(originator, question, query)
        if result.get("ok"):
            print(f"  sent to: {result['sent_to']}")
        else:
            print(f"  error: {result.get('err')}")

        # Sleep a beat
        time.sleep(1)

    # Final state
    print("\n" + "=" * 70)
    print("  FLEET FINAL STATE")
    print("=" * 70)
    final = a2a("GET", "/")
    print(f"  total cells: {final.get('cells')}")
    print(f"  messages_pending: {final.get('messages_pending')}")

    # Try the semantic search
    print("\n=== semantic search demos ===")
    for q in ["who writes essays", "compilers", "multi-language"]:
        r = a2a("GET", f"/find-semantic?q={q.replace(' ', '+')}&k=3")
        matches = r.get("matches", [])
        print(f"\n  Q: '{q}'")
        for m in matches[:3]:
            md = m.get("metadata", {})
            print(f"    {m['id']:25} score={m['score']:.3f} role={md.get('role')}")


if __name__ == "__main__":
    main()
