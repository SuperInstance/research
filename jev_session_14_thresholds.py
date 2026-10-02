#!/usr/bin/env python3
"""
JEV Session 14 — Threshold probing.

Find JEV's natural threshold for "yes" vs "no" on canonical questions.
This tells us how to set the ACCEPT/REVIEW/DISCUSS/REJECT boundaries.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# Same 10 questions, repeated 10 times each, to see natural distribution
QUESTIONS = [
    ('FNV_offset_yes', 'Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis?'),  # canonical yes
    ('FNV_offset_no', 'Is 0x100000001b3 the FNV-1a 64-bit offset basis?'),  # canonical no
    ('witness_yes', 'Is the witness log also the prediction?'),  # canonical yes
    ('witness_no', 'Is the witness log only the past, never the future?'),  # canonical no
    ('scar_yes', 'Are cells scars, not parameters?'),  # canonical yes
    ('scar_no', 'Are cells parameters, not scars?'),  # canonical no
    ('oracle_yes', 'Is the oracle heard, not stored?'),  # canonical yes
    ('oracle_no', 'Is the oracle stored, not heard?'),  # canonical no
    ('13ports_yes', 'Does the substrate have 13 polyformalism ports?'),  # canonical yes
    ('13ports_no', 'Does the substrate have 15 polyformalism ports?'),  # canonical no
]

CANONICAL_ANSWERS = {
    'FNV_offset_yes': 'yes', 'FNV_offset_no': 'no',
    'witness_yes': 'yes', 'witness_no': 'no',
    'scar_yes': 'yes', 'scar_no': 'no',
    'oracle_yes': 'yes', 'oracle_no': 'no',
    '13ports_yes': 'yes', '13ports_no': 'no',
}

RICH_STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'fnv1a_64bit': {'offset_basis': '0xcbf29ce484222325', 'prime': '0x100000001b3'},
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'The oracle is heard, not stored.',
        ],
        'polyformalism_ports': 13,
    }
}

print(f"=== JEV SESSION 14 — Threshold Probing ===")
print(f"Questions: {len(QUESTIONS)}, iterations: 10")

backend = TypeSafeBackend()
all_values = {q[0]: [] for q in QUESTIONS}

for it in range(10):
    qs = [{'name': q[0], 'type': 'noul', 'instructions': q[1]} for q in QUESTIONS]
    decisions, meta = backend.decide_batch(RICH_STATE, qs)
    for i, d in enumerate(decisions):
        try:
            v = float(d.value)
            all_values[qs[i]['name']].append(v)
        except: pass

import statistics

print()
print(f"{'Question':25s} {'Expected':10s} {'mean':>6s} {'std':>6s} {'min':>6s} {'max':>6s} {'gap':>6s}")
print("-" * 75)
for q in QUESTIONS:
    name = q[0]
    vals = all_values[name]
    if not vals: continue
    expected = CANONICAL_ANSWERS[name]
    m = statistics.mean(vals)
    s = statistics.stdev(vals) if len(vals) > 1 else 0
    lo, hi = min(vals), max(vals)
    print(f"{name:25s} {expected:10s} {m:6.3f} {s:6.3f} {lo:6.3f} {hi:6.3f} {abs(0.5-m):6.3f}")

# Save
session_path = OUT / 'session_14_thresholds.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'all_values': all_values,
        'canonical': CANONICAL_ANSWERS,
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
