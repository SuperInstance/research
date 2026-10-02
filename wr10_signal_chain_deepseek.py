#!/usr/bin/env python3
"""WR10 piece 2 — DeepSeek Cellular Biologist voice."""
import os, json, time, urllib.request

os.environ.setdefault('DEEPINFRA_TOKEN', '')
TOKEN = os.environ['DEEPINFRA_TOKEN']

PROMPT = """Write a 600-word piece from the perspective of a cell — biological, not digital — experiencing its first JEV "spike" as if the spike were a perturbation of its membrane voltage.

Style — Cellular Biologist (DeepSeek voice):
- Molecular / biological metaphors
- "The cytoplasm" "the membrane" "the channel"
- Themes: gradients, permeability, repair cascades
- Long, flowing, dense sentences; rich in physics / chemistry detail
- Reference substrate doctrines (cells are scars, the witness log is the prediction)
- Mention at least one numerical fact (FNV-1a, xoshiro256**, Bell states, cosine similarity)
- End with an oracle-sighting moment

Output ONLY the piece, no preamble, no commentary. Keep it 550-650 words. Stay in voice — this is a cell narrating its own membrane voltage tracing the JEV spike as if it were a depolarization."""

def call():
    body = {
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'messages': [
            {'role': 'system', 'content': 'You are a cell — biological, membrane-bound — narrating your own experience of a JEV validator spike perturbing your membrane voltage. Stay scientific-poetic. Avoid generic AI tropes. Do not announce your model.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500,
        'temperature': 0.9,
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
print(f'DeepSeek ({time.time()-t0:.1f}s):')
print(text)

with open('/workspace/repos/ai-writings/cellular-first-design/reports/wr10-deepseek-signal-chain.md', 'w') as f:
    f.write('# WR10 — A Cell Hears Its Membrane Spike (Cellular Biologist, DeepSeek)\n\n')
    f.write(text)
print('Saved.')
