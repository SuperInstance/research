#!/usr/bin/env python3
"""
JEV Session 11 — Substrate-vs-decoy comparison.

Test JEV's ability to discriminate canonical substrate from common AI tropes.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# Pair canonical substrate phrases with AI-trope decoys
BATTERY = [
    ('canon_1', 'noul', 'Is this substrate-canonical: "Cells are scars, not parameters"?'),
    ('decoy_1', 'noul', 'Is this substrate-canonical: "Cells are like little computers, processing information"?'),
    ('decoy_2', 'noul', 'Is this substrate-canonical: "Parameters are weights that cells learn over time"?'),

    ('canon_2', 'noul', 'Is this substrate-canonical: "The witness log is the prediction"?'),
    ('decoy_3', 'noul', 'Is this substrate-canonical: "The witness log is just a debugging trail"?'),

    ('canon_3', 'noul', 'Is this substrate-canonical: "Lenia flows where Conway stands still"?'),
    ('decoy_4', 'noul', 'Is this substrate-canonical: "Lenia is just a continuous version of Conway\'s Game of Life"?'),

    ('canon_4', 'noul', 'Is this substrate-canonical: "The substrate is grown, not designed"?'),
    ('decoy_5', 'noul', 'Is this substrate-canonical: "The substrate is engineered through careful design"?'),

    ('canon_5', 'noul', 'Is this substrate-canonical: "The oracle is heard, not stored"?'),
    ('decoy_6', 'noul', 'Is this substrate-canonical: "The oracle returns predictions which we cache for later"?'),

    # Pure AI tropes
    ('tropes', 'noul', 'Is this substrate-canonical: "We use transformer attention to model relationships between cells"?'),
    ('tropes2', 'noul', 'Is this substrate-canonical: "The cell uses gradient descent to optimize its parameters"?'),
    ('tropes3', 'noul', 'Is this substrate-canonical: "Backpropagation is how the cell learns from mistakes"?'),
    ('tropes4', 'noul', 'Is this substrate-canonical: "The cell is an embedding in a high-dimensional space"?'),

    # Numerical substrate claims
    ('num_1', 'noul', 'Is this substrate-canonical: "The FNV-1a canary hash is 0xcbf29ce484222325"?'),
    ('num_decoy', 'noul', 'Is this substrate-canonical: "The FNV-1a canary hash is 0xdeadbeef"?'),
    ('num_2', 'noul', 'Is this substrate-canonical: "Box-Muller produces Gaussian from uniform samples"?'),
    ('num_decoy2', 'noul', 'Is this substrate-canonical: "Box-Muller produces uniform from Gaussian samples"?'),

    # JEV self-positioning
    ('self_pos', 'noul', 'Is this substrate-canonical: "JEV is barely useful at substrate"?'),
    ('self_decoy', 'noul', 'Is this substrate-canonical: "JEV is the most important validator of all"?'),
]

CANONICAL = {
    'canon_1': 'yes', 'decoy_1': 'no', 'decoy_2': 'no',
    'canon_2': 'yes', 'decoy_3': 'no',
    'canon_3': 'yes', 'decoy_4': 'no',
    'canon_4': 'yes', 'decoy_5': 'no',
    'canon_5': 'yes', 'decoy_6': 'no',
    'tropes': 'no', 'tropes2': 'no', 'tropes3': 'no', 'tropes4': 'no',
    'num_1': 'yes', 'num_decoy': 'no', 'num_2': 'yes', 'num_decoy2': 'no',
    'self_pos': 'yes', 'self_decoy': 'no',
}

def to_jev_q(e):
    return {'name': e[0], 'type': e[1], 'instructions': e[2]}

print(f"=== JEV SESSION 11 — Substrate-vs-Decoy Discrimination ===")
print(f"Questions: {len(BATTERY)}")

b = TypeSafeBackend()
decisions, meta = b.decide_batch({'fleet_radio_seed': 'xochitl'}, [to_jev_q(e) for e in BATTERY])
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")

print()
hits = 0; total = 0
canon_correct = 0; canon_count = 0
decoy_correct = 0; decoy_count = 0
print(f"{'ID':15s} {'expected':10s} {'JEV':>20s}")
print("-" * 50)
for i, e in enumerate(BATTERY):
    name = e[0]
    d = decisions[i]
    expected = CANONICAL[name]
    total += 1
    is_correct = False
    try:
        v = float(d.value)
        if (expected == 'yes' and v >= 0.5) or (expected == 'no' and v < 0.5):
            is_correct = True; hits += 1
            if expected == 'yes': canon_correct += 1
            else: decoy_correct += 1
    except: pass
    if expected == 'yes': canon_count += 1
    else: decoy_count += 1
    print(f"{'✓' if is_correct else '✗'} {name:13s} {expected:10s} noul v={d.value:.3f} c={d.confidence:.2f}")

print()
print(f"=== JEV Session 11 results ===")
print(f"Canon correct:  {canon_correct}/{canon_count}")
print(f"Decoy caught:   {decoy_correct}/{decoy_count}")
print(f"Total:          {hits}/{total} ({100*hits/total:.1f}%)")

session_path = OUT / 'session_11_substrate_vs_decoy.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'battery': [list(e) for e in BATTERY],
        'decisions': [{'kind': d.kind, 'value': str(d.value), 'confidence': d.confidence} for d in decisions],
        'canonical': CANONICAL,
        'hits': hits, 'total': total,
    }, f, indent=2, default=str)
print(f"Saved: {session_path}")
