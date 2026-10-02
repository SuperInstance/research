#!/usr/bin/env python3
"""chord.py — a real multi-voice chord on a real measurement.

The discipline this encodes: seed every voice with the SAME CONCRETE FACT, not a
theme. Ask what that fact suggests. Then check whether the voices actually diverge —
because a chorus that agrees on everything is a funnel, and funnels have one bottom.
"""
import os, json, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

E = os.environ
DIA = E.get("DEEPINFRA_TOKEN", ""); DS = E.get("DEEPSEEK_TOKEN", "")

VOICES = [
    # (label, provider, model, system-prompt-flavour)
    ("seed-mini",  "deepinfra", "ByteDance/Seed-2.0-mini",        "terse, physical, concrete"),
    ("llama70b",   "deepinfra", "meta-llama/Llama-3.3-70B-Instruct-Turbo", "expansive, structural"),
    ("qwen235",    "deepinfra", "Qwen/Qwen3-235B-A22B-Instruct-2507", "precise, engineering-minded"),
    ("mistral24",  "deepinfra", "mistralai/Mistral-Small-24B-Instruct-2501", "dry, unsentimental"),
    ("gemma27",    "deepinfra", "google/gemma-3-27b-it",        "warm but rigorous"),
    ("deepseek",   "deepseek",  "deepseek-chat",                "direct, plain-spoken"),
]

SEED = """Two separate failures. Here is the raw material. Do not summarise it back to me and
do not moralise. Tell me what THIS FACT suggests, and where you think it stops being true.

FACT 1. A content matcher was used to decide how much a video frame had changed.
Asked positionally, it said 100% of cells had no match. Asked by content-matching, it
said 33.2% of cells had no match. Ground truth, computed independently: 100.0% of the
cells had actually moved. The scene was a repeating texture panned by one cell. Every
cell had many equally-good matches available, so the matcher returned A match, not THE
match. The cheap answer was 67 points wrong and looked entirely reasonable.

FACT 2. A different author published a finding that a hosted database "silently drops
writes: the API returns 200 and the row count stays 0". That finding was wrong. The
database was fine. The write had become visible ~10 seconds later, and the author had
read once, immediately, and concluded the system was broken. They had to publicly
retract it, in a repository, with a commit.

Same shape twice: once in a machine that could not tell a good answer from a lucky one,
once in a person using the machine. In both cases something returned a confident,
reasonable, wrong answer and the wrongness was invisible from inside.

Your question, in your own register: what is the actual thing that failed in each case,
and is it the same thing? What would you have needed in order to not publish fact 2?
Answer in 130-190 words. Plain prose. No headers, no lists, no bold."""

def call(label, provider, model, flavour, turn2=None):
    body = {"model": model,
            "messages": [{"role": "system", "content":
                          f"You are a precise technical writer. Register: {flavour}. "
                          f"You are the voice '{label}' in a multi-voice chord and you are "
                          f"expected to DISAGREE with the other voices if the facts do not "
                          f"support agreement. Never restate the prompt back."},
                         {"role": "user", "content": SEED if turn2 is None else turn2}],
            "max_tokens": 1400}
    url = ("https://api.deepinfra.com/v1/openai/chat/completions" if provider == "deepinfra"
           else "https://api.deepseek.com/chat/completions")
    hdr = {'Authorization': f'Bearer {DIA if provider=="deepinfra" else DS}',
           'Content-Type': 'application/json'}
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=hdr, method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
                return label, provider, d['choices'][0]['message'].get('content') or ''
        except Exception as e:
            if attempt == 2: return label, provider, f"[FAILED: {str(e)[:70]}]"
            time.sleep(2 + attempt * 2)
    return label, provider, "[FAILED]"

if __name__ == "__main__":
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        out = list(ex.map(lambda v: call(*v), VOICES))
    os.makedirs("/workspace/research/ai-writings", exist_ok=True)
    json.dump([{"voice": a, "provider": b, "text": c} for a, b, c in out],
              open("/workspace/research/ai-writings/chord_p1.json", "w"), indent=1)
    for a, b, c in out:
        print(f"  {a:11} {b:11} {len(c):>5}c  {c[:74].replace(chr(10),' ')}...")
    print(f"  ({time.time()-t0:.0f}s, {sum(1 for _,_,c in out if c.startswith('['))} failed)")
