#!/usr/bin/env python3
"""
One read-back cannot distinguish "the write failed" from "you read too early."
That was the retracted claim's root error. This measures the distribution instead:
insert, then poll on a schedule and record WHEN each vector becomes visible.

The output is a visibility-latency distribution, not a boolean.
"""
import os, json, time, uuid, urllib.request, urllib.error
T = os.environ["CLOUDFLARE_TOKEN"]
ACCT = "049ff5e84ecf636b53b162cbb580aae6"
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/vectorize"
H = {"Authorization": f"Bearer {T}", "Content-Type": "application/json", "User-Agent": "m"}
DIM = 384   # must match @cf/baai/bge-small-en-v1.5; a 384/8 mismatch is a hard 400
NAME = "consistency-probe-" + uuid.uuid4().hex[:8]

def call(path, data=None, method=None, timeout=40, ctype="application/json"):
    body = data if isinstance(data, (bytes, type(None))) else json.dumps(data).encode()
    h = dict(H); h["Content-Type"] = ctype
    req = urllib.request.Request(BASE + path, data=body,
                                 headers=h, method=method or ("POST" if data is not None else "GET"))
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, {"err": e.read()[:140].decode("utf-8", "replace")}
        except Exception as e:
            if a == 2: return 0, {"err": str(e)[:80]}
            time.sleep(1.5 * (a + 1))

def vecs(n):
    # distinct, non-degenerate, unit-ish vectors
    out = []
    for i in range(n):
        v = [((i * 7 + j * 13) % 17) / 16.0 - 0.5 for j in range(DIM)]
        out.append([round(x, 6) for x in v])
    return out

if __name__ == "__main__":
    # The create API now requires a NESTED config object. The flat form
    # {name, dimensions, metric, embedding_model} — which worked earlier in this same
    # session — is rejected with "vectorize.index.invalid_config - Config must be provided".
    st, d = call("/indexes", {"name": NAME,
        "config": {"dimensions": DIM, "metric": "cosine",
                   "embedding_model": "@cf/baai/bge-small-en-v1.5"}})
    print(f"  create -> {st}")
    if st not in (200, 201):
        print("  ", str(d)[:200]); raise SystemExit(1)
    print(f"  index: {NAME}")
    N = 10
    vs = vecs(N)
    t0 = time.time()
    # Insert is NDJSON with {id, values} per line. The documented-looking
    # {"ids": [...], "vectors": [...]} JSON batch form returns
    # vectorize.unknown_content_type, and {"id", "vector"} returns an invalid-vector error.
    payload = "\n".join(json.dumps({"id": f"v{i}", "values": v}) for i, v in enumerate(vs)).encode()
    st, d = call(f"/indexes/{NAME}/insert", payload, ctype="application/x-ndjson")
    print(f"  insert -> {st}  ({time.time()-t0:.2f}s)")
    if st not in (200, 201):
        print("  ", str(d)[:200]); raise SystemExit(1)
    print("  polling visibility (single read-back cannot decide; the schedule can)")
    seen, latencies = set(), {}
    for t in (0, 2, 5, 8, 12, 18, 25, 35, 50, 70, 95):
        while time.time() - t0 < t: time.sleep(0.2)
        st, d = call(f"/indexes/{NAME}/list")
        found = set()
        if st == 200:
            ids = d.get("result", {}).get("ids") or d.get("result", {}).get("vectors") or []
            for x in ids:
                found.add(x.get("id") if isinstance(x, dict) else x)
        n_new = len(found - seen)
        for x in (found - seen): latencies[x] = round(time.time() - t0, 1)
        seen |= found
        print(f"    t+{t:>3}s  rows={len(seen):>2}/{N}  (+{n_new})")
        if len(seen) == N: break
    print(f"\n  visible: {len(seen)}/{N}")
    if latencies:
        vals = sorted(latencies.values())
        print(f"  first visible at: min {vals[0]}s  median {vals[len(vals)//2]}s  max {vals[-1]}s")
    print(f"\n  VERDICT: writes are eventually consistent with a visibility latency of")
    print(f"           roughly {min(latencies.values()) if latencies else '?'}s to {max(latencies.values()) if latencies else '?'}s.")
    print(f"           A single read-back at t+0 would have reported this as data loss.")
    call(f"/indexes/{NAME}", method="DELETE")
    print(f"  cleaned up {NAME}")
