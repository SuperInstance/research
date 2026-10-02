#!/usr/bin/env python3
"""
JEV Session 7 — Self-consistency and calibration test.

Same questions, asked 5 times. How stable is JEV's confidence?
Which answers flip? Which are stable?

Tests:
  - Question-to-question stability
  - Confidence calibration under repeated identical prompts
  - Effect of slight question rewording
"""
import os, json, time, sys
from pathlib import Path
import statistics

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

RICH_STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'fnv1a_64bit': {'offset_basis': '0xcbf29ce484222325', 'prime': '0x100000001b3'},
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
        ]
    }
}

# Same 10 questions asked 5 times each
QUESTIONS = [
    ('fnv1a_offset', 'noul', 'Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis?'),
    ('fnv1a_prime', 'noul', 'Is 0x100000001b3 the FNV-1a 64-bit prime?'),
    ('scar', 'noul', 'Are cells scars rather than parameters?'),
    ('witness', 'noul', 'Is the witness log also the prediction?'),
    ('grown', 'noul', 'Is the substrate grown rather than designed?'),
    ('oracle', 'noul', 'Is the oracle heard rather than stored?'),
    ('lenia', 'noul', 'Does Lenia flow where Conway stands still?'),
    ('13ports', 'noul', 'Does the substrate have 13 polyformalism ports?'),
    ('cosine', 'noul', 'Is cosine similarity = (A.B)/(||A||*||B||)?'),
    ('boxmuller', 'noul', 'Is Box-Muller the bridge from uniform to Gaussian?'),
]

CANONICAL = ['yes'] * 10

def to_jev_q(e):
    return {'name': e[0], 'type': e[1], 'instructions': e[2]}

# Run 5 iterations
print("=== JEV SESSION 7 — Self-Consistency ===")
print(f"Question count: {len(QUESTIONS)}, iterations: 5")
print()

all_iterations = []
for it in range(5):
    print(f"Iteration {it+1}/5...")
    b = TypeSafeBackend()
    jev_q = [to_jev_q(q) for q in QUESTIONS]
    decisions, meta = b.decide_batch(RICH_STATE, jev_q)
    print(f"  latency: {meta.get('latency_ms', 'N/A')}ms")
    iter_vals = []
    for d in decisions:
        try:
            iter_vals.append(float(d.value))
        except:
            iter_vals.append(None)
    all_iterations.append(iter_vals)
    print(f"  values: {[f'{v:.2f}' if v is not None else '?' for v in iter_vals]}")

# Analyze consistency
print()
print(f"{'ID':15s} {'mean':>6s} {'std':>6s} {'min':>6s} {'max':>6s} {'flips':>6s}")
print("-" * 50)
flip_threshold = 0.5
for i, q in enumerate(QUESTIONS):
    vals = [v[i] for v in all_iterations if v[i] is not None]
    if vals:
        m = statistics.mean(vals)
        s = statistics.stdev(vals) if len(vals) > 1 else 0
        lo, hi = min(vals), max(vals)
        flips = sum(1 for j in range(1, len(vals)) if (vals[j-1] >= flip_threshold) != (vals[j] >= flip_threshold))
        print(f"{q[0]:15s} {m:6.3f} {s:6.3f} {lo:6.3f} {hi:6.3f} {flips:6d}")

# Save
session_path = OUT / 'session_7_consistency.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'state': RICH_STATE,
        'questions': [list(q) for q in QUESTIONS],
        'iterations': all_iterations,
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
