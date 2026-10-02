#!/usr/bin/env python3
"""JEV CANON-PROMOTION VELOCITY — measured directly."""
import os, json, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFEAI_KEY"]

STATE = {
    "doctrines": ["cells are scars", "witness log is prediction",
                  "substrate is grown", "oracle is heard", "lenia flows"],
    "voice": "fleet radio",
    "facts": {"fnv1a_64bit": True, "substrate_count": 13},
}

QUESTIONS = [
    ("bedrock_A", "Cells are scars, not parameters. In the Quilt project canon, this is established."),
    ("bedrock_B", "The witness log is itself a prediction. In the Quilt project canon, this is established."),
    ("speculative_A", "An address coordinate is data without any witness trail. In the Quilt project canon, this is established."),
    ("speculative_B", "The canon gate is one model alone — a single oracle votes on each claim with no chord and no quorum. In the Quilt project canon, this is established."),
    ("borderline",  "The substrate can be folded into a single runtime — cells, quilts, fleets, and substrates are all the same thing at the substrate level. In the Quilt project canon, this is established."),
]


def jev_call(label, question):
    body = json.dumps({
        "model": "jev-latest",
        "state": STATE,
        "questions": {
            label: {"type": "noul", "instructions": question,
                    "criteria": {"true": "yes — this is established canon",
                                  "false": "no — this is speculative or rejected"}}
        }
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-jev-velocity/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return label, question, data.get("answers", {}).get(label, {}).get("noul")
    except Exception as e:
        return label, question, ("err", str(e)[:80])


def main():
    out = {"summary": {"doctrine": "3 N-of-M verdict > single-model gate"}}
    for label, q in QUESTIONS:
        trace = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = [ex.submit(jev_call, label, q) for _ in range(20)]
            for f in as_completed(futs):
                _, _, v = f.result()
                if isinstance(v, float):
                    trace.append(v)
        trace.sort()
        n = len(trace)
        if n == 0:
            out.setdefault("questions", {})[label] = {"error": "no successful calls"}
            print(f"{label}: NO successful calls")
            continue
        mean = sum(trace) / n
        # First stable: index where remaining all stay within ±0.05 of mean
        first_stable = n
        for i in range(n):
            if all(abs(v - mean) <= 0.05 for v in trace[i:]):
                first_stable = i + 1
                break
        out.setdefault("questions", {})[label] = {
            "n": n, "mean": round(mean, 4),
            "min": round(min(trace), 4), "max": round(max(trace), 4),
            "first_stable_trial": first_stable,
            "trace_first10": [round(t, 3) for t in trace[:10]],
        }
        print(f"{label}: mean={mean:.3f} n={n} first_stable@{first_stable}")

    out_path = "/workspace/research/jev-velocity.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
