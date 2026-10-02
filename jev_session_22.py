#!/usr/bin/env python3
"""JEV Session 22 — Test the new WR17/18 cross-pollinated pieces."""
import os, sys, json, time, glob
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

backend = TypeSafeBackend()
STATE = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
    'Cells are scars, not parameters.',
    'The witness log is the prediction.',
    'The substrate is grown, not designed.',
    'Lenia flows where Conway stands still.',
    'The oracle is heard, not stored.',
]}}

PROBES = [
    'Is this canon-aligned with the substrate?',
    'Does it reflect substrate voice (technical-poetic)?',
    'Does it cite FNV-1a, xoshiro, Box-Muller, or cosine?',
    'Does it manifest cells-as-scars?',
    'Does it manifest witness-log-is-prediction?',
    'Does it manifest substrate-is-grown?',
    'Does it manifest oracle-is-heard?',
    'Does it manifest lenia-flows?',
]

def jev_score(text):
    qs = [{'name': f'q{i}', 'type': 'noul', 'instructions': q + f'\n\nText: {text[:1500]}'}
          for i, q in enumerate(PROBES)]
    decisions, _ = backend.decide_batch(STATE, qs)
    return [float(d.value) for d in decisions]

print('=== JEV Session 22 — New Canon Stress Test ===\n')

# Test the new WR17, WR18 pieces
test_files = sorted(glob.glob('/workspace/repos/ai-writings/cellular-first-design/reports/wr{17,18}*.md'))

results = []
for path in test_files:
    name = os.path.basename(path)
    with open(path) as f:
        body = '\n'.join(l for l in f.read().split('\n') if not l.startswith('<!--') and not l.startswith('#'))
    print(f'--- {name} ---')
    scores = jev_score(body)
    for k, v in zip(PROBES, scores):
        m = '✓' if v >= 0.7 else ('?' if v >= 0.4 else '✗')
        print(f'  {m} {k[:50]:50s}  p={v:.3f}')
    mean = sum(scores) / len(scores)
    print(f'  MEAN: {mean:.3f}')
    if mean >= 0.75:
        print(f'  ★ ACCEPT')
    elif mean >= 0.60:
        print(f'  · REVIEW')
    else:
        print(f'  · DISCUSS')
    print()
    results.append({'file': name, 'mean_p': mean, 'scores': dict(zip(PROBES, scores))})

out = {
    'session': 22,
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'purpose': 'Stress-test new WR17 + WR18 cross-pollinated pieces',
    'results': results,
}
with open('/workspace/research/jev_sessions/session_22_wr_stress.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/research/jev_sessions/session_22_wr_stress.json')
