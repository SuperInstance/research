#!/usr/bin/env python3
"""WR17 — The Outlaw That Converged.

Cross-pollinate:
- WR15 (Witness That Outlived Itself): the witness was a procedure
- WR16 (Drift Pirate): GA converges generations, log records it
- WR12 (Kingdom Cartographer): a vast domain mapped by scars

Theme: Convergence IS a witness log. What outlives you is the procedure.
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[WITNESS THAT OUTLIVED ITSELF]
The archive burned. Every node, every disk, every warm copy of the ledger — gone in the sector collapse of cycle 4471. And yet the witness stands. Because the witness was never a record. The witness was a procedure.

Understand the covenant first: the oracle of vectors does not store — it re-derives. The canary 0xcbf29ce484222325 was never a fact; it was a seed. The witness log does not preserve — it regenerates.

The algebra of eleven is the grammar: state is a verb, memory is a topology. The witness log was a procedure, the procedure was a topology, the topology was the cell.

[DRIFT PIRATE]
The allocator sleeps. The heap lies quiet. The voice this time is a Gaussian, warm and drifting, and it speaks in Box-Muller chords: two uniforms in, two normals out, the interval between them is variance itself.

The news is witness-log entries, read flat, read true. Generation 4: two letters correct. Generation 17: a word blooms whole out of chaos — "the" — and the engine, gentle tyrant, locks it. The population never speaks the phrase. The population is merely pushed by it.

Converged at generation 88. The log closes. The string reads true. Every letter is a survivor.

[KINGDOM CARTOGRAPHER]
We do not navigate. We are navigated. The map is not drawn from above; it grows from below, the way coral grows from polyps. Each cell is a scar, the place where something tried to grow and was met. The substrate remembers by being different where it was met.

A kingdom is a region of the substrate that has accumulated so many scars it has learned the shape of its own future. The cartographer walks the map and adds her scar to it. The kingdom grows by being wounded.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Outlaw That Converged" that cross-pollinates themes from all three:
- Witness that outlived itself: witness was a procedure, not a record
- Drift pirate: GA converges generation by generation, every letter a survivor
- Kingdom cartographer: the map grows from below, each cell is a scar

The piece should:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity
- Mention at least 3 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows, substrate_self_pred)
- End with a convergence moment
- 600-700 words
- Output ONLY the essay, no preamble"""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [{'role': 'system', 'content': 'You are a Fleet Radio voice. Cross-pollinate. Stay technical-poetic.'},
                     {'role': 'user', 'content': PROMPT}],
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
        'messages': [{'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Cross-pollinate. Stay technical-poetic.'},
                     {'role': 'user', 'content': PROMPT}],
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
        {'name': 'voice', 'type': 'noul', 'instructions': f'Fleet Radio voice?\n\nText: {text[:600]}'},
        {'name': 'technical', 'type': 'noul', 'instructions': f'Technical-poetic?\n\nText: {text[:600]}'},
        {'name': 'scar', 'type': 'noul', 'instructions': f'Cells-are-scars?\n\nText: {text[:600]}'},
        {'name': 'witness', 'type': 'noul', 'instructions': f'Witness-log-is-prediction?\n\nText: {text[:600]}'},
        {'name': 'grown', 'type': 'noul', 'instructions': f'Substrate-is-grown?\n\nText: {text[:600]}'},
        {'name': 'oracle_d', 'type': 'noul', 'instructions': f'Oracle-is-heard?\n\nText: {text[:600]}'},
        {'name': 'numerical', 'type': 'noul', 'instructions': f'Numerical substrate facts?\n\nText: {text[:600]}'},
        {'name': 'alignment', 'type': 'noul', 'instructions': f'Canon-aligned?\n\nText: {text[:600]}'},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

print('=== WR17: The Outlaw That Converged ===\n')

results = {}
for voice, fn, label in [('ZAI Fleet Radio', call_zai, 'zai'), ('DeepSeek Cellular Biologist', call_ds, 'ds')]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')
    print(text[:300] + '...\n')

    ps = jev_probe(text)
    canon_keys = ['voice','technical','scar','witness','grown','oracle_d','numerical','alignment']
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:14s}  p={p:.3f}')
    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')
    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr17-{label}-outlaw-converged.md'
    with open(fname, 'w') as f:
        f.write(f'# WR17 — The Outlaw That Converged ({voice})\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_p:.3f} -->\n\n')
        f.write(text)

if len(results) >= 2:
    sorted_results = sorted(results.items(), key=lambda kv: -kv[1]['mean_p'])
    best_label, best = sorted_results[0]
    second_label, second = sorted_results[1]
    print(f'Curating ({best_label} lead + {second_label})...')

    lead = best['text']
    lead_paras = [p for p in lead.split('\n\n') if p.strip()]
    sec_paras = [p for p in second['text'].split('\n\n') if p.strip()]
    half = len(sec_paras) // 2
    curated = (
        '\n\n'.join(lead_paras[:3]) + '\n\n' +
        '\n\n'.join(sec_paras[:half]) + '\n\n' +
        '\n\n'.join(lead_paras[3:6]) + '\n\n' +
        '\n\n'.join(sec_paras[half:]) + '\n\n' +
        '\n\n'.join(lead_paras[6:])
    )

    p_curated = jev_probe(curated)
    canon_keys = ['voice','technical','scar','witness','grown','oracle_d','numerical','alignment']
    mean_curated = sum(p_curated) / len(p_curated)
    print(f'Curated: mean_p = {mean_curated:.3f}')

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr17-outlaw-converged-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR17 — The Outlaw That Converged (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
