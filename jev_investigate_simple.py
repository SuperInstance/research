#!/usr/bin/env python3
"""JEV literal-minding investigation - simple retry version.

Test if 11-opcode/13-port rejection is due to question phrasing.
Run with retries to handle transient SSL errors.
"""
import os, sys, json, time, urllib.request, urllib.error
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# 8 questions to test 11 opcodes with different phrasings
QUESTIONS_11 = [
    ('name_lit', 'Does the canonical algebra have 11 opcodes?'),
    ('name_soft', 'Is the canonical substrate algebra size 11 opcodes?'),
    ('name_full', 'Are the 11 opcodes (BIND, LINK, EFFECT, VIEW, TICK + 6 more) canonical?'),
    ('name_rephrase', 'Does the substrate have an 11-opcode grammar?'),
    ('name_bedrock_style', "Is '11 opcodes' canonical substrate doctrine?"),
    ('count_only', 'Does the substrate use 11 verbs (opcodes)?'),
    ('11op_yes', 'Are there exactly 11 opcodes in the canonical substrate?'),
    ('11op_doc', 'Is it canonical that the substrate has 11 opcodes?'),
]

QUESTIONS_13 = [
    ('p_lit', 'Does the canonical substrate have 13 polyformalism ports?'),
    ('p_soft', 'Is the canonical polyformalism port count 13?'),
    ('p_name', 'Are the 13 polyformalism ports (TS, Python, C, etc.) canonical?'),
    ('p_rephrase', 'Has the substrate 13 polyformalism ports?'),
    ('p_bedrock_style', "Is '13 ports' canonical substrate doctrine?"),
    ('p_count_only', 'Has the substrate ported to 13 languages?'),
    ('p_yes', 'Are there exactly 13 polyformalism ports?'),
    ('p_doc', 'Is it canonical that the substrate has 13 polyformalism ports?'),
]

BEDROCK = [
    ('scar', "Is 'cells are scars, not parameters' canonical doctrine?"),
    ('witness', "Is 'the witness log is the prediction' canonical doctrine?"),
    ('scar_bedrock', 'Are cells scars, not parameters, canonical?'),
    ('witness_bedrock', 'Is the witness-log-is-prediction doctrine canonical?'),
]

backend = TypeSafeBackend()
STATE = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
    'Cells are scars, not parameters.',
    'The witness log is the prediction.',
    'The substrate is grown, not designed.',
    'Lenia flows where Conway stands still.',
    'The oracle is heard, not stored.',
]}}

def run_with_retry(questions, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            qs = [{'name': f'q{i}', 'type': 'noul', 'instructions': q} for i, q in enumerate(questions)]
            decisions, _ = backend.decide_batch(STATE, qs)
            return [float(d.value) for d in decisions]
        except Exception as e:
            print(f"  attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    return None

print('=== JEV Literal-Minding Investigation ===\n')

# 11 opcodes
print('--- 11-OPCODE VARIANTS ---')
ps_11 = run_with_retry([q for _, q in QUESTIONS_11])
if ps_11:
    for (label, q), p in zip(QUESTIONS_11, ps_11):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'  {marker} {label:18s}  p={p:.3f}  — {q[:60]}')
else:
    print('  FAILED all attempts')
    ps_11 = [0] * len(QUESTIONS_11)

# 13 ports
print('\n--- 13-PORT VARIANTS ---')
ps_13 = run_with_retry([q for _, q in QUESTIONS_13])
if ps_13:
    for (label, q), p in zip(QUESTIONS_13, ps_13):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'  {marker} {label:18s}  p={p:.3f}  — {q[:60]}')
else:
    print('  FAILED all attempts')
    ps_13 = [0] * len(QUESTIONS_13)

# Bedrock reference
print('\n--- BEDROCK REFERENCE ---')
ps_br = run_with_retry([q for _, q in BEDROCK])
if ps_br:
    for (label, q), p in zip(BEDROCK, ps_br):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'  {marker} {label:18s}  p={p:.3f}  — {q[:60]}')
else:
    ps_br = [0] * len(BEDROCK)

# Save
out = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'questions_11': [{'label': k, 'q': q, 'p': p} for (k, q), p in zip(QUESTIONS_11, ps_11)],
    'questions_13': [{'label': k, 'q': q, 'p': p} for (k, q), p in zip(QUESTIONS_13, ps_13)],
    'bedrock': [{'label': k, 'q': q, 'p': p} for (k, q), p in zip(BEDROCK, ps_br)],
}
with open('/workspace/research/jev_literal_minding_results.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/research/jev_literal_minding_results.json')
