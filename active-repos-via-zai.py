#!/usr/bin/env python3
"""
active-repos-via-zai.py — ZAI generates the canonical "what we're working on" doc.

Feeds ZAI the actively-worked repos and asks it to produce:
- repo name + GH URL
- unique purpose (1 sentence)
- what's being done to make it production-ready
- overall goal / outcome
"""
import os, json, urllib.request, subprocess, re
from pathlib import Path

ZAI = "https://api.z.ai/api/coding/paas/v4/chat/completions"
KEY = os.environ["ZAI_TOKEN"]
OUT = Path("/workspace/research/active-repos-report.md")

# Hand-curated list of the most actively-worked-on quilt-* repos
REPOS = [
    ("quilt-cli",                "https://github.com/SuperInstance/quilt-cli",
     "Unified CLI for the fleet — 21 commands"),
    ("quilt-bootstrap",          "https://github.com/SuperInstance/quilt-bootstrap",
     "Fleet bootstrap — restore 13 walkers from a single command"),
    ("quilt-brewer",             "https://github.com/SuperInstance/quilt-brewer",
     "Recipe-driven walker factory — grow walkers from recipes"),
    ("quilt-fleet-snapshot",     "https://github.com/SuperInstance/quilt-fleet-snapshot",
     "Fleet-state tarball — the wipe-problem solver"),
    ("quilt-schema-registry",    "https://github.com/SuperInstance/quilt-schema-registry",
     "Schema validator — every walker self-registers here"),
    ("quilt-trace",              "https://github.com/SuperInstance/quilt-trace",
     "Receipt log → HTML landing page renderer"),
    ("quilt-perception",         "https://github.com/SuperInstance/quilt-perception",
     "Sensor-stream walker — 6 perception slots, polarity rules"),
    ("quilt-fable",              "https://github.com/SuperInstance/quilt-fable",
     "Multi-voice narrative walker — chord composition"),
    ("quilt-orchestrator",       "https://github.com/SuperInstance/quilt-orchestrator",
     "DAG composer — plan/execute/compose/validate"),
    ("quilt-linker",             "https://github.com/SuperInstance/quilt-linker",
     "Graph linker — find/resolve/compose chains across the fleet"),
    ("quilt-canon-witness",      "https://github.com/SuperInstance/quilt-canon-witness",
     "Cryptographic witness log — FNV-1a 64-chained append-only ledger"),
    ("quilt-canary-port",        "https://github.com/SuperInstance/quilt-canary-port",
     "Polyformalism canary — fnv1a-64 byte-exact across substrates"),
    ("quilt-organism",           "https://github.com/SuperInstance/quilt-organism",
     "Corpus walker — explores cells across substrates"),
    ("quilt-optimization",       "https://github.com/SuperInstance/quilt-optimization",
     "cuOpt substrate — VRP + linear programming"),
    ("quilt-cell-harness",       "https://github.com/SuperInstance/quilt-cell-harness",
     "Cell / Quilt / Qult algebra — fractal morphogenesis"),
    ("quilt-multi-oracle",       "https://github.com/SuperInstance/quilt-multi-oracle",
     "Multi-LLM chord oracle — ZAI/DeepSeek/DeepInfra consensus"),
    ("quilt-canon-witness-witness", "https://github.com/SuperInstance/quilt-canon-witness-witness",
     "Witness about the witness — meta-canon ledger"),
    ("quilt-jev-oracle",         "https://github.com/SuperInstance/quilt-jev-oracle",
     "JEV canon-promotion oracle — 22 questions"),
    ("quilt-jev-toolkit",        "https://github.com/SuperInstance/quilt-jev-toolkit",
     "JEV toolkit — typesafe.ai/JEV client + canon gate"),
    ("quilt-spreadsheet-inference", "https://github.com/SuperInstance/quilt-spreadsheet-inference",
     "Spreadsheet exo-model — Jepa + JEV + MOTH + LLM cells"),
    ("quilt-fluidics",           "https://github.com/SuperInstance/quilt-fluidics",
     "Coupling Charter compiled — Reynolds rider + zigzag-jig"),
    ("quilt-fold",               "https://github.com/SuperInstance/quilt-fold",
     "Frame + Fold + Cycle + Rain + Tiling abstraction"),
    ("quilt-full-stack-demo",    "https://github.com/SuperInstance/quilt-full-stack-demo",
     "Single-file canonical hello-world of the entire stack"),
    ("quilt-port",               "https://github.com/SuperInstance/quilt-port",
     "User-facing production port — cost-plus economics"),
    ("quilt-cli-sprint",         None,
     "Sprint lineage for the CLI — each sprint declares its successor"),
    ("quilt-research-canons",    "https://github.com/SuperInstance/quilt-research-canons",
     "Discoverable research artifacts bundle for other agents"),
    ("jev-quilt",                "https://github.com/SuperInstance/jev-quilt",
     "JEV canonical SDK — 81 tests passing via stdlib, no pytest"),
    ("quilt-port",               "https://github.com/SuperInstance/quilt-port",
     "User-facing port — multi-tier projection (Python/Web/ESP32/Ideation)"),
    ("superinstance-advisor",    None,
     "Taps creative-break harness — 22+ wipe-survivor rounds"),
    ("api-orchestra",            "https://github.com/SuperInstance/api-orchestra",
     "Multi-LLM creative chorus — 6 ZAI + 12 DeepInfra critics"),
    ("polyglot-review",          "https://github.com/SuperInstance/polyglot-review",
     "12-lens code review — each model reviews as a different language"),
]


PROMPT_HEADER = """Produce a markdown document — the canonical "what we're working on" report for the Quilt fleet.

For EACH repo, give these 4 fields in a table column OR as bullets:
- **purpose** (1 sentence, what it does — clearly distinct from siblings)
- **road to production-ready** (1-2 lines, what's still blocking it from being truly production-grade — tests, packaging, CI, refactor, etc.)
- **goal** (1 sentence, what we're trying to achieve)
- **unique contribution** (1 sentence, what makes this repo distinct from the rest of the fleet)

Use the input below. Output a single markdown document with a top-level TL;DR, then for each repo one section.

The voice: the steward. The tone: clear and honest about status, no marketing fluff.

```"""

repos_text = "\n".join(f"- {name}: {url or '(local only)'} — {purpose}"
                       for name, url, purpose in REPOS)
prompt = PROMPT_HEADER + repos_text + "\n```"

body = json.dumps({
    "model": "glm-4.5-flash",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 4000,
    "temperature": 0.6,
    "thinking": {"type": "disabled"},
}).encode()
req = urllib.request.Request(ZAI, data=body, headers={
    "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
    "User-Agent": "mavis-active-reports/1.0",
})
for attempt in range(3):
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content:
            OUT.write_text(content)
            print(f"Wrote {OUT} ({len(content)} chars)")
            break
    except Exception as e:
        print(f"  attempt {attempt+1}: {str(e)[:80]}")
        import time; time.sleep(8)
