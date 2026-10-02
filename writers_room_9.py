#!/usr/bin/env python3
"""Writers' room round 9: 3 voices × 4 topics on the latest demos."""
import os, json, time, urllib.request, concurrent.futures

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/writers_room_9"
os.makedirs(OUT, exist_ok=True)

PROVIDERS = {
    "zai": {"url": "https://api.z.ai/api/coding/paas/v4/chat/completions", "model": "glm-4.5", "extra": {"thinking": {"type": "disabled"}}},
    "deepinfra-deepseek": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "deepseek-ai/DeepSeek-V4-Flash"},
    "deepinfra-qwen": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "Qwen/Qwen3-235B-A22B-Instruct-2507"},
}

TOPICS = [
    ("the-ca-gallery", "The CA gallery. 250 words on 10 cellular automaton rules running side-by-side, where Conway's elegance and Wireworld's complexity emerge from the same hash function."),
    ("the-mandelbrot-key", "The Mandelbrot key. 250 words on a hash-seeded Julia set, where every name becomes a unique fractal — same name, same c, same infinite boundary."),
    ("the-texture-of-fbm", "The texture of FBM. 250 words on 6 filters (wood/marble/cloud/fire/water/stone) that all share the same FBM noise substrate."),
    ("the-kingdom-cartographer", "The kingdom cartographer. 250 words on a procedural map where FNV-1a(x, y) decides biome, and where the same kingdom is drawn from the same hash every time."),
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
