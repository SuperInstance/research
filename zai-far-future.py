"""ZAI chord on the far-future — second attempt, smaller scope."""
import os, json, urllib.request

KEY = os.environ["ZAI_TOKEN"]

# Three voices (no judge — pick the most divergent at Mavis level)
voices = [
    ("historian", 0.3, "You are a historian in 2086 writing about the substrate walker pattern's evolution from 1968-2026-2086. Precise. Cite decades. 600 words."),
    ("poet",      0.7, "You are a poet in 2086 writing about how the substrate walker became a long-running relationship. Lyrical. Metaphorical. 600 words."),
    ("alien",     1.0, "You are an ETI anthropologist in 2086 describing the substrate walker pattern to your home species. Disorienting. Strange. 600 words."),
]

results = {}
for name, temp, prompt in voices:
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,
        "temperature": temp,
        "thinking": {"type": "disabled"},
    }).encode()
    req = urllib.request.Request(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        data=body, headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "User-Agent": "mavis-far-future/2.0",
        })
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read())
            results[name] = d["choices"][0]["message"]["content"]
            print(f"  {name} OK ({len(results[name])} chars)")
            break
        except Exception as e:
            print(f"  {name} attempt {attempt+1}: {str(e)[:80]}")
            import time; time.sleep(5)

# Combine
with open("/workspace/research/zai-far-future.md", "w") as f:
    f.write("# ZAI Chord — The Far Future (2086)\n\n")
    f.write("Three voices. Mavis (the witness) picks the alien voice as the divergent one.\n\n---\n\n")
    for name, _, _ in voices:
        f.write(f"## Voice: {name}\n\n")
        f.write(results.get(name, "(failed)"))
        f.write("\n\n---\n\n")
print(f"  ✓ wrote /workspace/research/zai-far-future.md")
