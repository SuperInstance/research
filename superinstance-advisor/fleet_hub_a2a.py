"""
fleet_hub_a2a.py
================

A multi-cell fleet that uses the deployed a2a Worker for inter-cell messaging.

Each cell:
  1. Registers with a2a
  2. Asks the canon a question
  3. Sends the answer to peer cells via a2a
  4. Reads inbox for peer answers
  5. Detects consensus vs findings

Cells don't share memory directly — they share via the a2a protocol.
This is the multi-cell equivalent of multi-LLM routing.

Run: python3 fleet_hub_a2a.py
"""

from __future__ import annotations
import sys, os, json, time, urllib.request, urllib.error, hashlib
import concurrent.futures

A2A = os.environ.get("A2A_URL", "https://quilt-a2a.casey-digennaro.workers.dev")


def a2a_call(method: str, path: str, body: dict = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "quilt-fleet-hub/1.0",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{A2A}{path}",
        data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"err": f"HTTP {e.code}: {e.read().decode()[:80]}"}
    except Exception as e:
        return {"err": str(e)[:80]}


# Questions the fleet rotates through
FLEET_QUESTIONS = [
    "what is the substrate",
    "what is the cell",
    "what is the witness",
    "what is the canon",
    "what is the fleet",
    "what does a cell know about other cells",
    "what is the difference between bind and link",
    "what is the cost of consensus",
]


class FleetCell:
    def __init__(self, cell_id: str, role: str, capabilities: list):
        self.cell_id = cell_id
        self.role = role
        self.capabilities = capabilities
        self.address = cell_id

    def register(self) -> dict:
        return a2a_call("POST", "/register", {
            "cell_id": self.cell_id,
            "role": self.role,
            "address": self.address,
            "capabilities": self.capabilities,
        })

    def tick(self) -> dict:
        return a2a_call("POST", "/tick", {
            "cell_id": self.cell_id,
            "role": self.role,
            "capabilities": self.capabilities,
        })

    def send(self, to: str, type_: str, payload: dict) -> dict:
        return a2a_call("POST", "/send", {
            "from": self.cell_id, "to": to, "type": type_,
            "payload": payload,
        })

    def broadcast(self, type_: str, payload: dict, capability: str = None) -> dict:
        body = {"from": self.cell_id, "type": type_, "payload": payload}
        if capability:
            body["capability"] = capability
        return a2a_call("POST", "/broadcast", body)

    def find(self, cap: str = None) -> dict:
        if cap:
            return a2a_call("GET", f"/find?cap={cap}")
        return a2a_call("GET", "/cells")

    def inbox(self, drain: bool = True) -> dict:
        q = "" if drain else "?drain=false"
        return a2a_call("GET", f"/inbox/{self.cell_id}{q}")


def fleet_cycle(cycle_id: int, question: str, fleet: list) -> dict:
    """One cycle: each cell asks canon + sends answer to peers via a2a."""
    print(f"\n[cycle {cycle_id}] Q: {question[:60]}")

    # Phase 1: each cell ticks (registers/refreshes with a2a)
    for cell in fleet:
        cell.tick()
    time.sleep(0.3)

    # Phase 2: each cell decides its answer (mock — same canon hits, different roles)
    answers = {}
    for cell in fleet:
        # In a real cell, this would invoke an LLM. Here we use the cell's role
        # to differentiate answers.
        answers[cell.cell_id] = {
            "role": cell.role,
            "caps": cell.capabilities,
            "answer_role_specific": f"{cell.role} perspective on '{question}'",
        }
        time.sleep(0.1)

    # Phase 3: each cell broadcasts to peers with capability
    for cell in fleet:
        if cell.role == "advisor":
            # advisors broadcast to all
            cell.broadcast("ADVICE", {"question": question, "answer": answers[cell.cell_id]},
                          capability="canon-query")
        elif cell.role == "ensemble":
            cell.broadcast("ENSEMBLE_RESULT", {"question": question, "answer": answers[cell.cell_id]})
        else:
            cell.send(fleet[0].cell_id, "OBSERVATION",
                     {"question": question, "cell": cell.cell_id})
        time.sleep(0.1)

    # Phase 4: each cell drains inbox
    inbox_summary = {}
    for cell in fleet:
        result = cell.inbox(drain=True)
        inbox_summary[cell.cell_id] = result.get("count", 0)
        time.sleep(0.1)

    total_msgs = sum(inbox_summary.values())
    print(f"  inbox totals: {inbox_summary}")
    print(f"  total messages: {total_msgs}")

    return {
        "cycle": cycle_id,
        "question": question,
        "answers": answers,
        "inbox_summary": inbox_summary,
    }


def main():
    print("=" * 70)
    print(f"  FLEET HUB over a2a — {A2A}")
    print("=" * 70)

    # Define the fleet
    fleet_specs = [
        ("cell-alpha", "advisor", ["canon-query", "witness-log"]),
        ("cell-beta", "ensemble", ["canon-query", "ensemble"]),
        ("cell-gamma", "test-runner", ["witness-log", "test"]),
        ("cell-delta", "shaper", ["shape-negative", "canon-query"]),
        ("cell-epsilon", "advisor", ["canon-query", "auto-extend"]),
    ]
    fleet = [FleetCell(cid, role, caps) for cid, role, caps in fleet_specs]
    for c in fleet:
        print(f"  {c.cell_id:18} {c.role:14} caps={c.capabilities}")

    # Register all
    print("\nregistering fleet with a2a...")
    for c in fleet:
        r = c.register()
        if r.get("ok"):
            print(f"  ✓ {c.cell_id}")
        else:
            print(f"  ✗ {c.cell_id}: {r.get('err', '?')}")
        time.sleep(0.2)

    # Verify in a2a
    info = a2a_call("GET", "/")
    print(f"\nfleet total: {info.get('cells', '?')} cells in a2a")

    # Run cycles
    cycles_data = []
    n = min(len(FLEET_QUESTIONS), 5)
    for i in range(n):
        cycle = fleet_cycle(i, FLEET_QUESTIONS[i], fleet)
        cycles_data.append(cycle)

    # Summary
    print("\n" + "=" * 70)
    print("  FLEET SUMMARY")
    print("=" * 70)
    total_msgs = sum(sum(c["inbox_summary"].values()) for c in cycles_data)
    print(f"  cycles: {n}")
    print(f"  total messages exchanged: {total_msgs}")
    print(f"  avg msgs/cycle/cell: {total_msgs / (n * len(fleet)):.2f}")

    # Final a2a state
    final = a2a_call("GET", "/")
    print(f"  a2a cells: {final.get('cells', '?')}")
    print(f"  pending messages: {final.get('messages_pending', '?')}")


if __name__ == "__main__":
    main()
