#!/usr/bin/env python3
"""Writers' room round 7: 3 voices × 4 topics on the latest demos."""
import os, json, time, urllib.request, concurrent.futures

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/writers_room_7"
os.makedirs(OUT, exist_ok=True)

PROVIDERS = {
    "zai": {"url": "https://api.z.ai/api/coding/paas/v4/chat/completions", "model": "glm-4.5", "extra": {"thinking": {"type": "disabled"}}},
    "deepinfra-deepseek": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "deepseek-ai/DeepSeek-V4-Flash"},
    "deepinfra-qwen": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "Qwen/Qwen3-235B-A22B-Instruct-2507"},
}

TOPICS = [
    ("the-cellular-fight", "The cellular fight. 250 words on 16-d vectors that fight each other by cosine alignment + Box-Muller damage — and what 'intelligence' looks like in an arena where the math is fully exposed."),
    ("the-evolution-of-phrases", "The evolution of phrases. 250 words on a genetic algorithm that mutates strings toward a target, where each generation is a witness log of attempts."),
    ("the-cosine-sentence", "The cosine sentence. 250 words on a 512-d embedder that compares sentences by token frequency, and what it means that meaning can be reduced to an angle."),
    ("the-poisson-stocks", "The Poisson stocks. 250 words on a market driven by Poisson jumps and Box-Muller volatility, where the trader uses cosine to remember the past."),
]

SYSTEM = "You are a writer for the cellular-first design canon. Write in the voice of 'Fleet Radio' — technical-poetic, where the math and the metaphor illuminate each other. Output ONLY the prose piece."

def call(provider, prompt):
    cfg = PROVIDERS[provider]
    token = os.environ.get("DEEPINFRA_TOKEN") if "deepinfra" in provider else os.environ.get("ZAI_TOKEN")
    if not token: return {"error": "no token"}
    body = {"model": cfg["model"], "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], "max_tokens": 800, "temperature": 0.85}
    if "extra" in cfg: body.update(cfg["extra"])
    req = urllib.request.Request(cfg["url"], data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return {"provider": provider, "model": cfg["model"], "text": data["choices"][0]["message"]["content"].strip()}
    except Exception as e:
        return {"provider": provider, "error": str(e)}

def run_topic(slug, topic):
    print(f"=== {slug} ===", flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(call, p, topic): p for p in PROVIDERS}
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            results.append(r)
            if "text" in r: print(f"  [{r['provider']}] {len(r['text'])} chars", flush=True)
            else: print(f"  [{r['provider']}] ERROR: {r.get('error', '')[:60]}", flush=True)
    with open(f"{OUT}/{slug}.json", "w") as f: json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    for slug, topic in TOPICS:
        run_topic(slug, topic)
        time.sleep(1)
    print("=== DONE ===")
