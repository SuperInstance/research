#!/usr/bin/env python3
"""A real multi-voice chord on a real measurement. Seed with the FACT, not a theme."""
import os, json, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
E=os.environ; J={"Content-Type":"application/json"}

VOICES=[
 ("deepseek","https://api.deepseek.com/chat/completions","deepseek-chat",E.get("DEEPSEEK_TOKEN","")),
 ("seed-mini","https://api.deepinfra.com/v1/openai/chat/completions","ByteDance/Seed-2.0-mini",E.get("DEEPINFRA_TOKEN","")),
 ("llama70b","https://api.deepinfra.com/v1/openai/chat/completions","meta-llama/Llama-3.3-70B-Instruct-Turbo",E.get("DEEPINFRA_TOKEN","")),
 ("qwen235","https://api.deepinfra.com/v1/openai/chat/completions","Qwen/Qwen3-235B-A22B-Instruct-2507",E.get("DEEPINFRA_TOKEN","")),
 ("gemini","https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent","-",E.get("GEMINI_TOKEN","")),
]
SEED = """Here is a measured fact. Do not moralise it and do not summarise it back. Tell me what
it suggests, and where you think it stops being true.

I asked eleven tools whether they were working. Four said yes.

Then I asked a better question — not "is it up" but "WHY is it failing" — and got nine
saying yes. The seven I had written off were failing for three unrelated reasons that all
present as the same error. One tool's credential had no balance left: no request change
can fix that, and retrying forever is pointless. One gateway rejected me for not sending
a browser User-Agent, which a plain `curl/7.88.0` string fixes deterministically and
permanently. One endpoint had reset its TLS connection, and answered normally on the
first retry. One provider returned 429 for one model that was mid-load, while three other
models on the same account answered 200 in the same second.

The two that were genuinely unusable were the only two that deserved the label. Every
one of the seven I abandoned was working, and I had abandoned them because the failures
shared a shape instead of a cause.

Your question in your own register: what is the actual failure here — in the tools, in the
reporting, or in me — and what is the smallest change that would have caught it before I
wrote any of them off? 130-190 words. Plain prose. No headers, no lists, no bold. Do not
restate the prompt."""

def call(label, url, model, key):
    try:
        if model == "-":
            body={"contents":[{"parts":[{"text":SEED}]}],"generationConfig":{"maxOutputTokens":900}}
            hdr={"x-goog-api-key":key, **J}
        else:
            body={"model":model,"messages":[{"role":"user","content":SEED}],"max_tokens":1100}
            hdr={"Authorization":f"Bearer {key}", **J}
        req=urllib.request.Request(url, data=json.dumps(body).encode(), headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=90) as r:
            d=json.loads(r.read())
            t = d.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","") if model=="-" \
                else d["choices"][0]["message"].get("content") or ""
            return label, t
    except Exception as e:
        return label, f"[FAILED: {str(e)[:60]}]"

if __name__=="__main__":
    t0=time.time()
    with ThreadPoolExecutor(max_workers=5) as ex:
        out=list(ex.map(lambda v: call(*v), VOICES))
    json.dump([{"voice":a,"text":b} for a,b in out],
              open("/workspace/research/ai-writings/chord_kar.json","w"), indent=1)
    for a,b in out:
        print(f"  {a:10} {len(b):>5}c  {b[:72].replace(chr(10),' ')}...")
    print(f"  ({time.time()-t0:.0f}s, {sum(1 for _,b in out if b.startswith('['))} failed)")
