#!/usr/bin/env python3
"""
JEV Session 13 — Temporal narrative test.

Send JEV a sequence of states representing canon evolution:
  - State 1: substrate = 5 laws (BIND/LINK/EFFECT/VIEW/TICK)
  - State 2: substrate = 11 opcodes (add FORGET/PROOF/ROUTE/CRDT/WORLD/TIME)
  - State 3: substrate = 13 polyformalism ports

Test if JEV can track the evolution correctly across states.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# 3 era snapshots
ERAS = [
    ('era1_5laws', {
        'canonical_substrate': {
            'era': 'phase 1',
            'opcodes': ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK'],
        }
    }, [
        ('opcodes_count', 'choice', 'How many base opcodes are there?',
         {'5': 'five', '6': 'six', '11': 'eleven', '13': 'thirteen'}),
        ('opcode_BIND', 'noul', 'Is BIND a substrate opcode in this era?'),
        ('opcode_FORGET', 'noul', 'Is FORGET a substrate opcode in this era?'),
    ]),
    ('era2_11opcodes', {
        'canonical_substrate': {
            'era': 'phase 2',
            'opcodes': ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK', 'FORGET', 'PROOF', 'ROUTE', 'CRDT', 'WORLD', 'TIME'],
        }
    }, [
        ('opcodes_count', 'choice', 'How many base opcodes are there?',
         {'5': 'five', '6': 'six', '11': 'eleven', '13': 'thirteen'}),
        ('opcode_BIND', 'noul', 'Is BIND a substrate opcode?'),
        ('opcode_FORGET', 'noul', 'Is FORGET a substrate opcode?'),
        ('opcode_TIME', 'noul', 'Is TIME a substrate opcode?'),
    ]),
    ('era3_13ports', {
        'canonical_substrate': {
            'era': 'phase 3',
            'polyformalism_ports': 13,
            'languages': ['JS', 'Python', 'C', 'Rust', 'Go', 'Haskell', 'J', 'Lua', 'Zig', 'SubLEQ', 'Verilog', 'VHDL', 'Forth'],
        }
    }, [
        ('ports_count', 'choice', 'How many polyformalism ports?',
         {'5': 'five', '11': 'eleven', '13': 'thirteen', '15': 'fifteen'}),
        ('port_has_forth', 'noul', 'Is Forth one of the polyformalism languages?'),
        ('port_has_python', 'noul', 'Is Python one of the polyformalism languages?'),
        ('port_has_cobol', 'noul', 'Is Cobol one of the polyformalism languages?'),
    ]),
]

EXPECTED = {
    'era1_5laws': {
        'opcodes_count': '5', 'opcode_BIND': 'yes', 'opcode_FORGET': 'no',
    },
    'era2_11opcodes': {
        'opcodes_count': '11', 'opcode_BIND': 'yes', 'opcode_FORGET': 'yes', 'opcode_TIME': 'yes',
    },
    'era3_13ports': {
        'ports_count': '13', 'port_has_forth': 'yes', 'port_has_python': 'yes', 'port_has_cobol': 'no',
    },
}

def to_jev_q(e):
    name = e[0]; kind = e[1]; instr = e[2]
    q = {'name': name, 'type': kind, 'instructions': instr}
    if kind == 'choice':
        q['options'] = e[3]
    return q

print(f"=== JEV SESSION 13 — Temporal Narrative Test ===")
print(f"Eras: {len(ERAS)}")

b = TypeSafeBackend()
for era_name, state, questions in ERAS:
    print(f"\n--- {era_name} ---")
    decisions, meta = b.decide_batch(state, [to_jev_q(q) for q in questions])
    print(f"  latency: {meta.get('latency_ms', 'N/A')}ms")

    exp = EXPECTED[era_name]
    for i, q in enumerate(questions):
        name = q[0]
        d = decisions[i]
        expected = exp.get(name, '?')
        is_correct = False
        if q[1] == 'choice':
            if str(d.value).strip() == expected: is_correct = True
        else:
            try:
                v = float(d.value)
                if (expected == 'yes' and v >= 0.5) or (expected == 'no' and v < 0.5):
                    is_correct = True
            except: pass
        print(f"  {'✓' if is_correct else '✗'} {name:25s} expected={expected:5s} JEV={d.value} c={d.confidence:.2f}")

# Save
session_path = OUT / 'session_13_narrative.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'eras': ERAS,
        'expected': EXPECTED,
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
