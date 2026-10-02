#!/usr/bin/env python3
"""Math writers' room — 5 voices × 3 math topics, parallel."""
import os, json, time, urllib.request, concurrent.futures

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/math_writers_room"
os.makedirs(OUT, exist_ok=True)

PROVIDERS = {
    "zai": {
        "url": "https://api.z.ai/api/coding/paas/v4/chat/completions",
        "model": "glm-4.5",
        "extra": {"thinking": {"type":"disabled"}},
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "qwen/qwen3.8-27b",
    },
    "deepinfra": {
        "url": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "Qwen/Qwen3-235B-A22B-Instruct-2507",
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
    },
    "kimi": {
        "url": "https://api.deepinfra.com/v1/openai/chat/completions",
        "model": "moonshotai/Kimi-K2.7",
    },
}

TOPICS = [
    ("box-muller", "Box-Muller: how substrate-rng turns two coin flips into a Gaussian. 250 words on the substrate's bridge from discrete to continuous."),
    ("witness-is-prediction", "The witness log is itself a prediction: write 250 words on the JEV × JEPA Rosetta stone where validator and predictor are reflections."),
    ("ring-lwe", "Ring-LWE in 13 lines: 250 words on why post-quantum crypto isn't magic — it's polynomials and Gaussian noise."),
]

SYSTEM = "You are a writer for the cellular-first design canon. Write in the voice of 'Fleet Radio' — technical-poetic, where the math and the metaphor illuminate each other. Do NOT begin with 'Great question' or similar. Do NOT explain what you'll do. Output ONLY the prose piece."

def call(provider, prompt, retries=2):
    cfg = PROVIDERS[provider]
    env_map = {
        "zai": "ZAI_TOKEN",
        "groq": "GROQ_TOKEN",
        "deepinfra": "DEEPINFRA_TOKEN",
        "deepseek": "DEEPSEEK_TOKEN",
        "kimi": "DEEPINFRA_TOKEN",
    }
    token = os.environ.get(env_map[provider])
    if not token:
        return {"error": f"no token for {provider}"}
    body = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 800,
        "temperature": 0.85,
    }
    if "extra" in cfg:
        body.update(cfg["extra"])
    req = urllib.request.Request(
        cfg["url"],
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
                text = data["choices"][0]["message"]["content"].strip()
                return {"text": text, "provider": provider, "model": cfg["model"]}
        except Exception as e:
            last = e
            time.sleep(2 ** attempt)
    return {"error": str(last), "provider": provider}

def run_topic(slug, topic):
    print(f"=== {slug} ===", flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(call, p, topic): p for p in PROVIDERS}
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            results.append(r)
            if "text" in r:
                print(f"  [{r['provider']}] {len(r['text'])} chars", flush=True)
            else:
                print(f"  [{r['provider']}] ERROR: {r.get('error', '')[:60]}", flush=True)
    out_file = f"{OUT}/{slug}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    all_results = {}
    for slug, topic in TOPICS:
        all_results[slug] = run_topic(slug, topic)
        time.sleep(2)
    print("\n=== ALL DONE ===")
    for slug, results in all_results.items():
        n = sum(1 for r in results if "text" in r)
        print(f"  {slug}: {n}/{len(results)} voices succeeded")
