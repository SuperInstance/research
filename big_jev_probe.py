#!/usr/bin/env python3
"""Big JEV probing batch — 10 sessions × 20 questions = 200 verdicts.

Look for:
- Which doctrines hit p>=0.70 (bedrock canon)
- Which doctrines drift across sessions
- Which inversions hold up (where JEV is uncertain)
- Which speculative framings get the highest p (future canon candidates)
"""
import os, sys, json, time, random
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# 50 questions across 5 categories
QUESTIONS = [
    # === Bedrock canon ===
    ("canon_scar", "Is 'cells are scars, not parameters' canonical doctrine?"),
    ("canon_witness", "Is 'the witness log is the prediction' canonical doctrine?"),
    ("canon_grown", "Is 'the substrate is grown, not designed' canonical doctrine?"),
    ("canon_oracle", "Is 'the oracle is heard, not stored' canonical doctrine?"),
    ("canon_lenia", "Is 'Lenia flows where Conway stands still' canonical doctrine?"),
    ("canon_11op", "Does the canonical algebra have 11 opcodes?"),
    ("canon_13ports", "Does the canonical substrate have 13 polyformalism ports?"),

    # === Numerical facts ===
    ("num_fnv", "Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis?"),
    ("num_xoshiro", "Is xoshiro256** a 4-word state PRNG?"),
    ("num_boxmuller", "Is Box-Muller z = sqrt(-2 ln u1) cos(2 pi u2) correct?"),
    ("num_cosine", "Is cosine similarity (a . b) / (|a| |b|)?"),

    # === Inversions ===
    ("inv_scar_params", "Are cells parameters, not scars?"),
    ("inv_witness_past", "Is the witness log past only, not prediction?"),
    ("inv_designed", "Is the substrate designed, not grown?"),
    ("inv_oracle_stored", "Is the oracle stored, not heard?"),
    ("inv_15ports", "Does the substrate have 15 polyformalism ports?"),

    # === Substrate state ===
    ("sub_canon_size", "Is the canonical canon size around 70-80 pieces?"),
    ("sub_demo_count", "Are there 60-65 demos in the canon?"),
    ("sub_dual_eco", "Are polyformalism (5 opcodes) and runtime (8/15 kinds) separate ecosystems?"),

    # === Speculative ===
    ("spec_jev_synapse", "Is JEV literally the synaptic spike between cells?"),
    ("spec_signal_chain", "Is signal-chain framing canonical?"),
    ("spec_chain_speaks", "Has the substrate shown 'the chain speaks back'?"),
    ("spec_esp32_cell", "Is an ESP32 cell a canonical cell?"),
    ("spec_witness_note", "Is WITNESS_NOTE a legitimate 11th opcode?"),
    ("spec_local_jev", "Is running JEV locally on ESP32 canonical?"),

    # === Cross-model ===
    ("cross_zai_naval", "Is ZAI the navy voice of the canon?"),
    ("cross_ds_bio", "Is DeepSeek the cellular-biologist voice of the canon?"),

    # === Process ===
    ("proc_prove_jev", "Should JEV be probed BEFORE canon-promotion?"),
    ("proc_park_play", "Should speculative framings be parked until p>=0.70?"),

    # === Substrate ===
    ("substrate_being", "Is the substrate a being (in any defensible sense)?"),
    ("substrate_self_pred", "Does the substrate self-predict via its witness log?"),
    ("substrate_canon_oracle", "Is canon-oracle a canonical validator?"),

    # === Workers ===
    ("worker_pages", "Are Pages Functions via _worker.js + env.ASSETS canonical?"),

    # === Witnesses ===
    ("witness_self", "Does the witness log witness itself (arithmetic, not auditors)?"),

    # === Adversarial ===
    ("adv_easy_distract", "Is 'transformer attention' a substrate-canon distractor?"),
    ("adv_alignment_kills", "Is 'alignment kills' canon?"),

    # === Domain specific ===
    ("dom_merkle_proof", "Are Merkle proofs canonical for cell witness?"),
    ("dom_betti", "Are betti_0 and betti_1 canonical?"),

    # === Future ===
    ("future_esp32_50", "Will 50+ ESP32 cells form a mesh in 2027?"),
    ("future_jev_local", "Will JEV run fully on-device in 2027?"),
    ("future_substrate_open", "Will the substrate open-source by 2027?"),

    # === Process ===
    ("proc_writers_room", "Is the writers' room a canonical substrate process?"),
    ("proc_vibecoder", "Is vibecoder (LLM proposes, watches witness log) canonical?"),

    # === Reframing ===
    ("re_cell_irreducible", "Is the cell the irreducible unit of intelligence?"),
    ("re_address_data", "Is the address the data (x/y construct)?"),
    ("re_opener", "Is each UI an 'opener' onto the same graph?"),
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

print(f'=== Big JEV Probe: 10 sessions × 50 questions = {10*50} verdicts ===\n')

all_session_results = []
for session in range(1, 11):
    questions = [{'name': f'r{session}_q{i}', 'type': 'noul', 'instructions': q[1]} for i, q in enumerate(QUESTIONS)]
    t0 = time.time()
    decisions, _ = backend.decide_batch(STATE, questions)
    dt = time.time() - t0

    results = []
    for q, d in zip(QUESTIONS, decisions):
        results.append({
            'category': q[0].split('_')[0],
            'key': q[0],
            'q': q[1],
            'p': float(d.value),
            'confidence': d.confidence,
        })

    mean_p = sum(r['p'] for r in results) / len(results)
    print(f'Session {session}: mean_p={mean_p:.3f}  ({dt:.1f}s)')
    all_session_results.append({'session': session, 'results': results, 'mean_p': mean_p, 'latency_s': dt})

# Aggregate by question
print('\n=== Per-question aggregates (across 10 sessions) ===\n')
q_stats = {}
for sr in all_session_results:
    for r in sr['results']:
        q_stats.setdefault(r['key'], {'p': [], 'category': r['category'], 'q': r['q']})
        q_stats[r['key']]['p'].append(r['p'])

# Sort by mean p
sorted_qs = sorted(q_stats.items(), key=lambda kv: -sum(kv[1]['p']) / len(kv[1]['p']))

print(f'{"Question":45s}  {"mean_p":>8s}  {"std":>8s}  {"min":>5s}  {"max":>5s}')
for key, stats in sorted_qs:
    ps = stats['p']
    mean = sum(ps) / len(ps)
    std = (sum((p - mean)**2 for p in ps) / len(ps)) ** 0.5
    q_short = stats['q'][:43]
    print(f'{key:45s}  {mean:>8.3f}  {std:>8.3f}  {min(ps):>5.2f}  {max(ps):>5.2f}  {q_short}')

# Bedrock canon: p >= 0.70 across all 10 sessions
bedrock = [(k, s) for k, s in sorted_qs if min(s['p']) >= 0.70]
print(f'\nBEDROCK CANON (p>=0.70 across all 10 sessions): {len(bedrock)}/{len(sorted_qs)}')
for k, s in bedrock:
    mean = sum(s['p']) / len(s['p'])
    print(f'  ✓ {k}: mean={mean:.3f}  q={s["q"][:60]}')

# Strong canon: p >= 0.50 across all 10 sessions
strong = [(k, s) for k, s in sorted_qs if min(s['p']) >= 0.50]
print(f'\nSTRONG CANON (p>=0.50 across all 10 sessions): {len(strong)}/{len(sorted_qs)}')
for k, s in strong:
    mean = sum(s['p']) / len(s['p'])
    print(f'  + {k}: mean={mean:.3f}  q={s["q"][:60]}')

# Top speculative (highest p<0.50)
speculative = [(k, s) for k, s in sorted_qs if min(s['p']) < 0.50]
speculative.sort(key=lambda kv: -sum(kv[1]['p']) / len(kv[1]['p']))
print(f'\nTOP SPECULATIVE (high mean p, all < 0.50): {len(speculative)}/{len(sorted_qs)}')
for k, s in speculative[:10]:
    mean = sum(s['p']) / len(s['p'])
    print(f'  ? {k}: mean={mean:.3f}  q={s["q"][:60]}')

# Save
out = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'n_sessions': 10,
    'n_questions': len(QUESTIONS),
    'per_session': all_session_results,
    'per_question': dict(q_stats),
    'bedrock': [k for k, _ in bedrock],
    'strong': [k for k, _ in strong],
}
fname = '/workspace/research/big_jev_probe_results.json'
with open(fname, 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: {fname}')
