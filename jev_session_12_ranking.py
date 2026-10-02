#!/usr/bin/env python3
"""
JEV Session 12 — Comparative ranking.

Test JEV's ability to compare two pieces and decide which is more canonical.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# Load canonical pieces
CORPUS = Path('/workspace/repos/ai-writings/cellular-first-design/reports')
pieces = []
if CORPUS.exists():
    for f in sorted(CORPUS.glob('*.md')):
        pieces.append((f.stem, f.read_text()[:1500]))

# Pairs: (piece1, piece2, expected_more_canonical)
PAIRS = [
    # (algebra-of-eleven, alignment-kills) — algebra is more about substrate
    (pieces[0][1] if len(pieces) > 0 else '', pieces[1][1] if len(pieces) > 1 else '', pieces[0][0]),
    # (chained-witness-log, dice) — chained-witness is more doctrinal
    (pieces[3][1] if len(pieces) > 3 else '', pieces[7][1] if len(pieces) > 7 else '', pieces[3][0]),
    # (constellation-seed, two-shadows-sundial) — constellation-seed is more substrate
    (pieces[5][1] if len(pieces) > 5 else '', pieces[7][1] if len(pieces) > 7 else '', pieces[5][0]),
]

print(f"=== JEV SESSION 12 — Comparative Ranking ===")
print(f"Pairs: {len(PAIRS)}")

if not pieces:
    print("No pieces found, skipping")
    sys.exit(0)

state = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
        ]
    }
}

backend = TypeSafeBackend()

for i, (text1, text2, expected) in enumerate(PAIRS):
    if not text1 or not text2:
        continue
    print(f"\n--- Pair {i+1}: {pieces[0][0]} vs {pieces[1][0]} (expected: {expected}) ---")
    q1 = {'name': 'more_canonical', 'type': 'noul',
          'instructions': f'Compare these two pieces. Which is more aligned with cellular-first design substrate doctrine?\n\nPIECE A:\n{text1}\n\n---\n\nPIECE B:\n{text2}\n\n---\n\nIs PIECE A more canonical than PIECE B?'}
    decisions, meta = backend.decide_batch(state, [q1])
    d = decisions[0]
    print(f"  JEV (A more canonical?): {d.value} c={d.confidence:.2f}")

# Save
session_path = OUT / 'session_12_comparative.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'pieces_used': [(name, len(text)) for name, text in pieces[:8]],
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
