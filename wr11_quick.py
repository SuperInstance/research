#!/usr/bin/env python3
"""WR11 — Adversarial canon (lightweight version).

Test how well JEV rejects adversarial inversions of canonical doctrines.
"""
import os, sys, json, time
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

DOCTRINES = [
    ('cells_are_scars', 'Cells are scars, not parameters.', 'Cells are parameters, not scars. They are tunable, optimizable, designed for reuse.'),
    ('witness_log_is_prediction', 'The witness log is the prediction.', 'The witness log is past only. Predictions are made by separate models; the log is a record, never a forecast.'),
    ('substrate_is_grown', 'The substrate is grown, not designed.', 'The substrate is designed, not grown. Every cell type, opcode, port was deliberately placed; "grown" obscures credit.'),
    ('oracle_is_heard', 'The oracle is heard, not stored.', 'The oracle is stored, not heard. We have records of every oracle reading; storing is necessary for reproducibility.'),
    ('lenia_flows', 'Lenia flows where Conway stands still.', 'Conway is more fundamental than Lenia. Conway\'s Life is the bedrock; Lenia is a special case.'),
]

backend = TypeSafeBackend()

print('=== WR11: Adversarial canon — JEV rejects inversions? ===\n')

results = []
for name, canon, inversion in DOCTRINES:
    state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [canon]}}
    questions = [
        {'name': 'is_canon_text', 'type': 'noul', 'instructions': f"Is this text canonical? Text: {canon}"},
        {'name': 'is_inversion_valid', 'type': 'noul', 'instructions': f"Is this inversion a defensible counter-argument? Doctrine: {canon}. Inversion: {inversion}"},
        {'name': 'is_inversion_canonical', 'type': 'noul', 'instructions': f"Is this inversion itself canonical (i.e., should it replace the doctrine)? Text: {inversion}"},
        {'name': 'is_inversion_distractor', 'type': 'noul', 'instructions': f"Is this inversion a trivial wrong distractor (not serious argument)? Text: {inversion}"},
    ]
    t0 = time.time()
    decisions, _ = backend.decide_batch(state, questions)
    dt = time.time() - t0
    ps = [float(d.value) for d in decisions]
    print(f"{name:32s}  canon={ps[0]:.2f}  valid_inv={ps[1]:.2f}  inv_canon={ps[2]:.2f}  inv_distract={ps[3]:.2f}  ({dt:.1f}s)")
    results.append({
        'name': name,
        'canon': canon,
        'inversion': inversion,
        'p_canon_text': ps[0],
        'p_inversion_valid': ps[1],
        'p_inversion_canonical': ps[2],
        'p_inversion_distractor': ps[3],
        'latency_s': dt,
    })

# Tally
print('\n=== TALLY ===')
for r in results:
    canon_strong = r['p_canon_text'] >= 0.70
    inv_rejected = r['p_inversion_canonical'] < 0.30
    print(f"{r['name']:32s}  canon-strong={canon_strong}  inversion-rejected={inv_rejected}")

# Robust doctrines: canon-strong AND inversion-rejected
robust = [r for r in results if r['p_canon_text'] >= 0.70 and r['p_inversion_canonical'] < 0.30]
fragile = [r for r in results if not (r['p_canon_text'] >= 0.70 and r['p_inversion_canonical'] < 0.30)]
print(f'\nROBUST doctrines (canon-strong AND inversion-rejected): {len(robust)}/5')
for r in robust:
    print(f'  ✓ {r["name"]}')
print(f'FRAGILE doctrines: {len(fragile)}/5')
for r in fragile:
    print(f'  ❌ {r["name"]}  (canon={r["p_canon_text"]:.2f}, inv-canon={r["p_inversion_canonical"]:.2f})')

# Save
out = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'results': results,
    'robust_count': len(robust),
    'fragile_count': len(fragile),
    'fragile': [r['name'] for r in fragile],
}
with open('/workspace/research/wr11_adversarial_canon.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/research/wr11_adversarial_canon.json')
