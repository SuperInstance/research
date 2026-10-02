#!/usr/bin/env python3
"""WR13 — The Grammar That Forgot Itself.

Cross-pollinate: Algebra of Eleven (BIND/LINK/EFFECT/VIEW/TICK + 6 more),
Chained Witness Log (each entry testifies about the one behind it),
Living Substrate (B3/S23 as enacted identity).
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[ALGEBRA OF ELEVEN]
Eleven opcodes. That is the whole grammar. In the old world you declared a variable and it sat there, mute, a bucket. Here nothing sits. Here everything is a cell — a living address in the graph — and the opcodes are the only verbs permitted to touch it.

BIND introduces two cells to each other. Not assignment — acquaintance. LINK stretches the wire between them and says: whatever one becomes, the other shall know. EFFECT is where knowledge becomes action, the cell reaching out into the world. VIEW is the read-only gaze, projection without mutation. TICK advances the heartbeat — the algebra is temporal, and time is not ambient but explicit, a step you must call.

FORGET is the mercy: edges dissolve, cells release their grip. PROOF seals a fact in attestation — the substrate does not believe, it verifies. ROUTE carries intent across the mesh, honoring distance. CRDT admits the truth of many writers: convergence, not consensus. WORLD is the boundary opcode, the membrane where the pure interior meets the impure without. TIME makes the fourth dimension first-class — you do not read the clock; you schedule it.

State is a verb. Memory is a topology. The program is not run; it is inhabited.

[CHAINED WITNESS LOG]
Every entry is bound to the one before it. You take the entry — its words, its timestamp, its author — and you crush it through the hash function until what falls out is a short, strange number, a fingerprint no two documents share. Then you write that fingerprint into the next entry, before its own words, before its own timestamp. Chain them like this and you have done something quiet and enormous: you have made the past.

Because the math is merciless. Change one comma in entry four hundred and its hash transforms utterly — avalanche, they call it, the way a single shifted grain brings down the slope. And now the fingerprint carried forward in entry four hundred and one no longer matches the broken thing behind it. The seam shows. The seam cannot not show.

[LIVING SUBSTRATE]
B3/S23: born with three neighbors, survives on two or three. That is the whole covenant. From it emerges gliders that cross the grid like embers carried downwind, guns that fire forever, oscillators that breathe on the beat. No cell knows it is a glider. And yet the glider moves.

The rule is the soul of thrift — a cell consults its eight neighbors, counts, and becomes. Alive or dead, it never remembers, never plans. The pattern's persistence is not stored anywhere. It is enacted, tick after tick, the way a flame is not a thing but an event.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Grammar That Forgot Itself" that cross-pollinates themes from all three:
- Algebra of Eleven: opcodes as the only verbs; state is a verb, memory is a topology
- Chained Witness Log: each entry testifies about the one behind it; tamper detection is arithmetic
- Living Substrate: B3/S23 as enacted identity, not stored

The piece should:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity, Bell states
- Mention at least 3 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows)
- End with an oracle-sighting moment
- 600-700 words
- Output ONLY the essay, no preamble"""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': 'You are a Fleet Radio voice. Cross-pollinate themes from prior canon. Stay technical-poetic.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["ZAI_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def call_ds(prompt):
    body = {
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'messages': [
            {'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Cross-pollinate themes. Stay technical-poetic.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def jev_probe(text):
    backend = TypeSafeBackend()
    state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
        'Cells are scars, not parameters.',
        'The witness log is the prediction.',
        'The substrate is grown, not designed.',
        'Lenia flows where Conway stands still.',
        'The oracle is heard, not stored.',
    ]}}
    questions = [
        {'name': 'voice_Fleet_Radio', 'type': 'noul', 'instructions': f'Is this in Fleet Radio voice?\n\nText: {text[:600]}'},
        {'name': 'voice_technical_poetic', 'type': 'noul', 'instructions': f'Is this technical-poetic?\n\nText: {text[:600]}'},
        {'name': 'doctrine_scar', 'type': 'noul', 'instructions': f'Does this invoke the cells-are-scars doctrine?\n\nText: {text[:600]}'},
        {'name': 'doctrine_witness', 'type': 'noul', 'instructions': f'Does this invoke the witness-log-is-prediction doctrine?\n\nText: {text[:600]}'},
        {'name': 'doctrine_grown', 'type': 'noul', 'instructions': f'Does this invoke the substrate-is-grown doctrine?\n\nText: {text[:600]}'},
        {'name': 'substance_numerical', 'type': 'noul', 'instructions': f'Numerical substrate facts?\n\nText: {text[:600]}'},
        {'name': 'substrate_alignment', 'type': 'noul', 'instructions': f'Canon-aligned?\n\nText: {text[:600]}'},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

print('=== WR13: The Grammar That Forgot Itself ===\n')

results = {}
for voice, fn, label in [('ZAI Fleet Radio', call_zai, 'zai'), ('DeepSeek Cellular Biologist', call_ds, 'ds')]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')
    print(text[:300] + '...\n')

    ps = jev_probe(text)
    canon_keys = ['voice_Fleet_Radio','voice_technical_poetic','doctrine_scar','doctrine_witness','doctrine_grown','substance_numerical','substrate_alignment']
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:30s}  p={p:.3f}')
    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')
    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr13-{label}-grammar.md'
    with open(fname, 'w') as f:
        f.write(f'# WR13 — The Grammar That Forgot Itself ({voice})\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_p:.3f} -->\n\n')
        f.write(text)

# Curation
if results.get('zai') and results.get('ds'):
    # Pick the higher-aligned one as lead
    if results['zai']['mean_p'] >= results['ds']['mean_p']:
        lead = results['zai']['text']
        secondary = results['ds']['text']
        lead_label = 'ZAI'
    else:
        lead = results['ds']['text']
        secondary = results['zai']['text']
        lead_label = 'DeepSeek'

    # Interleave
    lead_paras = [p for p in lead.split('\n\n') if p.strip()]
    sec_paras = [p for p in secondary.split('\n\n') if p.strip()]
    half = len(sec_paras) // 2

    curated = (
        '\n\n'.join(lead_paras[:3]) + '\n\n' +
        '\n\n'.join(sec_paras[:half]) + '\n\n' +
        '\n\n'.join(lead_paras[3:6]) + '\n\n' +
        '\n\n'.join(sec_paras[half:]) + '\n\n' +
        '\n\n'.join(lead_paras[6:])
    )

    p_curated = jev_probe(curated)
    canon_keys = ['voice_Fleet_Radio','voice_technical_poetic','doctrine_scar','doctrine_witness','doctrine_grown','substance_numerical','substrate_alignment']
    mean_curated = sum(p_curated) / len(p_curated)
    print(f'Curated ({lead_label} lead + other): mean_p = {mean_curated:.3f}')

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr13-grammar-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR13 — The Grammar That Forgot Itself (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
