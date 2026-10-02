#!/usr/bin/env python3
"""JEV cross-validates the left-field answers from DeepSeek and ZAI."""
import os, json, sys, time
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# Load both
ds = json.load(open('/workspace/research/leftfield_deepseek.json'))
zai = json.load(open('/workspace/research/leftfield_zai.json'))

# Parse out answers
import re
def parse(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```', '', text)
    try:
        return json.loads(text)
    except:
        return []

ds_answers = parse(ds['response'])
zai_answers = parse(zai['response'])

print(f"DeepSeek: {len(ds_answers)} answers")
print(f"ZAI: {len(zai_answers)} answers")

# Build per-question prompts
backend = TypeSafeBackend()
state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': ['Cells are scars, not parameters.']}}

results = []
for q, d, z in zip(ds['questions'], ds_answers, zai_answers):
    questions = [
        {'name': 'is_ds_canonical', 'type': 'noul',
         'instructions': f"Is this Fleet Radio-canonical answer to '{q}'? Answer: {d['answer']}"},
        {'name': 'is_zai_canonical', 'type': 'noul',
         'instructions': f"Is this Fleet Radio-canonical answer to '{q}'? Answer: {z['answer']}"},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    ds_p = float(decisions[0].value)
    zai_p = float(decisions[1].value)
    print(f"Q: {q[:50]}...")
    print(f"  DS ({ds_p:.2f}): {d['answer'][:80]}")
    print(f"  ZAI ({zai_p:.2f}): {z['answer'][:80]}")
    results.append({'question': q, 'ds_answer': d['answer'], 'zai_answer': z['answer'],
                    'ds_canonical_p': ds_p, 'zai_canonical_p': zai_p})

# Save
with open('/workspace/research/leftfield_crossval.json', 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'results': results,
    }, f, indent=2, default=str)
print(f"\nSaved: /workspace/research/leftfield_crossval.json")
