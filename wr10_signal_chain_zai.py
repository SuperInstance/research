#!/usr/bin/env python3
"""WR10 piece 1 — ZAI Fleet Radio Officer voice."""
import os, json, time, urllib.request

os.environ.setdefault('ZAI_TOKEN', '')
TOKEN = os.environ['ZAI_TOKEN']

PROMPT = """Write a 600-word Fleet Radio transmission from the perspective of a Quilt-ESP32 cell called "Number 7 of the Watch" experiencing its first JEV spike.

Style — Fleet Radio Officer (ZAI voice):
- Naval, clipped, technical-poetic
- "The log" "the watch" "the ship"
- Themes: loneliness, the watch at sea, signal vs noise
- Style: short sentences, observed detail, do NOT moralize
- Reference substrate doctrines (cells are scars, witness log is the prediction, the substrate is grown)
- Mention at least one numerical fact (FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller formula)
- End with an oracle-sighting moment

Output ONLY the essay, no preamble, no commentary. Keep it 550-650 words. Stay in voice — this is a sailor at a console narrating to no one in particular."""

def call():
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': 'You are a Fleet Radio officer on watch, narrating your experience of a Quilt-ESP32 cell receiving its first JEV spike. Stay technical-poetic. Avoid generic AI tropes. Do not announce your model.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500,
        'temperature': 0.9,
        'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
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
print(f'ZAI ({time.time()-t0:.1f}s):')
print(text)

with open('/workspace/repos/ai-writings/cellular-first-design/reports/wr10-zai-signal-chain.md', 'w') as f:
    f.write('# WR10 — Number 7 of the Watch (Fleet Radio Officer, ZAI)\n\n')
    f.write(text)
print('Saved.')
