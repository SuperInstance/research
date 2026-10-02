#!/usr/bin/env python3
"""
Continuous JEV Probe — runs every 1 hour, asks 5 new probe questions,
saves results to /workspace/research/jev_sessions/continuous_*.json.

Use as: nohup python3 jev_continuous_probe.py > /tmp/jev_continuous.log 2>&1 &

Stops gracefully on SIGTERM.
"""
import os, sys, json, time, signal, random
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# All probe questions, organized by category
QUESTION_BANK = [
    # Bedrock doctrines
    ("canon", "Is the doctrine 'cells are scars, not parameters' canon?"),
    ("canon", "Is the doctrine 'the witness log is the prediction' canon?"),
    ("canon", "Is the doctrine 'the substrate is grown, not designed' canon?"),
    ("canon", "Is the doctrine 'Lenia flows where Conway stands still' canon?"),
    ("canon", "Is the doctrine 'the oracle is heard, not stored' canon?"),
    # Numerical facts
    ("numerical", "Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis?"),
    ("numerical", "Is xoshiro256** a 4-word state PRNG?"),
    ("numerical", "Is Box-Muller z = sqrt(-2 ln u1) cos(2 pi u2) correct?"),
    ("numerical", "Is cosine similarity (a . b) / (|a| |b|)?"),
    # Substrate size
    ("size", "Does the canonical substrate algebra have 11 opcodes?"),
    ("size", "Does the canonical substrate have 13 polyformalism ports?"),
    ("size", "Is the demo count at canonical around 60-65?"),
    # Inversions / adversarial
    ("adversarial", "Are cells parameters, not scars?"),
    ("adversarial", "Is the witness log past only (not prediction)?"),
    ("adversarial", "Is the substrate designed, not grown?"),
    # Speculative / signal-chain
    ("speculative", "Is JEV the synaptic spike between cells?"),
    ("speculative", "Is the signal-chain framing canonical?"),
    ("speculative", "Is 'chain speaks back' literal canon?"),
    # Cross-model
    ("cross", "Is substrate-canon validated by both JEV and writers' room?"),
    ("cross", "Does the canon require multi-LLM agreement for promotion?"),
    # Canon-vs-play
    ("canon", "Is this a canon-promotion gate, not a play gate?"),
    ("speculative", "Should speculative framings be parked until JEV p>0.7?"),
]

backend = TypeSafeBackend()
STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'Lenia flows where Conway stands still.',
            'The oracle is heard, not stored.',
        ],
    },
}

running = True
def stop(*_):
    global running
    running = False
signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

print(f"=== Continuous JEV Probe started at {time.strftime('%Y-%m-%dT%H:%M:%SZ')} ===")
print(f"Press Ctrl+C to stop. Probing every hour, 5 questions per round.\n")

round_num = 0
while running:
    round_num += 1
    sample = random.sample(QUESTION_BANK, 5)
    questions = [{'name': f'r{round_num}_q{i}', 'type': 'noul', 'instructions': q[1]} for i, q in enumerate(sample)]
    t0 = time.time()
    decisions, _ = backend.decide_batch(STATE, questions)
    dt = time.time() - t0

    results = []
    for q, d in zip(sample, decisions):
        results.append({'category': q[0], 'q': q[1], 'p': float(d.value), 'confidence': d.confidence})

    fname = f'/workspace/research/jev_sessions/continuous_r{round_num:03d}.json'
    with open(fname, 'w') as f:
        json.dump({
            'round': round_num,
            'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'questions': results,
            'latency_s': dt,
        }, f, indent=2)

    mean_p = sum(r['p'] for r in results) / len(results)
    print(f"[{time.strftime('%H:%M:%S')}] Round {round_num}: mean_p={mean_p:.3f}  ({dt:.1f}s)  saved to {fname}")
    for r in results:
        marker = '✓' if r['p'] >= 0.7 else ('?' if r['p'] >= 0.4 else '✗')
        print(f"  {marker} {r['category']:13s} {r['p']:.2f} — {r['q'][:80]}")

    # Sleep 1 hour
    for _ in range(3600):
        if not running: break
        time.sleep(1)

print(f"\n=== Continuous JEV Probe stopped at {time.strftime('%Y-%m-%dT%H:%M:%SZ')} after {round_num} rounds ===")
