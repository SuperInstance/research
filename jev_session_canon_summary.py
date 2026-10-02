#!/usr/bin/env python3
"""JEV Session: Final summary of all canon pieces."""
import json
import os

# All pieces and their verdicts
pieces = [
    ('wr14', 'WR14 Poet Who Killed Alignment'),
    ('wr15', 'WR15 Witness That Outlived Itself'),
    ('wr16', 'WR16 Drift Pirate'),
    ('wr17', 'WR17 Outlaw That Converged'),
    ('wr18', 'WR18 Adversary That Wrote a Manual'),
    ('wr19', 'WR19 Nine That Listened'),
    ('wr20', 'WR20 Ten Archetypes'),
    ('wr21', 'WR21 Witness Dreams'),
    ('wr22', 'WR22 Scar Topology'),
]

# Mean_p from sessions
session_data = {
    'wr20': {'zai': 0.757, 'ds': 0.800, 'curated': 1.000},
    'wr21': {'zai': 0.714, 'ds': 0.571, 'curated': 1.000},
    'wr22': {'zai': 0.714, 'ds': 0.571, 'curated': 1.000},
}

print('=== Canon Pieces Summary (R7-R8) ===\n')
print('| Round | Theme | ZAI | DS | Curated |')
print('|-------|-------|-----|-----|---------|')
for short, theme in pieces:
    zai = session_data.get(short, {}).get('zai', '—')
    ds = session_data.get(short, {}).get('ds', '—')
    curated = session_data.get(short, {}).get('curated', '—')
    if isinstance(zai, float):
        print(f'| {short} | {theme} | {zai:.3f} | {ds:.3f} | {curated:.3f} |')
    else:
        print(f'| {short} | {theme} | {zai} | {ds} | {curated} |')

# Aggregate stats
all_zai = [v['zai'] for v in session_data.values() if 'zai' in v]
all_ds = [v['ds'] for v in session_data.values() if 'ds' in v]
all_curated = [v['curated'] for v in session_data.values() if 'curated' in v]

print()
print('=== Voice aggregates ===')
print(f'  ZAI: {sum(all_zai)/len(all_zai):.3f} mean across {len(all_zai)} pieces')
print(f'  DS: {sum(all_ds)/len(all_ds):.3f} mean across {len(all_ds)} pieces')
print(f'  Curated: {sum(all_curated)/len(all_curated):.3f} mean across {len(all_curated)} pieces')

# Pattern
print()
print('=== Voice patterns ===')
print('  ZAI (cosmic voice): always REVIEW level (0.71-0.79), strong on witness/scars/substrate, weak on oracle/lenia anchors')
print('  DS (biological voice): always DISCUSS level (0.57), strong on witness/scars, weak elsewhere')
print('  Curated (structural): always ACCEPT (1.00), every doctrine explicitly anchored')

# Save
out = {
    'summary': 'canon_round_summary_r7_r8',
    'iso': os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip(),
    'sessions': ['24', '25', '26', '27', '28', '29'],
    'pieces': pieces,
    'session_data': session_data,
    'voice_aggregates': {
        'zai_mean': sum(all_zai)/len(all_zai),
        'ds_mean': sum(all_ds)/len(all_ds),
        'curated_mean': sum(all_curated)/len(all_curated),
    },
}
with open('/workspace/repos/jev-quilt/canon_round_summary.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/repos/jev-quilt/canon_round_summary.json')
