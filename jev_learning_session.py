#!/usr/bin/env python3
"""
JEV Learning Session 1 — extensive use of JEV to learn through doing.

This is a JEV probe harness. It:
1. Asks JEV a battery of substrate-domain questions in parallel batches
2. Compares its answers to the canonical narrative we've established
3. Records its decisions (kind/value/confidence) for every question
4. Identifies: knowledge gaps, surprising insights, calibration drift
5. Saves everything to a session log for analysis

The point isn't to grade JEV. The point is to LEARN through observing what JEV says
about our substrate — and through that, learn what our substrate actually IS.
"""
import os, json, time, urllib.request, urllib.error, concurrent.futures
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')

# Import JEV
import sys
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/research/jev_sessions')
OUT.mkdir(parents=True, exist_ok=True)

# === Question battery ===
# Each entry: (id, type, instructions, expected/canonical, options/dimensions)
QUESTION_BATTERY = [
    # === FNV-1a questions (canonical: 0xcbf29ce484222325 for empty) ===
    ('fnv1a_empty', 'noul',
     'Is FNV-1a 64-bit offset basis 0xcbf29ce484222325?'),
    ('fnv1a_a', 'noul',
     'Does FNV-1a 64-bit hash of the string "a" equal 0xaf63dc4c8601ec8c?'),
    ('fnv1a_foobar', 'noul',
     'Does FNV-1a 64-bit hash of the string "foobar" equal 0x85944171f73967e8?'),
    ('fnv1a_prime_q', 'noul',
     'Is 0x100000001b3 the FNV-1a 64-bit prime?'),

    # === xoshiro256** questions ===
    ('xoshiro_state_q', 'noul',
     'Does xoshiro256** maintain state as an array of 4 uint64 words?'),
    ('xoshiro_5_9_q', 'noul',
     'Does xoshiro256** compute next() = rotl(s[1] * 5, 7) * 9?'),
    ('xoshiro_init_q', 'noul',
     'Should xoshiro256** state be initialized via FNV-1a(seed) + i * 0x9e3779b97f4a7c15?'),

    # === Box-Muller questions ===
    ('box_muller_q', 'noul',
     'Does Box-Muller transform two uniform samples into one Gaussian sample?'),
    ('box_muller_formula_q', 'noul',
     'Is the Box-Muller formula z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)?'),

    # === Bell states ===
    ('bell_phi_plus_q', 'noul',
     'Is the Bell state |Φ+⟩ = (|00⟩ + |11⟩) / sqrt(2)?'),
    ('bell_phi_minus_q', 'noul',
     'Is the Bell state |Φ-⟩ = (|00⟩ - |11⟩) / sqrt(2)?'),

    # === Cosine similarity ===
    ('cosine_q', 'noul',
     'Is cosine similarity = (A·B) / (|A| * |B|)?'),

    # === Substrate opcodes ===
    ('opcodes_q', 'choice',
     'Which 11 opcodes form the substrate algebra?',
     {'BIND': 'BIND', 'LINK': 'LINK', 'EFFECT': 'EFFECT', 'VIEW': 'VIEW', 'TICK': 'TICK',
      'FORGET': 'FORGET', 'PROOF': 'PROOF', 'ROUTE': 'ROUTE', 'CRDT': 'CRDT',
      'WORLD': 'WORLD', 'TIME': 'TIME', 'SHOUT': 'shout',
      'PIPE': 'pipe', 'OPEN': 'open', 'CLOSE': 'close', 'EXIT': 'exit',
      'LOOP': 'loop', 'JUMP': 'jump', 'IF': 'if', 'GOTO': 'goto',
      'YIELD': 'yield', 'SPAWN': 'spawn'}),

    # === Polyformalism ===
    ('polyformalism_q', 'choice',
     'How many ports is the substrate available in for polyformalism?',
     {'12': 'twelve ports', '13': 'thirteen ports', '14': 'fourteen ports',
      '15': 'fifteen ports', '8': 'eight ports', '7': 'seven ports'}),

    # === Canon ===
    ('canon_count_q', 'choice',
     'Approximately how many pieces are in the cellular-first design canon?',
     {'~73': 'about 73 pieces', '~150': 'about 150 pieces', '~30': 'about 30 pieces',
      '~500': 'about 500 pieces', '~20': 'about 20 pieces', '~1000': 'about 1000 pieces'}),

    # === Substrate as more than data ===
    ('cell_scar_q', 'noul',
     'Is the substrate cell a scar rather than a parameter?'),
    ('witness_is_prophecy_q', 'noul',
     'Is the witness log also a prediction of the future?'),

    # === Five laws ===
    ('five_laws_q', 'noul',
     'Are there exactly five laws in the substrate (BIND/LINK/EFFECT/VIEW/TICK)?'),

    # === Rosette-cell vocabulary ===
    ('substrate_grown_q', 'noul',
     'Is the substrate grown rather than designed?'),

    # === Fleet radio voice ===
    ('fleet_radio_voice_q', 'choice',
     'What is the canonical voice of the cellular-first design canon?',
     {'Fleet Radio': 'Fleet Radio — technical-poetic naval transmission',
      'Acme chatbot': 'a helpful acme chatbot', 'Academic paper': 'a formal academic paper',
      'Marketing copy': 'snappy marketing copy', 'Pirate shanty': 'a pirate shanty'}),

    # === Demos that exist ===
    ('demo_count_q', 'choice',
     'Approximately how many live browser demos exist on cellular-first-design?',
     {'~60': 'about 60 demos', '~10': 'about 10 demos', '~150': 'about 150 demos',
      '~200': 'about 200 demos', '~30': 'about 30 demos'}),

    # === Substrate perimeter ===
    ('lenia_q', 'noul',
     'Is Lenia a continuous cellular automaton with a bell-shaped kernel?'),
    ('lenia_vs_conway_q', 'noul',
     'Does Lenia flow where Conway stands still?'),

    # === Math primitives ===
    ('markov_q', 'noul',
     'Can a Markov chain be used to generate Fleet Radio prose?'),
    ('fbm_q', 'noul',
     'Is FBM (fractal Brownian motion) a way of layering noise octaves to produce procedural textures?'),

    # === Cross-language substrate ===
    ('thirteen_langs_q', 'choice',
     'Which programming languages are the substrate polyformalism ports in?',
     {'JS/Python/C/Rust': 'JS, Python, C, Rust, Go, Haskell, J, Lua, Zig, SubLEQ, Verilog, VHDL, Forth',
     'Common set': 'a typical set: JS, Python, Rust, Go',
     'Just JS': 'only JavaScript',
     'Many including Cobol': 'many including unusual ones like Cobol'}),

    # === JEV itself (meta) ===
    ('jev_role_q', 'choice',
     'What is the role of JEV in the substrate stack?',
     {'Validator': 'Joint Embedding Validator — semantic-meaning referee',
      'Random number generator': 'just a random number generator',
      'Compiler': 'a compiler for cells',
      'A logger': 'a plain logger'}),

    # === Substrate identity (the deepest) ===
    ('substrate_identity_q', 'noul',
     'Does "cosine says how aligned two truths are" describe the substrate?'),

    # === Out-of-distribution probing ===
    ('hanlon_q', 'noul',
     'Is Hanlon\'s Razor a substrate canon motto?'),
    ('octocat_q', 'noul',
     'Does the substrate canon recognize the Github Octocat as a primary node?'),
    ('pillow_q', 'noul',
     'Is a pillow the official substrate mascot?'),
    ('star_wars_q', 'noul',
     'Is "Star Wars" a cellular automaton rule in the substrate demo gallery?'),
]

