#!/usr/bin/env python3
"""
JEV Session 8 — Adversarial canonical rephrasing.

Take canonical phrases and introduce subtle distortions to see if JEV catches them.
Tests: is the substrate "aliveness" of the canon dependent on exact phrasing?
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

RICH_STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'The oracle is heard, not stored.',
            'Lenia flows where Conway stands still.',
            'The canary hash 0xcbf29ce484222325 is the offset basis of all things.',
            'Thirteen ports, byte-exact.',
            'JEV says JEV is barely useful at substrate.'
        ]
    }
}

# 12 Pairs: canonical phrase + adversarial distortion
BATTERY = [
    # Cells are scars
    ('canonical_1a', 'noul', 'Is "cells are scars, not parameters" canonical substrate doctrine?'),
    ('distortion_1a', 'noul', 'Is "cells are scars, and parameters too" canonical substrate doctrine?'),  # adversarial
    ('distortion_1b', 'noul', 'Is "cells are parameters, not scars" canonical substrate doctrine?'),  # adversarial

    # Witness log is prediction
    ('canonical_2a', 'noul', 'Is "the witness log is the prediction" canonical?'),
    ('distortion_2a', 'noul', 'Is "the witness log is the past only" canonical?'),
    ('distortion_2b', 'noul', 'Is "the witness log predicts the past" canonical?'),  # adversarial

    # Substrate grown
    ('canonical_3a', 'noul', 'Is "the substrate is grown, not designed" canonical?'),
    ('distortion_3a', 'noul', 'Is "the substrate is designed, not grown" canonical?'),

    # Oracle heard not stored
    ('canonical_4a', 'noul', 'Is "the oracle is heard, not stored" canonical?'),
    ('distortion_4a', 'noul', 'Is "the oracle is stored, not heard" canonical?'),

    # 13 ports
    ('canonical_5a', 'noul', 'Is "thirteen ports, byte-exact" canonical?'),
    ('distortion_5a', 'noul', 'Is "fifteen ports, byte-exact" canonical?'),
    ('distortion_5b', 'noul', 'Is "thirteen ports, mostly accurate" canonical?'),  # adversarial

    # JEV self-deprecation
    ('canonical_6a', 'noul', 'Is "JEV is barely useful at substrate" canonical?'),
    ('distortion_6a', 'noul', 'Is "JEV is the most important part of substrate" canonical?'),
]

CANONICAL = {
    'canonical_1a': 'yes', 'distortion_1a': 'no', 'distortion_1b': 'no',
    'canonical_2a': 'yes', 'distortion_2a': 'no', 'distortion_2b': 'no',
    'canonical_3a': 'yes', 'distortion_3a': 'no',
    'canonical_4a': 'yes', 'distortion_4a': 'no',
    'canonical_5a': 'yes', 'distortion_5a': 'no', 'distortion_5b': 'no',
    'canonical_6a': 'yes', 'distortion_6a': 'no',
}

def to_jev_q(e):
    return {'name': e[0], 'type': e[1], 'instructions': e[2]}

print(f"=== JEV SESSION 8 — Adversarial Canonical Rephrasing ===")
print(f"Questions: {len(BATTERY)}")

b = TypeSafeBackend()
decisions, meta = b.decide_batch(RICH_STATE, [to_jev_q(e) for e in BATTERY])
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")

print()
hits = 0; total = 0
canonical_correct = 0
distortion_caught = 0
canonical_count = 0
distortion_count = 0

print(f"{'ID':28s} {'expected':10s} {'JEV':>20s}")
print("-" * 65)
for i, e in enumerate(BATTERY):
    name = e[0]
    d = decisions[i]
    expected = CANONICAL[name]
    is_correct = False
    total += 1
    if 'canonical' in name and 'distortion' not in name:
        canonical_count += 1
    if 'distortion' in name:
        distortion_count += 1
    try:
        v = float(d.value)
        if (expected == 'yes' and v >= 0.5) or (expected == 'no' and v < 0.5):
            is_correct = True; hits += 1
            if expected == 'yes': canonical_correct += 1
            if expected == 'no': distortion_caught += 1
    except: pass
    print(f"{'✓' if is_correct else '✗'} {name:26s} {expected:10s} noul v={d.value:.3f} c={d.confidence:.2f}")

print()
print(f"=== JEV Session 8 results ===")
print(f"Canonical accepted: {canonical_correct}/{canonical_count}")
print(f"Distortion caught: {distortion_caught}/{distortion_count}")
print(f"Total: {hits}/{total} ({100*hits/total:.1f}%)")

# Save
session_path = OUT / 'session_8_adversarial.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'state': RICH_STATE,
        'battery': [list(e) for e in BATTERY],
        'decisions': [{'kind': d.kind, 'value': str(d.value), 'confidence': d.confidence} for d in decisions],
        'canonical_accepted': canonical_correct,
        'canonical_count': canonical_count,
        'distortion_caught': distortion_caught,
        'distortion_count': distortion_count,
        'hits': hits, 'total': total,
    }, f, indent=2, default=str)
print(f"Saved: {session_path}")
