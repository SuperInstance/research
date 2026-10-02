#!/usr/bin/env python3
"""Multi-reviewer playtest round 4: 8 newest demos."""
import os, json, time, urllib.request, concurrent.futures

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/playtest_4"
os.makedirs(OUT, exist_ok=True)

PROVIDERS = {
    "zai": {"url": "https://api.z.ai/api/coding/paas/v4/chat/completions", "model": "glm-4.5", "extra": {"thinking": {"type": "disabled"}}},
    "deepinfra-deepseek": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "deepseek-ai/DeepSeek-V4-Flash"},
    "deepinfra-qwen": {"url": "https://api.deepinfra.com/v1/openai/chat/completions", "model": "Qwen/Qwen3-235B-A22B-Instruct-2507"},
}

DEMOS = [
    ("cellular-fight", "8-fighter battle arena. Each fighter is a 16-d vector with deterministic seed. Cosine alignment determines hit chance, Box-Muller modulates damage. HP and energy bars, auto-battle loop."),
    ("evo", "Genetic algorithm evolves to find a target phrase. Mutation rate 0.01-1.0, population size 20-500. Crossover + mutation. Fitness = char-match. Live top-12 viewer + best fitness chart."),
    ("sentence-encoder", "Token-frequency embedder (512-d). Cosine similarity over 51-sentence Fleet Radio corpus. Top-8 most similar sentences. Hash per query."),
    ("stocks", "Stock market sim. Poisson(λ) jumps + Box-Muller Gaussian volatility. Buy/sell buttons. Trading bot logic uses cosine-similarity to past."),
    ("graph", "CRDT graph editor. Click to add nodes (FNV-1a hash positions). Add edges via form. Recent ops log. Peer-merge via hash."),
    ("dna", "DNA sequence generator. FNV-1a(x,y,z) emits nucleotides (ATCG). Reverse complement + DNA→RNA transcription + codon translation to amino acids. GC content stat."),
    ("3d", "3D voxel field. FNV-1a(x,y,z) → live voxel. Drag to rotate, scroll to zoom. Adjustable size + density. Depth-sorted rendering."),
    ("mnist", "Hand-drawn digit recognizer. 280x280 canvas, 16-d cosine templates per digit 0-9. Live prediction while drawing. Top-10 confidence bars."),
]

QUESTION_TMPL = """You are reviewing a single-page HTML demo. Rate it on 4 dimensions from 0-10:

Q1. First impression: Is the visual design compelling? Does it look like a polished product?
Q2. Navigation: Are controls clear and obvious? Can a first-time user figure it out?
Q3. Credibility: Does it feel mathematically sound? Are there obvious issues with the demo?
Q4. Verifiability: Can a curious user verify the math is real? Are there debug panels?

Then suggest 1 specific improvement.

Output ONLY a JSON object with exactly: q1 (int 0-10), q2 (int 0-10), q3 (int 0-10), q4 (int 0-10), improvement (string)

Description of the demo: {description}

Respond ONLY with the JSON object, nothing else."""

def call(provider, prompt):
    cfg = PROVIDERS[provider]
    token = os.environ.get("DEEPINFRA_TOKEN") if "deepinfra" in provider else os.environ.get("ZAI_TOKEN")
    if not token: return {"error": "no token"}
    body = {"model": cfg["model"], "messages": [{"role": "system", "content": "You are a UX reviewer for the cellular-first design canon. Output strict JSON only."}, {"role": "user", "content": prompt}], "max_tokens": 200, "temperature": 0.4}
    if "extra" in cfg: body.update(cfg["extra"])
    req = urllib.request.Request(cfg["url"], data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            text = data["choices"][0]["message"]["content"].strip()
            start = text.find('{'); end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"raw": text}
    except Exception as e:
        return {"error": str(e)}

def review(slug, description):
    print(f"=== {slug} ===", flush=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(call, p, QUESTION_TMPL.format(description=description)): p for p in PROVIDERS}
        for f in concurrent.futures.as_completed(futs):
            try:
                r = f.result()
                r['_provider'] = futs[f]
                results.append(r)
                print(f"  [{futs[f]}] {json.dumps(r)[:120]}", flush=True)
            except Exception as e:
                print(f"  [{futs[f]}] ERROR: {e}", flush=True)
    with open(f"{OUT}/{slug}.json", "w") as f: json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    for slug, desc in DEMOS:
        review(slug, desc)
        time.sleep(1)
    print("=== DONE ===")
