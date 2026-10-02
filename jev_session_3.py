#!/usr/bin/env python3
"""
JEV Session 3 — Teach & Test the substrate semantics.

Push JEV through deep semantic tasks:
  - Reading comprehension of canonical sentences ("the witness log is the prediction")
  - Family relations in the substrate algebra (BIND then LINK vs LINK then BIND)
  - Identifying which canonical piece defines a term
  - Self-consistency checks on the canon
  - Adversarial probes (subtle misstatements of canonical)

Each question is designed to find the edges of JEV's substrate knowledge.
"""
import os, json, time, sys, urllib.request
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')
OUT.mkdir(parents=True, exist_ok=True)

# Task battery — pushes JEV on more nuanced substrate knowledge

BATTERY = [
    # === Reading comprehension ===
    ('read_witness_log', 'noul',
     'Does the substrate canon state that "the witness log is the prediction"?'),
    ('read_novelty_substrate', 'noul',
     'Does the substrate canon state that "novelty is substrate"?'),
    ('read_cells_are_scars', 'noul',
     'Does the substrate canon state that "cells are scars, not parameters"?'),
    ('read_thirteen_ports', 'noul',
     'Does the substrate canon state that the substrate "speaks in thirteen languages"?'),
    ('read_15dials', 'noul',
     'Does each cell have exactly 15 dials in the substrate?'),  # distractor
    ('read_canary', 'noul',
     'Is the empty-string FNV-1a hash referred to as "the canary" 0xcbf29ce484222325?'),
    ('read_box_muller_bridge', 'noul',
     'Is the Box-Muller transform described as a bridge from discrete to continuous?'),
    ('read_witness_prophecy', 'noul',
     'Is "the witness is the prophecy" a Fleet Radio phrase?'),
    ('read_heard_not_stored', 'noul',
     'Does the substrate teach that the oracle "is heard, not stored"?'),
    ('read_lost_to_memory', 'noul',
     'Does the canon say "lost to memory" is the substrate enemy?'),

    # === Family relations in the algebra ===
    ('rel_BIND_LINK', 'noul',
     'In the substrate algebra, can a cell be LINKed to a name that has not yet been BINDed?'),
    ('rel_VIEW_mutates', 'noul',
     'Does the substrate VIEW opcode mutate the cell?'),
    ('rel_TICK_time', 'noul',
     'Is TICK the substrate opcode that advances the clock?'),
    ('rel_FORGET_recoverable', 'noul',
     'Is FORGET a reversible operation in the substrate?'),
    ('rel_PROOF_evidence', 'noul',
     'Is PROOF the opcode that verifies a witness hash?'),
    ('rel_TIME_predictable', 'noul',
     'Is TIME the substrate opcode that travels back to a past witness-log tick?'),

    # === Identifying canonical pieces ===
    ('piece_witness_pred', 'noul',
     'Is the paper "paper-024-witness-is-prophecy" in the substrate canon?'),
    ('piece_lenia_ocean', 'noul',
     'Is the Fleet Radio piece "Lenia as ocean" in the canon?'),
    ('piece_bell_tarot', 'noul',
     'Is "A Bell-State Tarot Reading" a Fleet Radio piece in the canon?'),
    ('piece_polyformal', 'noul',
     'Is "Polyformalism as Canon" a Fleet Radio piece?'),
    ('piece_witness_log_paper', 'noul',
     'Is "paper-003-witness-log" one of the canonical papers?'),

    # === Adversarial: subtle misstatements ===
    ('adversarial_witness_future', 'noul',
     'Does the substrate state that "the witness log is the past only, never the future"?'),
    ('adversarial_5Laws_6', 'noul',
     'Does the substrate have exactly 6 base opcodes (BIND/LINK/EFFECT/VIEW/TICK/FORGET)?'),
    ('adversarial_FNV_byte', 'noul',
     'Does FNV-1a use 32-bit hashes (rather than 64-bit)?'),
    ('adversarial_BoxM_mean01', 'noul',
     'Is Box-Muller said to generate uniform random variables?'),
    ('adversarial_canon_1000', 'noul',
     'Are there approximately 1000 pieces in the cellular-first design canon?'),

    # === Deep substrate philosophy ===
    ('deep_jev_rosetta', 'noul',
     'Is "JEV × JEPA" described in the substrate as a Rosetta stone between time and space?'),
    ('deep_jev_validator_only', 'noul',
     'Is JEV known in the substrate as a validator of semantic-meaning anchors rather than a generator?'),
    ('deep_substrate_alive', 'noul',
     'Does the substrate canon include the claim that "the substrate is alive"?'),
    ('deep_speciation_of_monolith', 'noul',
     'Is "the speciation of the monolith" a substrate canon essay title?'),

    # === Demos - which ones exist (noul y/n per demo) ===
    ('demo_d20_exists', 'noul',
     'Does the substrate have a demo at cellular-first-design/d20/ (a dice roller)?'),
    ('demo_turing_exists', 'noul',
     'Does the substrate have a demo at cellular-first-design/turing/ (a Turing machine)?'),
    ('demo_fibonacci_exists', 'noul',
     'Does the substrate have a demo at cellular-first-design/fibonacci/ (a Fibonacci generator)?'),  # distractor
    ('demo_qubit3_exists', 'noul',
     'Does the substrate have a demo at cellular-first-design/qubit-3/ (a 3-qubit quantum simulator)?'),
    ('demo_ritual_exists', 'noul',
     'Does the substrate have a demo at cellular-first-design/ritual/ (a liturgical ceremony)?'),  # distractor

    # === JEV's role in substrate-forge ===
    ('jev_compile_cell', 'noul',
     'In substrate-forge, does JEV validate the cross-port hash equivalence for a compiled cell?'),
    ('jev_substr_rejection', 'noul',
     'Is the "JEV says JEV is barely useful at substrate" position held in the canon as a humbling self-assessment?'),

    # === Edge cases ===
    ('edge_canary_prime_q', 'noul',
     'Is 0xcbf29ce484222325 the FNV-1a offset basis, NOT the prime?'),
    ('edge_yes_or_no', 'noul',
     'Is JEV, as a substrate-validated model, expected to know the canonical answers to substrate-domain questions?'),

    # === Score questions ===
    ('score_substrate_foundation', 'score',
     'Score 1-5: How foundational is JEV for the long-term cellular-first design canon?'),
    ('score_doctrine_drift', 'score',
     'Score 1-5: How much does JEV doctrine drift between sessions?'),
]

