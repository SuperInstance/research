"""
jev_client.py — minimal JEV (TypeSafe) client for many-call discovery.

Endpoints:
  GET  /v1/models                          — list models
  POST /v1/systemone                       — ask questions about content

Question types:
  noul:   yes/no question. Returns {type: noul, noul: 0.99}
  choice: pick from named criteria. Returns {type: choice, choice: {name: prob, ...}}
  score:  rate on ordered criteria. Returns {type: score, score: 0..N-1, score_probabilities: [...]}
"""
import json, os, time, urllib.request, urllib.error, random

BASE = "https://api.typesafe.ai"
HDR = lambda: {
    "Authorization": f"Bearer {os.environ['TYPESAFEAI_KEY']}",
    "Content-Type": "application/json",
    "User-Agent": "mavis-jev/1.0",
}


def _post(path, payload, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST", headers=HDR())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _get(path, timeout=15):
    req = urllib.request.Request(BASE + path, headers=HDR())
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def list_models():
    return _get("/v1/models")


def ask(state, questions, model="jev-latest", timeout=30):
    """state: any content (string, dict, list).
       questions: dict of {name: question_spec}.
       Returns the raw response."""
    return _post("/v1/systemone",
                 {"state": state, "model": model, "questions": questions},
                 timeout=timeout)


# === Helper builders ===

def noul(instructions, criteria=None):
    q = {"type": "noul", "instructions": instructions}
    if criteria:
        q["criteria"] = criteria
    return q


def choice(instructions, criteria):
    """criteria: dict of {name: description}"""
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def score(instructions, criteria):
    """criteria: ordered list of descriptions (position = score)"""
    return {"type": "score", "instructions": instructions, "criteria": criteria}


# === Examples ===

if __name__ == "__main__":
    print("Models:", json.dumps(list_models(), indent=2)[:500])

    # Test all 3 types in one call
    r = ask(
        "Quilt cells form communities that grow and die like organisms. The canary witnesses the joint state.",
        {
            "is_biological": noul("Does this text use biological metaphors?"),
            "doctrine_type": choice(
                "Which doctrine does this express?",
                {
                    "morphogenesis": "growth from fuel and pressure",
                    "witness_chain": "ledger of receipts",
                    "polyformality": "same doctrine across substrates",
                    "agreement_binding": "intelligence from agreements"
                }
            ),
            "complexity": score(
                "Rate the conceptual complexity",
                ["trivial", "moderate", "deep", "frontier"]
            )
        }
    )
    print(json.dumps(r, indent=2))
