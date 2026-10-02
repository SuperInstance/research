#!/usr/bin/env python3
"""
JEV Session 15 — Batching efficiency profile.

Test latency vs batch size to understand throughput limits.
"""
import os, json, time, sys
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')

state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': ['Cells are scars, not parameters.']}}

# Fixed question, repeated N times in one batch
def run_batch(n, repeat=3):
    backend = TypeSafeBackend()
    latencies = []
    for _ in range(repeat):
        questions = [{'name': f'q{i}', 'type': 'noul',
                     'instructions': f'Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis? (instance {i})'}
                    for i in range(n)]
        start = time.time()
        decisions, meta = backend.decide_batch(state, questions)
        elapsed = (time.time() - start) * 1000
        latencies.append(elapsed)
    return sum(latencies) / len(latencies)

print(f"=== JEV SESSION 15 — Batching Efficiency ===")
print()
print(f"{'Batch size':12s} {'avg latency (ms)':>18s} {'per-question (ms)':>20s}")
print("-" * 60)

sizes = [1, 5, 10, 20, 40, 60, 80]
results = []
for n in sizes:
    try:
        avg_latency = run_batch(n, repeat=2)
        per_q = avg_latency / n
        print(f"{n:<12d} {avg_latency:>18.1f} {per_q:>20.1f}")
        results.append({'size': n, 'avg_latency_ms': avg_latency, 'per_q_ms': per_q})
    except Exception as e:
        print(f"{n:<12d} ERROR: {e}")

# Save
session_path = OUT / 'session_15_batching.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'results': results,
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