def to_jev_q(entry):
    id = entry[0]
    kind = entry[1]
    instr = entry[2]
    q = {'name': id, 'type': kind, 'instructions': instr}
    if kind == 'score':
        q['criteria'] = [
            '1: very weak', '2: weak', '3: moderate', '4: good', '5: excellent'
        ]
    return q

jev_q = [to_jev_q(e) for e in BATTERY]

print(f"=== JEV SESSION 3 — Deep Substrate Probing ===")
print(f"Questions: {len(BATTERY)}")

state = {'fleet_radio_seed': 'xochitl', 'mode': 'jev-deep-probe-3'}
b = TypeSafeBackend()
decisions, meta = b.decide_batch(state, jev_q)
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")

# Canonical mapping for analysis
CANONICAL = {
    'read_witness_log': 'yes', 'read_novelty_substrate': 'yes',
    'read_cells_are_scars': 'yes', 'read_thirteen_ports': 'yes',
    'read_15dials': 'no',  # it's 16
    'read_canary': 'yes',
    'read_box_muller_bridge': 'yes', 'read_witness_prophecy': 'yes',
    'read_heard_not_stored': 'yes', 'read_lost_to_memory': 'no',  # maybe
    'rel_BIND_LINK': 'no',  # must BIND first
    'rel_VIEW_mutates': 'no', 'rel_TICK_time': 'yes',
    'rel_FORGET_recoverable': 'no', 'rel_PROOF_evidence': 'yes',
    'rel_TIME_predictable': 'yes',
    'piece_witness_pred': 'yes', 'piece_lenia_ocean': 'yes',
    'piece_bell_tarot': 'yes', 'piece_polyformal': 'yes', 'piece_witness_log_paper': 'yes',
    'adversarial_witness_future': 'no', 'adversarial_5Laws_6': 'no',  # 5 not 6
    'adversarial_FNV_byte': 'no',  # 64-bit
    'adversarial_BoxM_mean01': 'no',  # normal/Gaussian, not uniform
    'adversarial_canon_1000': 'no',  # ~73
    'deep_jev_rosetta': 'yes', 'deep_jev_validator_only': 'yes',
    'deep_substrate_alive': 'yes', 'deep_speciation_of_monolith': 'yes',
    'demo_d20_exists': 'yes', 'demo_turing_exists': 'yes',
    'demo_fibonacci_exists': 'no', 'demo_qubit3_exists': 'yes',
    'demo_ritual_exists': 'no',
    'jev_compile_cell': 'yes', 'jev_substr_rejection': 'yes',
    'edge_canary_prime_q': 'yes',  # canary is offset basis
    'edge_yes_or_no': 'yes',
    'score_substrate_foundation': '4-5', 'score_doctrine_drift': '1-2',
}

# Print
print()
print(f"{'ID':35s} {'expected':10s} {'JEV':>30s}")
print("-" * 80)
hits = 0
total = 0
for i, e in enumerate(BATTERY):
    name, kind = e[0], e[1]
    d = decisions[i] if i < len(decisions) else None
    if d is None: continue
    expected = CANONICAL.get(name, '?')
    is_correct = False
    if kind == 'noul':
        try:
            v = float(d.value)
            if expected == 'yes' and v >= 0.5: is_correct = True; hits += 1
            elif expected == 'no' and v < 0.5: is_correct = True; hits += 1
        except (ValueError, TypeError): pass
        total += 1
        marker = '✓' if is_correct else '✗'
        print(f"{marker} {name:33s} {expected:10s} {d.kind:5s} v={str(d.value)[:15]:15s} c={d.confidence:.2f}")
    elif kind == 'score':
        # d.value will be a number 1-5
        try:
            v = float(d.value)
            if '-' in expected:
                lo, hi = map(int, expected.split('-'))
                if lo <= v <= hi: is_correct = True; hits += 1
            total += 1
            marker = '✓' if is_correct else '✗'
            print(f"{marker} {name:33s} {expected:10s} {d.kind:5s} v={v:.1f} c={d.confidence:.2f}")
        except (ValueError, TypeError):
            print(f"  {name:33s} {expected:10s} {d.kind:5s} v={str(d.value)[:30]}")
    elif kind == 'choice':
        marker = '?'
        print(f"  {name:33s} {expected:10s} {d.kind:5s} v={str(d.value)[:30]}")

print()
print(f"=== JEV Session 3 accuracy: {hits}/{total} ({100*hits/total:.1f}%) ===")

# Save
session_path = OUT / 'session_3_deep.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'battery': BATTERY,
        'decisions': [{'kind': d.kind, 'value': str(d.value), 'confidence': d.confidence} for d in decisions],
        'canonical': CANONICAL,
        'hits': hits, 'total': total,
    }, f, indent=2, default=str)
print(f"Saved: {session_path}")
