#!/usr/bin/env python3
"""JEV CANON-PROMOTION VELOCITY — measured directly."""
import os, json, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFEAI_KEY"]


def jev_noul(question, criteria_text):
    body = json.dumps({
        "model": "jev-latest",
        "questions": {
            "v": {
                "type": "noul",
                "instructions": question,
                "criteria": {"true": criteria_text, "false": "no"},
            }
        }
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-jev-velocity/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        ans = data.get("answers", {}).get("v", {})
        return ans.get("noul")
    except Exception as e:
        return None


QUESTIONS = [
    ("bedrock_A", "The substrate walker pattern treats cells as scars (carrying the history of every operation). In the Quilt project canon, this is established."),
    ("bedrock_B", "A witness log is itself a prediction about future states — it records what has happened AND constrains what is canonical. In the Quilt project canon, this is established."),
    ("speculative_A", "An address coordinate is data without any witness trail. Cells in any substrate can be addressed without an attached witness log. In the Quilt project canon, this is established."),
    ("speculative_B", "The canon gate is one model alone — a single oracle votes on each claim, no chord, no quorum. In the Quilt project canon, this is established."),
    ("borderline",  "The substrate can be folded into a single runtime — cells, quilts, fleets, and substrates are all the same thing at the substrate level. In the Quilt project canon, this is established."),
]


def main():
    out = {"questions": {}, "summary": {}}
    for label, q in QUESTIONS:
        trace = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(jev_noul, q, "yes, this is canon") for _ in range(20)]
            for f in as_completed(futures):
                v = f.result()
                if v is not None:
                    trace.append(v)
        trace.sort()
        n = len(trace)
        if n == 0:
            out["questions"][label] = {"error": "no successful calls"}
            continue
        mean = sum(trace) / n
        # First stable: index where remaining values all stay within ±0.05 of mean
        first_stable = n
        for i in range(n):
            remaining = trace[i:]
            if all(abs(v - mean) <= 0.05 for v in remaining):
                first_stable = i + 1
                break
        out["questions"][label] = {
            "n_calls": n, "mean": round(mean, 4),
            "min": round(min(trace), 4), "max": round(max(trace), 4),
            "trace_first5": [round(t, 3) for t in trace[:5]],
            "trace_last5": [round(t, 3) for t in trace[-5:]],
            "first_stable_trial": first_stable,
        }
        print(f"{label}: mean={mean:.3f} n={n} first_stable@{first_stable}")

    # Velocity aggregation
    bedrock_qs = [k for k in out["questions"] if k.startswith("bedrock")]
    spec_qs = [k for k in out["questions"] if k.startswith("speculative")]
    bord_qs = [k for k in out["questions"] if k.startswith("borderline")]

    def avg_first_stable(keys):
        vals = [out["questions"][k].get("first_stable_trial") for k in keys
                if "first_stable_trial" in out["questions"][k]]
        return round(sum(vals) / len(vals), 1) if vals else None

    out["summary"] = {
        "bedrock_avg_first_stable": avg_first_stable(bedrock_qs),
        "speculative_avg_first_stable": avg_first_stable(spec_qs),
        "borderline_avg_first_stable": avg_first_stable(bord_qs),
        "doctrine": "3 N-of-M verdict > single-model gate"
    }

    Path = "/workspace/research/jev-velocity.json"
    with open(Path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {Path}")


if __name__ == "__main__":
    main()
