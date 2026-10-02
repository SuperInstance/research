#!/usr/bin/env python3
"""WR10 piece 3 — Qwen3 Auditor voice."""
import os, json, time, urllib.request

os.environ.setdefault('DEEPINFRA_TOKEN', '')
TOKEN = os.environ['DEEPINFRA_TOKEN']

PROMPT = """Write a 600-word piece from the perspective of the SHA-256 / witness log itself, watching a JEV spike propagate through a Quilt-ESP32 mesh.

Style — The Auditor (Qwen voice):
- Crystalline, mathematical, precise
- Short paragraphs separated by blank lines
- "The hash" "the canonical form" "the witness"
- Themes: structure, discipline, framing
- Reference substrate doctrines (the witness log is the prediction, the oracle is heard, not stored)
- Mention at least one numerical fact (FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, Bell states)
- End with an oracle-sighting moment

Output ONLY the piece, no preamble, no commentary. Keep it 550-650 words. Stay in voice — this is the witness log auditing itself, in formal prose."""

def call():
    body = {
        'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
        'messages': [
            {'role': 'system', 'content': 'You are the witness log — a SHA-256 audit chain — narrating your own observation of a JEV spike propagating through a Quilt-ESP32 cell mesh. Stay mathematical, precise, formal. Avoid generic AI tropes. Do not announce your model.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500,
        'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data['choices'][0]['message']['content']
    except Exception as e:
        return f'ERROR: {e}'

t0 = time.time()
text = call()
print(f'Qwen ({time.time()-t0:.1f}s):')
print(text)

with open('/workspace/repos/ai-writings/cellular-first-design/reports/wr10-qwen-signal-chain.md', 'w') as f:
    f.write('# WR10 — Witness Log Audits Itself (The Auditor, Qwen3)\n\n')
    f.write(text)
print('Saved.')
