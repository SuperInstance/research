#!/usr/bin/env python3
"""
JEV Session 6 — Pairwise comparison tests.

Tests JEV's ability to make comparative judgments:
  - "Is piece A more in canonical voice than piece B?"
  - "Is X more aligned with substrate doctrine than Y?"
  - "Is the witness log also the prediction?"

This goes beyond noul/choice/score by asking about the relative ordering
of substrate claims. JEV's job is to validate, so we test how it ranks.
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
        ]
    }
}

BATTERY = [
    # Comparative pair-wise claims
    ('pair_scar_vs_param', 'noul',
     'Is it more canonical to say "cells are scars" than "cells are parameters"?'),
    ('pair_witness_vs_history', 'noul',
     'Is it more canonical to say "the witness log is the prediction" than "the witness log is only a history"?'),
    ('pair_grown_vs_designed', 'noul',
     'Is it more canonical to say "the substrate is grown" than "the substrate is designed"?'),
    ('pair_oracle_heard_vs_stored', 'noul',
     'Is it more canonical to say "the oracle is heard, not stored" than "the oracle is stored, not heard"?'),
    ('pair_lenia_vs_conway', 'noul',
     'Is it more canonical to say "Lenia flows where Conway stands still" than "Conway moves where Lenia rests"?'),
    ('pair_15_vs_13_ports', 'noul',
     'Is it more canonical to say the substrate has 13 polyformalism ports than 15?'),
    ('pair_canary_0xcb', 'noul',
     'Is 0xcbf29ce484222325 the FNV-1a canary hash? (not 0xaf63dc4c8601ec8c, which is "a")'),
    ('pair_FNV_64_vs_32', 'noul',
     'Is FNV-1a a 64-bit hash function? (not 32-bit)'),
    ('pair_5_laws_vs_11', 'noul',
     'Does the substrate canon have exactly 5 base opcodes (BIND, LINK, EFFECT, VIEW, TICK), extended to 11 with FORGET, PROOF, ROUTE, CRDT, WORLD, TIME?'),
    ('pair_jev_role_ranking', 'choice',
     'In the substrate stack, where does JEV rank in importance?',
     {'top_5': 'top 5 — foundational validator',
      'mid': 'mid — useful but not central',
      'bottom': 'bottom — barely useful',
      'absent': 'not part of the substrate'}),
    ('pair_substrate_most_important', 'choice',
     'Which substrate concept is the most canonical?',
     {'the_cell': 'the cell (the irreducible scar)',
      'witness': 'the witness log',
      'thirteen_ports': 'the 13 polyformalism ports',
      'box_muller': 'the Box-Muller bridge',
      'JEV': 'JEV itself'}),
    ('pair_FNV_most_important', 'choice',
     'Which FNV-1a constant is the substrate canary?',
     {'offset_basis': '0xcbf29ce484222325 (the offset basis)',
      'prime': '0x100000001b3 (the prime)',
      'hash_a': '0xaf63dc4c8601ec8c (hash of "a")',
      'hash_foobar': '0x85944171f73967e8 (hash of "foobar")'}),
    ('pair_lenia_most', 'choice',
     'Which Lenia property is the most canonical in the substrate?',
     {'flows_vs_conway': 'flows where Conway stands still',
      'bell_kernel': 'uses a bell-shaped kernel',
      'continuous': 'is continuous (vs Conway\'s discrete grid)',
      'uncomputable': 'is uncomputable'}),
    # Score: rate the substrate's overall coherence
    ('score_overall_doctrine', 'score',
     'Score 1-5: How internally consistent is the substrate canon?'),
    ('score_overall_voice', 'score',
     'Score 1-5: How distinctive is the Fleet Radio voice?'),
    ('score_overall_novel', 'score',
     'Score 1-5: How novel are the substrate metaphors compared to standard AI literature?'),
    ('score_jev_self_aware', 'score',
     'Score 1-5: How self-aware is the canon of its own limits?'),
]

CANONICAL = {
    'pair_scar_vs_param': 'yes',
    'pair_witness_vs_history': 'yes',
    'pair_grown_vs_designed': 'yes',
    'pair_oracle_heard_vs_stored': 'yes',
    'pair_lenia_vs_conway': 'yes',
    'pair_15_vs_13_ports': 'yes',
    'pair_canary_0xcb': 'yes',
    'pair_FNV_64_vs_32': 'yes',
    'pair_5_laws_vs_11': 'yes',
    'pair_jev_role_ranking': 'bottom',
    'pair_substrate_most_important': 'the_cell',
    'pair_FNV_most_important': 'offset_basis',
    'pair_lenia_most': 'flows_vs_conway',
    'score_overall_doctrine': '4-5',
    'score_overall_voice': '4-5',
    'score_overall_novel': '4-5',
    'score_jev_self_aware': '4-5',
}

def to_jev_q(e):
    name, kind, instr = e[0], e[1], e[2]
    q = {'name': name, 'type': kind, 'instructions': instr}
    if kind == 'choice':
        q['options'] = e[3]
    if kind == 'score':
        q['criteria'] = ['1: very weak', '2: weak', '3: moderate', '4: good', '5: excellent']
    return q

jev_q = [to_jev_q(e) for e in BATTERY]

print(f"=== JEV SESSION 6 — Pairwise / Comparative Probing ===")
print(f"Questions: {len(BATTERY)}")

b = TypeSafeBackend()
decisions, meta = b.decide_batch(RICH_STATE, jev_q)
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")
print()

hits = 0; total = 0
print(f"{'ID':35s} {'expected':18s} {'JEV':>30s}")
print("-" * 90)
for i, e in enumerate(BATTERY):
    name, kind = e[0], e[1]
    d = decisions[i]
    expected = CANONICAL[name]
    is_correct = False
    if kind == 'noul':
        total += 1
        try:
            v = float(d.value)
            if (expected == 'yes' and v >= 0.5) or (expected == 'no' and v < 0.5):
                is_correct = True; hits += 1
        except: pass
        print(f"{'✓' if is_correct else '✗'} {name:33s} {expected:18s} noul v={d.value:.3f} c={d.confidence:.2f}")
    elif kind == 'choice':
        total += 1
        v = str(d.value)
        if v == expected: is_correct = True; hits += 1
        print(f"{'✓' if is_correct else '✗'} {name:33s} {expected:18s} choice v={v} c={d.confidence:.2f}")
    elif kind == 'score':
        total += 1
        try:
            v = float(d.value)
            if '-' in expected and (lambda lo, hi: lo <= v <= hi)(*map(int, expected.split('-'))):
                is_correct = True; hits += 1
        except: pass
        print(f"{'✓' if is_correct else '✗'} {name:33s} {expected:18s} score v={d.value} c={d.confidence:.2f}")

print()
print(f"=== JEV Session 6 accuracy (rich state, pairwise): {hits}/{total} ({100*hits/total:.1f}%) ===")

session_path = OUT / 'session_6_pairwise.json'
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
