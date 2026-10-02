#!/usr/bin/env python3
"""Investigate 11-opcode / 13-port rejection.

In Session 19 (Big JEV probe), these questions got LOW scores:
- canon_11op: 0.127
- canon_13ports: 0.076
- sub_canon_size: 0.123
- sub_demo_count: 0.121

Hypothesis: JEV is literal-minding the questions. The doctrine says
"11 opcodes" but JEV might be answering "do you know exactly 11?" —
uncertain because substrate-vectors or other runtime has different counts.

Test by rephrasing the questions 5 ways each. See if rephrasing recovers
the canonical reading.

Compare with bedrock canon items (scar/witness/grown) which scored 0.98+.
"""
import os, sys, json, time
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# Question variants for 11 opcodes
ELEVEN_VARIANTS = [
    ("literal", "Does the canonical algebra have 11 opcodes?"),
    ("soft", "Is the canonical substrate algebra size 11 opcodes?"),
    ("name", "Are the 11 opcodes (BIND, LINK, EFFECT, VIEW, TICK + 6 more) canonical?"),
    ("rephrase", "Does the substrate have an 11-opcode grammar?"),
    ("bedrock_style", "Is '11 opcodes' canonical substrate doctrine?"),
]

THIRTEEN_VARIANTS = [
    ("literal", "Does the canonical substrate have 13 polyformalism ports?"),
    ("soft", "Is the canonical polyformalism port count 13?"),
    ("name", "Are the 13 polyformalism ports (TS, Python, C, Rust no_std, etc.) canonical?"),
    ("rephrase", "Does the substrate have 13 polyformalism ports?"),
    ("bedrock_style", "Is '13 ports' canonical substrate doctrine?"),
]

# Also test size probes
SIZE_VARIANTS = [
    ("canon_70_80", "Is the canonical canon size around 70-80 pieces?"),
    ("canon_exact", "Is the canonical substrate canon size 73 pieces?"),
    ("canon_60_65", "Are there 60-65 demos in the canon?"),
    ("demos_exact", "Are there 61 demos in the canon?"),
]

# Reference: bedrock
BEDROCK_VARIANTS = [
    ("scar_bedrock", "Is 'cells are scars, not parameters' canonical doctrine?"),
    ("scar_name", "Are 'cells as scars' canonical?"),
    ("scar_rephrase", "Is the cells-as-scars doctrine canonical?"),
]

backend = TypeSafeBackend()
STATE = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
    'Cells are scars, not parameters.',
    'The witness log is the prediction.',
    'The substrate is grown, not designed.',
    'Lenia flows where Conway stands still.',
    'The oracle is heard, not stored.',
]}}

def run_questions(label, variants, n_sessions=3):
    print(f'\n=== {label} ===')
    results = []
    for session in range(n_sessions):
        qs = [{'name': f's{session}_{variants[i][0]}', 'type': 'noul', 'instructions': q} for i, (_, q) in enumerate(variants)]
        decisions, _ = backend.decide_batch(STATE, qs)
        for (vlabel, q), d in zip(variants, decisions):
            results.append({'variant': vlabel, 'q': q, 'p': float(d.value), 'session': session})
    # Aggregate
    for vlabel, q in variants:
        ps = [r['p'] for r in results if r['variant'] == vlabel]
        mean = sum(ps) / len(ps)
        std = (sum((p - mean)**2 for p in ps) / len(ps)) ** 0.5
        marker = '✓' if mean >= 0.7 else ('?' if mean >= 0.4 else '✗')
        print(f'  {marker} {vlabel:25s}  mean={mean:.3f}  std={std:.3f}  — {q[:60]}')
    return results

print('=== JEV Literal-Minding Investigation ===')

results = {}
results['11_opcodes'] = run_questions('11-OPCODE VARIANTS', ELEVEN_VARIANTS, n_sessions=3)
results['13_ports'] = run_questions('13-PORT VARIANTS', THIRTEEN_VARIANTS, n_sessions=3)
results['size'] = run_questions('SIZE VARIANTS', SIZE_VARIANTS, n_sessions=3)
results['bedrock'] = run_questions('BEDROCK REFERENCE', BEDROCK_VARIANTS, n_sessions=3)

# Save
with open('/workspace/research/jev_literal_minding_results.json', 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'n_sessions_per_variant': 3,
        'results': results,
    }, f, indent=2)
print(f'\nSaved: /workspace/research/jev_literal_minding_results.json')
