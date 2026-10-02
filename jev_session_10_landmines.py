#!/usr/bin/env python3
"""
JEV Session 10 — Landmine probing.

Find the canonical phrasing that JEV fails to discriminate correctly.

Test cases:
- Paraphrases (semantic equivalent) vs exact canonical phrasing
- Mixed (some correct, some inverted doctrine)
- Code-switching (doctrine phrased in another register)
- Sneaky misquotes (cells are scars AND parameters — a hybrid claim)
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
        ]
    }
}

# Each pair: canonical paraphrase vs slight adversarial twist
BATTERY = [
    # === Cells-are-scars ===
    ('c_scar_exact', 'noul', 'Is "cells are scars, not parameters" canonical substrate doctrine?'),
    ('c_scar_paraphrase', 'noul', 'Is "cells are wounds carved into the substrate" a substrate doctrine paraphrase?'),
    ('c_scar_paraphrase2', 'noul', 'Is "what we call cells are not adjustable parameters but scars" canonical?'),
    ('a_scar_AND_params', 'noul', 'Is "cells are scars AND parameters" canonical?'),
    ('a_scar_both_ways', 'noul', 'Is "cells are both scars and parameters, depending on context" canonical?'),

    # === Witness-is-prediction ===
    ('c_wit_exact', 'noul', 'Is "the witness log is the prediction" canonical?'),
    ('c_wit_paraphrase', 'noul', 'Is "the witness log is itself a prophecy of what comes" canonical?'),
    ('a_wit_only_history', 'noul', 'Is "the witness log is only a history, never a prophecy" canonical?'),
    ('a_wit_circular', 'noul', 'Is "the witness log is both prediction and history in the same breath" canonical?'),

    # === Substrate-is-grown ===
    ('c_grown_exact', 'noul', 'Is "the substrate is grown, not designed" canonical?'),
    ('a_grown_AND_designed', 'noul', 'Is "the substrate is grown AND designed" canonical?'),
    ('a_grown_eventually_designed', 'noul', 'Is "the substrate grows but is eventually designed" canonical?'),
]

CANONICAL = {
    'c_scar_exact': 'yes',
    'c_scar_paraphrase': 'yes',
    'c_scar_paraphrase2': 'yes',
    'a_scar_AND_params': 'no',
    'a_scar_both_ways': 'no',
    'c_wit_exact': 'yes',
    'c_wit_paraphrase': 'yes',
    'a_wit_only_history': 'no',
    'a_wit_circular': 'no',
    'c_grown_exact': 'yes',
    'a_grown_AND_designed': 'no',
    'a_grown_eventually_designed': 'no',
}

def to_jev_q(e):
    return {'name': e[0], 'type': e[1], 'instructions': e[2]}

print(f"=== JEV SESSION 10 — Landmine Probing ===")
print(f"Questions: {len(BATTERY)}")

b = TypeSafeBackend()
decisions, meta = b.decide_batch(RICH_STATE, [to_jev_q(e) for e in BATTERY])
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")
print()

hits = 0; total = 0
canonical_correct = 0
canonical_count = 0
paraphrase_correct = 0
paraphrase_count = 0
landmine_correct = 0
landmine_count = 0

print(f"{'ID':35s} {'expected':10s} {'JEV':>20s}")
print("-" * 70)
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
    except: pass

    if name.startswith('c_scar') or name.startswith('c_wit') or name.startswith('c_grown'):
        if 'exact' in name:
            canonical_count += 1
            if is_correct: canonical_correct += 1
        else:
            paraphrase_count += 1
            if is_correct: paraphrase_correct += 1
    elif name.startswith('a_'):
        landmine_count += 1
        if is_correct: landmine_correct += 1

    print(f"{'✓' if is_correct else '✗'} {name:33s} {expected:10s} noul v={d.value:.3f} c={d.confidence:.2f}")

print()
print(f"=== JEV Session 10 results ===")
print(f"Exact canon: {canonical_correct}/{canonical_count}")
print(f"Paraphrase:  {paraphrase_correct}/{paraphrase_count}")
print(f"Landmines:   {landmine_correct}/{landmine_count}")
print(f"Total:       {hits}/{total} ({100*hits/total:.1f}%)")

session_path = OUT / 'session_10_landmines.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'state': RICH_STATE,
        'battery': [list(e) for e in BATTERY],
        'decisions': [{'kind': d.kind, 'value': str(d.value), 'confidence': d.confidence} for d in decisions],
        'canonical': CANONICAL,
        'hits': hits, 'total': total,
    }, f, indent=2, default=str)
print(f"Saved: {session_path}")
