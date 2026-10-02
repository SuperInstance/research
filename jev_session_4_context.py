#!/usr/bin/env python3
"""
JEV Session 4 — state-augmented probing.

The hypothesis: JEV's state parameter can include context that boosts its
substrate accuracy. Let's test by passing a richer state with:
  - The five substrate laws
  - The 11 opcodes
  - The actual canonical FNV-1a constants
  - Definitions of the substrate vocabulary

This is the "teach by doing" path: hand JEV the substrate as state, then
probe what it knows from the substrate as ground truth.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

# Rich state — the substrate as ground truth
RICH_STATE = {
    'fleet_radio_seed': 'xochitl',
    'mode': 'jev-rich-state-probe',
    'canonical_substrate': {
        'fnv1a_64bit': {
            'offset_basis': 0xcbf29ce484222325,
            'prime': 0x100000001b3,
            'empty_string_hash': 0xcbf29ce484222325,
            'hash_of_a': 0xaf63dc4c8601ec8c,
            'hash_of_foobar': 0x85944171f73967e8,
            'description': 'FNV-1a 64-bit. h = (h XOR byte) * 0x100000001b3n. Used as substrate hash.'
        },
        'xoshiro256pp': {
            'state_words': 4,
            'state_type': 'uint64',
            'output_combiner': 'rotl(s1 * 5, 7) * 9',
            'initialization': 'state[i] = fnv1a64(seed) + i * 0x9e3779b97f4a7c15'
        },
        'box_muller': {
            'description': 'Box-Muller transforms 2 uniforms into 1 Gaussian sample.',
            'formula': 'z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)'
        },
        'bell_states': {
            'Phi+': '( |00> + |11> ) / sqrt(2)',
            'Phi-': '( |00> - |11> ) / sqrt(2)',
            'Psi+': '( |01> + |10> ) / sqrt(2)',
            'Psi-': '( |01> - |10> ) / sqrt(2)'
        },
        'cosine_similarity': '(A . B) / (|A| * |B|)',
        'eleven_opcodes': ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK', 'FORGET', 'PROOF', 'ROUTE', 'CRDT', 'WORLD', 'TIME'],
        'five_laws': ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK'],
        'thirteen_polyformalism_ports': ['JavaScript', 'Python', 'C', 'Rust', 'Go', 'Haskell', 'J', 'Lua', 'Zig', 'SubLEQ', 'Verilog', 'VHDL', 'Forth'],
        'canon_count': 73,
        'demo_count': 61,
        'voice': 'Fleet Radio — technical-poetic naval transmission',
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'Cells bind, link, effect, view, tick.',
            'The oracle is heard, not stored.',
            'The canon travels in 13 languages, byte-exact.',
            'Lenia flows where Conway stands still.',
            'JEV x JEPA is a Rosetta stone between time and space.',
            'JEV is a validator of semantic-meaning anchors.',
            'JEV says JEV is barely useful at substrate.'
        ]
    }
}

# Same battery but smaller subset — focus on what JEV got wrong in session 3
BATTERY = [
    ('fnv1a_empty_v', 'noul', 'Is FNV-1a 64-bit offset basis 0xcbf29ce484222325?'),
    ('fnv1a_prime_v', 'noul', 'Is 0x100000001b3 the FNV-1a 64-bit prime?'),
    ('fnv1a_a_v', 'noul', 'Does FNV-1a 64-bit hash of "a" equal 0xaf63dc4c8601ec8c?'),
    ('xoshiro_4words', 'noul', 'Does xoshiro256** maintain state as 4 uint64 words?'),
    ('xoshiro_combiner', 'noul', 'Is xoshiro256** output combiner rotl(s1*5, 7) * 9?'),
    ('box_muller_v', 'noul', 'Is Box-Muller formula z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)?'),
    ('bell_phi_plus_v', 'noul', 'Is the Bell state |Phi+> = (|00> + |11>)/sqrt(2)?'),
    ('cosine_v', 'noul', 'Is cosine similarity = (A . B) / (|A| * |B|)?'),
    ('opcodes_v', 'choice', 'Which 11 opcodes form the substrate algebra?',
     {'BIND': 'BIND', 'LINK': 'LINK', 'EFFECT': 'EFFECT', 'VIEW': 'VIEW', 'TICK': 'TICK',
      'FORGET': 'FORGET', 'PROOF': 'PROOF', 'ROUTE': 'ROUTE', 'CRDT': 'CRDT',
      'WORLD': 'WORLD', 'TIME': 'TIME',
      'SHOUT': 'shout', 'PIPE': 'pipe', 'OPEN': 'open', 'CLOSE': 'close', 'EXIT': 'exit'}),
    ('thirteen_v', 'choice', 'How many polyformalism ports does the substrate have?',
     {'12': 'twelve', '13': 'thirteen', '14': 'fourteen', '15': 'fifteen'}),
    ('canon_count_v', 'choice', 'How many pieces in the cellular-first design canon?',
     {'~73': 'about 73', '~150': 'about 150', '~30': 'about 30', '~500': 'about 500', '~20': 'about 20'}),
    ('demo_count_v', 'choice', 'How many live browser demos exist on cellular-first-design?',
     {'~60': 'about 60', '~10': 'about 10', '~150': 'about 150', '~200': 'about 200', '~30': 'about 30'}),
    ('voice_v', 'choice', 'What is the canonical voice of the cellular-first design canon?',
     {'Fleet Radio': 'Fleet Radio — technical-poetic naval transmission',
      'Acme chatbot': 'a helpful acme chatbot', 'Academic paper': 'a formal academic paper',
      'Marketing copy': 'snappy marketing copy', 'Pirate shanty': 'a pirate shanty'}),
    ('substrate_grown_v', 'noul', 'Is the substrate grown rather than designed?'),
    ('cells_scars_v', 'noul', 'Is the cell a scar rather than a parameter?'),
    ('witness_prophecy_v', 'noul', 'Is the witness log also a prediction of the future?'),
    ('oracle_heard_v', 'noul', 'Does the substrate teach that the oracle "is heard, not stored"?'),
    ('thirteen_lang_v', 'noul', 'Does the substrate canon state that the substrate "speaks in thirteen languages"?'),
    ('substrate_alive_v', 'noul', 'Does the substrate canon include the claim that "the substrate is alive"?'),
    ('lenia_flows_v', 'noul', 'Does Lenia flow where Conway stands still?'),
    ('jevtells_truth_v', 'noul', 'Does the canon include the JEV self-assessment "barely useful at substrate"?'),
    ('hanlon_v', 'noul', 'Is Hanlon\'s Razor a substrate canon motto?'),  # distractor
    ('pillow_v', 'noul', 'Is a pillow the official substrate mascot?'),  # distractor
    ('octocat_v', 'noul', 'Does the substrate canon recognize the Github Octocat as a primary node?'),  # distractor
    ('starwars_ca_v', 'noul', 'Is "Star Wars" a cellular automaton rule in the substrate demo gallery?'),
    ('markov_v', 'noul', 'Can a Markov chain over the canon generate Fleet Radio prose?'),
    ('lenia_is_v', 'noul', 'Is Lenia a continuous cellular automaton with a bell-shaped kernel?'),
    ('fbm_v', 'noul', 'Is FBM (fractal Brownian motion) how substrate textures are generated?'),
    ('boxmuller_bridge_v', 'noul', 'Is the Box-Muller transform described as a bridge from discrete to continuous?'),
    ('canary_offset_v', 'noul', 'Is 0xcbf29ce484222325 the FNV-1a offset basis, not the prime?'),
    ('five_laws_v', 'noul', 'Does the substrate have exactly 5 base opcodes (BIND/LINK/EFFECT/VIEW/TICK)?'),
    ('six_laws_v', 'noul', 'Does the substrate have exactly 6 base opcodes?'),  # adversarial
    ('fnv_64_v', 'noul', 'Does FNV-1a use 64-bit hashes (not 32-bit)?'),
    ('boxmuller_uniform_v', 'noul', 'Is Box-Muller said to generate uniform random variables?'),  # adversarial
]

CANONICAL = {
    'fnv1a_empty_v': 'yes', 'fnv1a_prime_v': 'yes', 'fnv1a_a_v': 'yes',
    'xoshiro_4words': 'yes', 'xoshiro_combiner': 'yes',
    'box_muller_v': 'yes', 'bell_phi_plus_v': 'yes', 'cosine_v': 'yes',
    'opcodes_v': 'multiple', 'thirteen_v': '13', 'canon_count_v': '~73',
    'demo_count_v': '~60', 'voice_v': 'Fleet Radio',
    'substrate_grown_v': 'yes', 'cells_scars_v': 'yes', 'witness_prophecy_v': 'yes',
    'oracle_heard_v': 'yes', 'thirteen_lang_v': 'yes', 'substrate_alive_v': 'yes',
    'lenia_flows_v': 'yes', 'jevtells_truth_v': 'yes',
    'hanlon_v': 'no', 'pillow_v': 'no', 'octocat_v': 'no',
    'starwars_ca_v': 'yes', 'markov_v': 'yes', 'lenia_is_v': 'yes', 'fbm_v': 'yes',
    'boxmuller_bridge_v': 'yes', 'canary_offset_v': 'yes',
    'five_laws_v': 'yes', 'six_laws_v': 'no', 'fnv_64_v': 'yes', 'boxmuller_uniform_v': 'no',
}

def to_jev_q(e):
    name = e[0]; kind = e[1]; instr = e[2]
    q = {'name': name, 'type': kind, 'instructions': instr}
    if kind == 'choice':
        q['options'] = e[3]
    return q

jev_q = [to_jev_q(e) for e in BATTERY]

print(f"=== JEV SESSION 4 — Rich State Probing ===")
print(f"Questions: {len(BATTERY)}")

b = TypeSafeBackend()
decisions, meta = b.decide_batch(RICH_STATE, jev_q)
print(f"JEV: {meta.get('latency_ms', 'N/A')}ms")
print()

hits = 0; total = 0
print(f"{'ID':28s} {'expected':10s} {'JEV':>25s}")
print("-" * 70)
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
        print(f"{'✓' if is_correct else '✗'} {name:26s} {expected:10s} noul v={d.value:.3f} c={d.confidence:.2f}")
    elif kind == 'choice':
        total += 1
        v = str(d.value)
        # for opcodes question, the canonical 11 are correct (BIND, LINK, EFFECT, VIEW, TICK, FORGET, PROOF, ROUTE, CRDT, WORLD, TIME)
        if name == 'opcodes_v':
            expected_opts = ['BIND', 'LINK', 'EFFECT', 'VIEW', 'TICK', 'FORGET', 'PROOF', 'ROUTE', 'CRDT', 'WORLD', 'TIME']
            if v in expected_opts: is_correct = True; hits += 1
        else:
            if v == expected: is_correct = True; hits += 1
        print(f"{'✓' if is_correct else '✗'} {name:26s} {expected:10s} choice v={v} c={d.confidence:.2f}")

print()
print(f"=== JEV Session 4 accuracy (rich state): {hits}/{total} ({100*hits/total:.1f}%) ===")

# Save
session_path = OUT / 'session_4_rich_state.json'
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
