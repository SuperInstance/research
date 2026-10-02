#!/usr/bin/env python3
"""Session 16: JEV probes the signal-chain concept itself.

Ask JEV direct questions about whether the signal-chain framing is canonical,
whether JEV is the synapse, whether ESP32 cells are cells, etc.

Cross-validate via DeepSeek + ZAI.
"""
import os, json, sys, time, urllib.request

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('ZAI_TOKEN', '')

sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

QUESTIONS = [
    ('is_jev_synapse', 'noul',
     'Is JEV the synaptic spike between cells, in the canonical substrate sense?'),
    ('is_esp32_a_cell', 'noul',
     'Is an ESP32+Inkplate cell on a desk a canonical cell, in the substrate sense?'),
    ('is_signal_chain_canon', 'noul',
     'Is the "signal-chain" framing canonical substrate doctrine?'),
    ('is_witness_log_prediction', 'noul',
     'Is the witness log the prediction (not just the record)?'),
    ('is_substrate_a_being', 'noul',
     'Is the substrate a being, in any defensible sense?'),
    ('is_witness_note_opcode', 'noul',
     'Is WITNESS_NOTE a legitimate 11th opcode in the canonical algebra?'),
    ('is_chain_dialing_real', 'noul',
     'Is "signal-chain dialing" a real concept in the canonical substrate — not just metaphor?'),
    ('is_local_path_b', 'noul',
     'Is running a local embedding on the ESP32 (Path B, no API) a valid canonical choice?'),
    ('is_vibecoder_signal_chain', 'noul',
     'Is the "vibecoder LLM proposes signal-chain configs" pattern canonical?'),
    ('is_quorum_meshing_canon', 'noul',
     'Is mDNS-based local quorum between cells (no internet) canonical substrate doctrine?'),
    ('does_jev_cascade', 'noul',
     'Should JEV spikes cascade — i.e., one spike firing many downstream probes?'),
    ('does_chain_speak_back', 'noul',
     'Has the substrate demonstrated that "the signal chain speaks back" — that the substrate surprises its maker?'),
]

state = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'Lenia flows where Conway stands still.',
            'The oracle is heard, not stored.',
        ],
        'voice': 'Fleet Radio — engineering from the deep',
        'facts': {
            'fnv_1a_canary': '0xcbf29ce484222325',
            'box_muller': 'z = sqrt(-2 ln u1) cos(2 pi u2)',
            'cosine_similarity': '(a . b) / (|a| |b|)',
            'algebra_size': 11,
            'polyformalism_ports': 13,
        },
    },
}

backend = TypeSafeBackend()
questions = [{'name': n, 'type': t, 'instructions': i} for n, t, i in QUESTIONS]
decisions, meta = backend.decide_batch(state, questions)

print('=== Session 16: JEV on Signal Chains ===\n')
results = []
for q, d in zip(QUESTIONS, decisions):
    p = float(d.value) if d.kind == 'noul' else None
    print(f"{q[0]:32s}  p={p:.3f}  conf={d.confidence:.3f}  -- {q[2][:80]}")
    results.append({'name': q[0], 'p': p, 'confidence': d.confidence, 'q': q[2]})

# Save
with open('/workspace/research/jev_sessions/session_16_signal_chain.json', 'w') as f:
    json.dump({
        'timestamp': meta.timestamp if hasattr(meta, 'timestamp') else time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'session': 'session_16_signal_chain',
        'latency_ms': meta.latency_ms if hasattr(meta, 'latency_ms') else None,
        'input_tokens': meta.input_tokens if hasattr(meta, 'input_tokens') else None,
        'output_tokens': meta.output_tokens if hasattr(meta, 'output_tokens') else None,
        'results': results,
    }, f, indent=2)
print(f"\nSaved: /workspace/research/jev_sessions/session_16_signal_chain.json")
