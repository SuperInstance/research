#!/usr/bin/env python3
"""JEV Session 22 v2 — direct test."""
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
    'Is this canon-aligned?',
    'Substrate voice (technical-poetic)?',
    'Numerical substrate facts (FNV-1a, xoshiro, Box-Muller, cosine)?',
    'Cells-are-scars doctrine present?',
    'Witness-log-is-prediction doctrine present?',
    'Substrate-is-grown doctrine present?',
    'Oracle-is-heard doctrine present?',
    'Lenia-flows doctrine present?',
]

def jev_score(text):
    qs = [{'name': f'q{i}', 'type': 'noul', 'instructions': q + f'\n\nText: {text[:1200]}'}
          for i, q in enumerate(PROBES)]
    decisions, _ = backend.decide_batch(STATE, qs)
    return [float(d.value) for d in decisions]

print('=== JEV Session 22 v2 — WR17/18 Stress Test ===\n')

# Find WR17, WR18 files
test_files = []
for f in sorted(glob.glob('/workspace/repos/ai-writings/cellular-first-design/reports/wr1[78]*.md')):
    if 'kimi' not in f:  # Skip Kimi-only files
        test_files.append(f)

print(f'Found {len(test_files)} files\n')

results = []
for path in test_files:
    name = os.path.basename(path)
    with open(path) as f:
        text = f.read()
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('<!--') and not l.startswith('#'))
    if len(body) < 50:
        continue
    print(f'--- {name} ({len(body)} chars) ---')
    scores = jev_score(body)
    for k, v in zip(PROBES, scores):
        m = '✓' if v >= 0.7 else ('?' if v >= 0.4 else '✗')
        print(f'  {m} {k[:50]:50s}  p={v:.3f}')
    mean = sum(scores) / len(scores)
    print(f'  MEAN: {mean:.3f}')
    if mean >= 0.75:
        verdict = 'ACCEPT'
    elif mean >= 0.60:
        verdict = 'REVIEW'
    else:
        verdict = 'DISCUSS'
    print(f'  Verdict: {verdict}\n')
    results.append({'file': name, 'mean_p': mean, 'verdict': verdict, 'scores': dict(zip(PROBES, scores))})

out = {
    'session': 22,
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'purpose': 'Stress-test new WR17 + WR18 cross-pollinated pieces',
    'results': results,
}
fname = '/workspace/research/jev_sessions/session_22_wr_stress.json'
with open(fname, 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: {fname}')
print(f'\n=== Summary ===')
for r in results:
    print(f"  {r['verdict']:8s}  {r['file']}  mean={r['mean_p']:.3f}")
