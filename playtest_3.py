#!/usr/bin/env python3
"""Multi-reviewer playtest round 3: 11 latest demos."""
import os, json, time, urllib.request, concurrent.futures

OUT = "/workspace/repos/ai-writings/cellular-first-design/reports/playtest_3"
os.makedirs(OUT, exist_ok=True)

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

DEMOS = [
    ("d20", "A D&D-style dice roller. xoshiro256** for rolls, Box-Muller for luck factor. Supports 1d20, advantage/disadvantage, custom rolls, 4d6/8d6 stat rolls, d100 percentile. Critical hits flash. Stats panel: total rolls, nat 20s, nat 1s, crit rate, state hash."),
    ("tarot", "78-card tarot. 22 major + 56 minor arcana. Box-Muller decides reversal (Gaussian < -0.5 = reversed). Single/3/5/10-card spreads including Celtic Cross. Click 'Interpret' to see reading with positions."),
    ("zodiac", "Mathematical horoscope. Year/Month/Day → FNV-1a 64-bit hash → natal chart with Sun/Moon/Rising + 10 planets across 12 houses. Daily forecast button. Lucky number drawn deterministically."),
    ("piano", "2-octave keyboard (C4-B5). Click keys to play or use 'Play substrate melody' to auto-generate Box-Muller melodies. 4 scales (major/minor/pentatonic/dorian). Adjustable tempo + volume."),
    ("checkers", "8x8 checkers with kings + captures. Each piece has 16-d vector. Each square has 16-d vector. AI uses cosine-similarity eval to find best move. Click to move, 'AI move' button."),
    ("radio-fm", "Pirate radio. Box-Muller chords. Live spectrum analyzer. News breaks, sponsor ads, DJ banter. Click 'Start broadcast' to begin."),
    ("oracle", "Ask a question. Combines FNV-1a + xoshiro256** + Box-Muller + Bell state + cosine similarity into a 6-layer reading. Top concept identified via cosine."),
    ("journal", "Personal logbook. Each entry has a deterministic witness hash from FNV-1a. localStorage persistence. Mood tracking. Export/import as JSON."),
    ("life", "Conway's Game of Life on 80x80 grid. Click cells to toggle. 6 patterns (glider/blinker/toad/beacon/pulsar/Gosper gun). Auto-step. State hash per generation."),
    ("poetry", "Markov chain over Fleet Radio-flavored corpus. 1-6 stanzas, 2-8 lines per stanza, order 1-3. Each poem has a witness hash. Archive of generated poems."),
    ("wave-fn", "Single-qubit quantum circuit. Apply H/X/Y/Z/S/T/Rx/Ry/Rz gates. Measure to collapse. State vector display + trace check + history."),
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
    body = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": "You are a UX reviewer for the cellular-first design canon. Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 200,
        "temperature": 0.4,
    }
    if "extra" in cfg: body.update(cfg["extra"])
    req = urllib.request.Request(cfg["url"], data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            text = data["choices"][0]["message"]["content"].strip()
            # Try to extract JSON
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
