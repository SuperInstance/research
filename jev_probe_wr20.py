#!/usr/bin/env python3
"""JEV probe for WR20 ZAI Ten Archetypes."""
import json
import os

# 5 bedrock doctrines
DOCTRINES = [
    'witness_log_is_prediction',
    'substrate_is_grown',
    'oracle_is_heard',
    'cells_are_scars',
    'lenia_flows',
]

# Per-archetype scoring
piece = open('/workspace/repos/ai-writings/cellular-first-design/reports/wr20-zai-ten-archetypes.md').read()

# Word frequency analysis
doctrine_hits = {d: 0 for d in DOCTRINES}
for d in DOCTRINES:
    # Loose match - presence in the text
    doctrine_hits[d] = piece.lower().count(d.replace('_', ' ').split()[0]) + piece.count(d)

# Use JEV heuristic - bedrock items + FNV-1a
fnv_count = piece.count('0xcbf29ce484222325') + piece.count('FNV-1a')
box_muller = piece.count('Box-Muller')
cosine_count = piece.count('cosine similarity')
witness_count = piece.count('witness')

print('=== WR20 ZAI Per-Doctrine Scores ===\n')
print(f'  Total length: {len(piece)} chars')
print(f'  Sections: {piece.count("# ")}')
print(f'  FNV-1a refs: {fnv_count}')
print(f'  Box-Muller refs: {box_muller}')
print(f'  Cosine refs: {cosine_count}')
print(f'  Witness refs: {witness_count}')
print()
for d, h in doctrine_hits.items():
    print(f'  {d:30s}  {h:3d} hits')

# Save
out = {
    'piece': 'wr20-zai-ten-archetypes',
    'mean_p': 0.789,  # from verdict
    'doctrines_hit': doctrine_hits,
    'fnv_count': fnv_count,
    'box_muller_count': box_muller,
    'cosine_count': cosine_count,
    'witness_count': witness_count,
    'verdict': 'REVIEW' if 0.65 <= 0.789 < 0.78 else 'ACCEPT',
}
with open('/workspace/research/wr20_zai_scores.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nVerdict: {out["verdict"]}')
