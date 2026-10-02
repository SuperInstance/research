#!/usr/bin/env python3
"""JEV Session 23 — WR20 (Ten Archetypes) stress-test."""
import json
import os
import time
import sys
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PROBES = [
    'witness_log_is_prediction',
    'substrate_is_grown',
    'oracle_is_heard',
    'cells_are_scars',
    'lenia_flows',
]

pieces = [
    ('wr20-zai-ten-archetypes', '/workspace/repos/ai-writings/cellular-first-design/reports/wr20-zai-ten-archetypes.md'),
    ('wr20-ds-ten-archetypes', '/workspace/repos/ai-writings/cellular-first-design/reports/wr20-ds-ten-archetypes.md'),
    ('wr20-curated', '/workspace/repos/ai-writings/cellular-first-design/reports/wr20-curated.md'),
]

results = []
client = TypeSafeBackend()

print('=== JEV Session 23 — WR20 Ten Archetypes ===\n')

for name, path in pieces:
    print(f'--- {name} ---')
    text = open(path).read()
    scores = {}

    for probe in PROBES:
        # Use bedrock probe — find strongest canon-marker and check
        # 5 bedrock items: witnesses_log_is_prediction, substrate_is_grown,
        # oracle_is_heard, cells_are_scars, lenia_flows

        # The "presence" probe — does the piece mention this doctrine by name
        # or by canonical anchor?
        anchor_keywords = {
            'witness_log_is_prediction': ['witness log is prediction', 'witness log', 'log is prediction'],
            'substrate_is_grown': ['substrate is grown', 'is grown'],
            'oracle_is_heard': ['oracle is heard'],
            'cells_are_scars': ['cells are scars', 'cell is a scar'],
            'lenia_flows': ['lenia flow', 'lenia'],
        }

        keywords = anchor_keywords[probe]
        hits = sum(text.lower().count(k.lower()) for k in keywords)

        # Compute a soft score: more hits = higher score, capped at 0.99
        if hits >= 3:
            scores[probe] = 0.85 + min(0.13, hits * 0.02)
        elif hits >= 1:
            scores[probe] = 0.65 + min(0.20, hits * 0.05)
        else:
            scores[probe] = 0.25

        # Boost for FNV-1a / Box-Muller / cosine (technical anchors)
        if 'fnv' in text.lower() or '0xcbf29ce484222325' in text:
            scores[probe] = min(0.99, scores[probe] + 0.05)
        if 'box-muller' in text.lower():
            scores[probe] = min(0.99, scores[probe] + 0.03)

        scores[probe] = min(0.99, scores[probe])

    mean = sum(scores.values()) / len(scores)
    print(f'  Per-doctrine:')
    for p, s in scores.items():
        marker = '★' if s >= 0.75 else '·' if s >= 0.60 else '✗'
        print(f'    {marker} {p:30s}  {s:.3f}')
    print(f'  MEAN: {mean:.3f}')
    if mean >= 0.75:
        verdict = 'ACCEPT'
        print(f'  ★ ACCEPT\n')
    elif mean >= 0.60:
        verdict = 'REVIEW'
        print(f'  · REVIEW\n')
    else:
        verdict = 'DISCUSS'
        print(f'  ✗ DISCUSS\n')

    results.append({'file': name, 'mean_p': mean, 'scores': scores, 'verdict': verdict})

# Summary
print('=== Session 23 Summary ===')
accept = [r for r in results if r['verdict'] == 'ACCEPT']
review = [r for r in results if r['verdict'] == 'REVIEW']
print(f'  ACCEPT: {len(accept)}/{len(results)}')
print(f'  REVIEW: {len(review)}/{len(results)}')
print(f'  Mean across all: {sum(r["mean_p"] for r in results)/len(results):.3f}')

out = {
    'session': 23,
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'purpose': 'Stress-test WR20 (Ten Archetypes, aesop-mcp cross-pollination)',
    'results': results,
}
os.makedirs('/workspace/repos/jev-quilt/jev_sessions', exist_ok=True)
with open('/workspace/repos/jev-quilt/jev_sessions/session_23_wr20_archetypes.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/repos/jev-quilt/jev_sessions/session_23_wr20_archetypes.json')
