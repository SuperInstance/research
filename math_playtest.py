#!/usr/bin/env python3
"""Multi-reviewer playtest on the new math demos."""
import os, json, urllib.request, concurrent.futures, time

DEMOS = {
    "ann-search": "https://raw.githubusercontent.com/SuperInstance/AI-Writings/master/cellular-first-design/ann-search/index.html",
    "quantum-dance": "https://raw.githubusercontent.com/SuperInstance/AI-Writings/master/cellular-first-design/quantum-dance/index.html",
}

REVIEW_PROMPT = """You are a skeptical reviewer evaluating a single-file browser demo of substrate math.

Demo URL: {url}

Open it (or fetch the source via the URL). Rate on a scale of 1-10 (10=excellent):

Q1. First-impression clarity — does the page immediately tell you what it does and why it matters?
Q2. Navigation/usability — can you figure out how to interact with it without external help?
Q3. Mathematical credibility — does the demo show actual math (not fake animations or hand-waving)?
Q4. Verifiability — could you, as a reviewer, independently confirm the math is correct?

Then briefly (3-5 sentences): the ONE thing the author could do to make this demo more impressive to an outside technical reviewer.

Be honest. Don't be polite. If it's broken, say so. If it's brilliant, say so. If it's 6/10, say 6/10.

Return JSON ONLY:
{{"q1":N,"q2":N,"q3":N,"q4":N,"one_fix":"..."}}
"""

PROVIDERS = {
    "zai": {
        "url": "https://api.z.ai/api/coding/paas/v4/chat/completions",
        "model": "glm-4.5",
        "extra": {"thinking": {"type": "disabled"}},
    },
    "deepinfra-deepseek": {
        "url": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "deepseek-ai/DeepSeek-V4-Flash",
    },
    "deepinfra-qwen": {
        "url": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "Qwen/Qwen3-235B-A22B-Instruct-2507",
    },
}

def fetch_source(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"FETCH_ERROR: {e}"

def call(provider, prompt):
    cfg = PROVIDERS[provider]
    token = os.environ.get("DEEPINFRA_TOKEN") if "deepinfra" in provider else os.environ.get("ZAI_TOKEN")
    if not token:
        return {"provider": provider, "error": "no token"}
    body = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": "You are a skeptical technical reviewer. Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 600,
        "temperature": 0.4,
    }
    if "extra" in cfg:
        body.update(cfg["extra"])
    req = urllib.request.Request(cfg["url"], data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
            text = data["choices"][0]["message"]["content"].strip()
            return {"provider": provider, "model": cfg["model"], "text": text}
    except Exception as e:
        return {"provider": provider, "error": str(e)}

def parse_json(text):
    # Strip code fences if any
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        t = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    # Find first { and last }
    s = t.find("{")
    e = t.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(t[s:e+1])
    except Exception:
        return None

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/math_playtest"
os.makedirs(OUT, exist_ok=True)

results = {}
for slug, url in DEMOS.items():
    print(f"\n=== {slug} ===")
    src = fetch_source(url)
    if src.startswith("FETCH_ERROR"):
        print(f"  FETCH ERROR: {src}")
        continue
    # Trim to first 8000 chars to fit context
    src_excerpt = src[:8000]
    prompt = REVIEW_PROMPT.format(url=url) + f"\n\nSOURCE EXCERPT (first 8000 chars):\n```html\n{src_excerpt}\n```"
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(call, p, prompt): p for p in PROVIDERS}
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            p = r.get("provider", "")
            if "text" in r:
                parsed = parse_json(r["text"])
                if parsed:
                    parsed["provider"] = r["provider"]
                    parsed["model"] = r["model"]
                    results.setdefault(slug, []).append(parsed)
                    print(f"  [{p}] {parsed.get('q1')}/{parsed.get('q2')}/{parsed.get('q3')}/{parsed.get('q4')} — fix: {parsed.get('one_fix', '')[:80]}")
                else:
                    print(f"  [{p}] PARSE ERROR: {r['text'][:200]}")
            else:
                print(f"  [{p}] ERROR: {r.get('error', '')[:80]}")
    time.sleep(2)

# Aggregate
print("\n=== AGGREGATE ===")
for slug, reviews in results.items():
    if reviews:
        n = len(reviews)
        q1 = sum(r.get('q1', 0) for r in reviews) / n
        q2 = sum(r.get('q2', 0) for r in reviews) / n
        q3 = sum(r.get('q3', 0) for r in reviews) / n
        q4 = sum(r.get('q4', 0) for r in reviews) / n
        print(f"  {slug}: Q1={q1:.1f} Q2={q2:.1f} Q3={q3:.1f} Q4={q4:.1f} (n={n})")

with open(f"{OUT}/playtest_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT}/playtest_results.json")
