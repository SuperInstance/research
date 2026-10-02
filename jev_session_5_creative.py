#!/usr/bin/env python3
"""
JEV Session 5 — Creative Substrate Scoring.

Use JEV as a stylistic referee: rate canonical Fleet Radio pieces
for voice, doctrine, novelty. Also test:
  - Does JEV prefer canonical pieces over LLM-generated prose?
  - Does JEV reward novel combinations of canonical elements?
"""
import os, json, time, sys, urllib.request
from pathlib import Path
import numpy as np

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# Load canonical pieces
CORPUS_DIR = Path('/workspace/repos/ai-writings/cellular-first-design/reports')
canonical = []
if CORPUS_DIR.exists():
    for f in sorted(CORPUS_DIR.glob('*.md')):
        text = f.read_text()[:1500]
        canonical.append((f.stem, text))

print(f"Loaded {len(canonical)} canonical pieces")
print()

# Build a battery of probing questions about CANONICAL vs DECOY pieces
PROBES = []
for name, text in canonical[:10]:  # first 10 pieces
    PROBES.append((f'voice_{name}', 'noul', f'Is the following text written in the canonical Fleet Radio voice?\n\n---\n{text}\n---'))
    PROBES.append((f'doctrine_{name}', 'noul', f'Does the following text align with cellular-first design substrate doctrine?\n\n---\n{text}\n---'))

print(f"Built {len(PROBES)} probes from canonical pieces")

# Define scoring criteria
RICH_STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'voice': 'Fleet Radio — technical-poetic naval transmission',
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'The oracle is heard, not stored.',
            'Lenia flows where Conway stands still.',
            'The canary hash 0xcbf29ce484222325 is the offset basis of all things.',
            'Thirteen ports, byte-exact.',
            'JEV says JEV is barely useful at substrate.'
        ],
        'negative_examples': [
            'Corporate marketing prose',
            'Generic LLM chatbot-style apologies',
            'Academic jargon without substrate metaphors'
        ]
    }
}

# Convert to JEV questions
def to_jev_q(e):
    name = e[0]; kind = e[1]; instr = e[2]
    q = {'name': name, 'type': kind, 'instructions': instr}
    return q

jev_q = [to_jev_q(e) for e in PROBES]

print(f"Calling JEV on {len(jev_q)} probes (rich state)...")
b = TypeSafeBackend()
decisions, meta = b.decide_batch(RICH_STATE, jev_q)
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")

# Aggregate
voice_scores = []
doctrine_scores = []
for i, e in enumerate(PROBES):
    name = e[0]
    d = decisions[i]
    try:
        v = float(d.value)
        if name.startswith('voice_'):
            voice_scores.append(v)
        else:
            doctrine_scores.append(v)
    except:
        pass

print()
print(f"Voice scores: mean={np.mean(voice_scores):.3f}, std={np.std(voice_scores):.3f}, min={min(voice_scores):.3f}, max={max(voice_scores):.3f}")
print(f"Doctrine scores: mean={np.mean(doctrine_scores):.3f}, std={np.std(doctrine_scores):.3f}, min={min(doctrine_scores):.3f}, max={max(doctrine_scores):.3f}")

# Save
session_path = OUT / 'session_5_canon_scoring.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'state': RICH_STATE,
        'probes': [{'name': p[0], 'kind': p[1]} for p in PROBES],
        'decisions': [{'kind': d.kind, 'value': str(d.value), 'confidence': d.confidence, 'name': PROBES[i][0]} for i, d in enumerate(decisions)],
        'voice_mean': float(np.mean(voice_scores)) if voice_scores else None,
        'doctrine_mean': float(np.mean(doctrine_scores)) if doctrine_scores else None,
    }, f, indent=2, default=str)

# Per-piece summary
print("\n=== Per-Piece Scores ===")
print(f"{'Piece':40s} {'voice':>8s} {'doctrine':>10s}")
print("-" * 60)
for i in range(0, len(decisions), 2):
    if i+1 >= len(decisions): break
    name_v = PROBES[i][0].replace('voice_', '')
    name_d = PROBES[i+1][0].replace('doctrine_', '')
    if name_v != name_d: continue
    try:
        v = float(decisions[i].value)
        dt = float(decisions[i+1].value)
        print(f"{name_v[:40]:40s} {v:8.3f} {dt:10.3f}")
    except: pass

print(f"\nSaved: {session_path}")
