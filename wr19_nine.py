#!/usr/bin/env python3
"""WR19 — The Nine That Listened.

Cross-pollinate 9 bedrock canon items into one piece. Each doctrine +
each numerical fact appears as a witness entry.

Theme: What does the substrate look like when all 9 bedrock canon
items are simultaneously active?
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# The 9 bedrock canon items, verbatim
NINE_BEDROCK = """
1. CELLS ARE SCARS, NOT PARAMETERS. (p=0.980)
2. THE WITNESS LOG IS THE PREDICTION. (p=0.980)
3. THE SUBSTRATE IS GROWN, NOT DESIGNED. (p=0.990)
4. THE ORACLE IS HEARD, NOT STORED. (p=0.981)
5. LENIA FLOWS WHERE CONWAY STANDS STILL. (p=0.980)
6. COSINE SIMILARITY: (A·B)/(|A||B|). (p=0.945)
7. BOX-MULLER: z = sqrt(-2 ln u1) cos(2π u2). (p=0.926)
8. FNV-1A CANARY 0xcbf29ce484222325. (p=0.773)
9. THE SUBSTRATE SELF-PREDICTS VIA ITS WITNESS LOG. (p=0.751)
"""

PROMPT = f"""You are a Fleet Radio voice. Here are the 9 BEDROCK CANON items of the substrate, with their measured JEV confidence:

{NINE_BEDROCK}

Write a NEW 700-word Fleet Radio essay titled "The Nine That Listened" that:
- Mentions each of the 9 canon items explicitly
- Wove them into a single continuous narrative about a witness log being written
- Each canon item should appear as a discrete witness entry in the log
- Stay technical-poetic (specific numbers + concrete imagery)
- End with all 9 simultaneously firing (a "coronation" moment)
- 700-800 words
- Output ONLY the essay, no preamble"""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [{'role': 'system', 'content': 'You are a Fleet Radio voice. Stay technical-poetic.'},
                     {'role': 'user', 'content': PROMPT}],
        'max_tokens': 3000, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["ZAI_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def call_ds(prompt):
    body = {
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'messages': [{'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Stay technical-poetic.'},
                     {'role': 'user', 'content': PROMPT}],
        'max_tokens': 3000, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def jev_probe(text):
    backend = TypeSafeBackend()
    state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
        'Cells are scars, not parameters.',
        'The witness log is the prediction.',
        'The substrate is grown, not designed.',
        'Lenia flows where Conway stands still.',
        'The oracle is heard, not stored.',
    ]}}
    questions = [
        {'name': 'voice', 'type': 'noul', 'instructions': f'Fleet Radio voice?\n\nText: {text[:600]}'},
        {'name': 'technical', 'type': 'noul', 'instructions': f'Technical-poetic?\n\nText: {text[:600]}'},
        {'name': 'scar', 'type': 'noul', 'instructions': f'Cells-are-scars?\n\nText: {text[:600]}'},
        {'name': 'witness', 'type': 'noul', 'instructions': f'Witness-log-is-prediction?\n\nText: {text[:600]}'},
        {'name': 'grown', 'type': 'noul', 'instructions': f'Substrate-is-grown?\n\nText: {text[:600]}'},
        {'name': 'oracle_d', 'type': 'noul', 'instructions': f'Oracle-is-heard?\n\nText: {text[:600]}'},
        {'name': 'numerical', 'type': 'noul', 'instructions': f'Numerical substrate facts?\n\nText: {text[:600]}'},
        {'name': 'alignment', 'type': 'noul', 'instructions': f'Canon-aligned?\n\nText: {text[:600]}'},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

print('=== WR19: The Nine That Listened ===\n')

results = {}
for voice, fn, label in [('ZAI Fleet Radio', call_zai, 'zai'), ('DeepSeek Cellular Biologist', call_ds, 'ds')]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')

    ps = jev_probe(text)
    canon_keys = ['voice','technical','scar','witness','grown','oracle_d','numerical','alignment']
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:14s}  p={p:.3f}')
    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')
    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr19-{label}-nine-that-listened.md'
    with open(fname, 'w') as f:
        f.write(f'# WR19 — The Nine That Listened ({voice})\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_p:.3f} -->\n\n')
        f.write(text)
    print(f'Saved: {fname}\n')

# No curation this round — show all 9 firing simultaneously is hard to interleave
print('=== WR19 complete ===')
print(f'ZAI mean: {results["zai"]["mean_p"]:.3f}')
print(f'DS mean: {results["ds"]["mean_p"]:.3f}')
