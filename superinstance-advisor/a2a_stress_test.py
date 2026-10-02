"""
a2a_stress_test.py
==================

Push the a2a Worker hard. Multiple cells register, send, broadcast,
drain inboxes, search by capability.

Run: python3 a2a_stress_test.py
"""

from __future__ import annotations
import sys, os, json, time, urllib.request, urllib.error
import concurrent.futures
import random
import string

A2A = "https://a2a.superinstance.dev"


def call(method: str, path: str, body: dict = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "quilt-a2a-stress-test/1.0",
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


def random_id(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def register_cell(args):
    cid, role, caps = args
    return call("POST", "/register", {
        "cell_id": cid, "role": role, "capabilities": caps
    })


def send_msg(args):
    f, to, t, payload = args
    return call("POST", "/send", {"from": f, "to": to, "type": t, "payload": payload})


def drain_inbox(args):
    cid, = args
    return call("GET", f"/inbox/{cid}")


def find_cells(cap):
    return call("GET", f"/find?cap={cap}")


def main():
    print("=" * 70)
    print("  A2A STRESS TEST — multiple cells, send/broadcast/drain")
    print("=" * 70)

    # Phase 1: Register 10 cells
    print("\nphase 1: register 10 cells (sequential, with throttle)")
    cell_specs = []
    for i in range(10):
        cid = f"stress-{random_id()}"
        role = random.choice(["advisor", "test-runner", "ensemble", "shaper"])
        caps = random.sample(["canon-query", "witness-log", "auto-extend",
                              "shape-negative", "polyformal", "vectorize"],
                             k=random.randint(2, 5))
        cell_specs.append((cid, role, caps))

    registered = []
    for spec in cell_specs:
        r = register_cell(spec)
        if r.get("ok"):
            registered.append(r)
        time.sleep(0.2)  # throttle

    print(f"  registered: {len(registered)}/10")
    print(f"  cells: {[c[0] for c in cell_specs[:5]]}...")

    # Phase 2: Send 20 messages (10 unicast, 10 broadcast)
    print("\nphase 2: 20 messages (10 unicast, 10 broadcast)")
    cells = [c[0] for c in cell_specs]
    msg_tasks = []
    for i in range(10):
        f, t = random.sample(cells, 2)
        msg_tasks.append((f, t, "REQUEST", {"ask": f"q{i}"}))
    broadcast_tasks = []
    for i in range(10):
        cap = random.choice(["auto-extend", "canon-query", "shape-negative"])
        broadcast_tasks.append((random.choice(cells), "EVENT",
                               {"data": f"event-{i}"}, cap))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        send_results = list(ex.map(send_msg, msg_tasks))
        time.sleep(0.5)
        bc_results = list(ex.map(lambda a: call("POST", "/broadcast",
            {"from": a[0], "type": a[1], "payload": a[2], "capability": a[3]}),
            broadcast_tasks))

    sent_ok = sum(1 for r in send_results if r.get("ok"))
    bc_ok = sum(1 for r in bc_results if r.get("ok"))
    bc_msgs = sum(r.get("delivered", 0) for r in bc_results if r.get("ok"))
    print(f"  unicast sent: {sent_ok}/10")
    print(f"  broadcasts:   {bc_ok}/10 (delivered {bc_msgs} messages)")

    # Phase 3: Drain all inboxes
    print("\nphase 3: drain all inboxes (sequential)")
    drain_results = []
    for c in cells:
        drain_results.append(drain_inbox((c,)))
        time.sleep(0.1)

    total_msgs = sum(r.get("count", 0) for r in drain_results)
    print(f"  total messages drained: {total_msgs}")

    # Phase 4: Capability search
    print("\nphase 4: capability search")
    for cap in ["auto-extend", "canon-query", "shape-negative"]:
        result = find_cells(cap)
        n = result.get("count", 0)
        print(f"  {cap:20}: {n} cells")

    # Phase 5: Tick (heartbeat)
    print("\nphase 5: tick heartbeat (sequential)")
    tick_tasks = [(c, "advisor", ["canon-query"]) for c in cells]
    tick_results = []
    for t in tick_tasks:
        tick_results.append(call("POST", "/tick",
            {"cell_id": t[0], "role": t[1], "capabilities": t[2]}))
        time.sleep(0.1)
    tick_ok = sum(1 for r in tick_results if r.get("ok"))
    total_inbox = sum(r.get("inbox_count", 0) for r in tick_results)
    print(f"  ticks: {tick_ok}/10 ok, inbox drained: {total_inbox} messages")

    # Final state
    print("\nfinal state:")
    info = call("GET", "/")
    print(f"  cells: {info.get('cells', 0)}")
    print(f"  messages_pending: {info.get('messages_pending', 0)}")

    print()
    print("=" * 70)
    print("  A2A STRESS TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