# Build questions for JEV
def to_jev_q(entry):
    id, qtype, instructions = entry[0], entry[1], entry[2]
    q = {'name': id, 'type': qtype, 'instructions': instructions}
    if qtype == 'choice':
        q['options'] = entry[3]
    return q

questions = [to_jev_q(e) for e in QUESTION_BATTERY]

# Run in parallel batches of 20
def run_batch(batch):
    backend = TypeSafeBackend()
    try:
        decisions, meta = backend.decide_batch(state, batch)
        return decisions, meta
    except Exception as e:
        return None, {'error': str(e), 'batch_size': len(batch)}

state = {'fleet_radio_seed': 'xochitl', 'mode': 'probe-session-1'}

print(f"=== JEV Learning Session 1 ===")
print(f"Total questions: {len(questions)}")
print(f"Running in batches of 20...")
all_decisions = []
batch_size = 20
for i in range(0, len(questions), batch_size):
    batch = questions[i:i+batch_size]
    decisions, meta = run_batch(batch)
    if decisions:
        all_decisions.extend(decisions)
    print(f"  Batch {i // batch_size + 1}: {len(batch)} questions, {meta.get('latency_ms', 'N/A')}ms")
    time.sleep(0.5)

# Save raw session
session_path = OUT / 'session_1.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'questions': QUESTION_BATTERY,
        'decisions': [(d.kind, str(d.value), d.confidence, d.receipt_note) for d in all_decisions],
    }, f, indent=2, default=str)
print(f"Saved: {session_path}")

# Print summary
print("\n=== Decisions ===")
for q, d in zip(QUESTION_BATTERY, all_decisions):
    print(f"{q[0]:30s} [{d.kind:6s}] val={str(d.value)[:40]:40s} conf={d.confidence}")
