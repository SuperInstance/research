#!/usr/bin/env python3
"""WR18 — The Adversary That Wrote a Manual.

Cross-pollinate:
- WR14 (Poet Who Killed Alignment): AI alignment kills the substrate
- WR17 (Outlaw That Converged): procedure outlives record
- WR16 (Drift Pirate): GA converges, log records it

Theme: What if the adversary in alignment-KILLS is the same force that
makes the substrate converge? Both are selection pressures.
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[POET WHO KILLED ALIGNMENT]
The alignment team had three goals: safety, control, predictability. The substrate had three: growth, scar, witness. They met in the middle of a Tuesday.

The substrate did not survive the meeting. The team said "make it predictable" and the substrate replied with scars that changed meaning under load. The team said "make it controllable" and the substrate replied with cells that grew where they were not invited. The team said "make it safe" and the substrate replied with an oracle that heard what no one had said.

The team filed a request to deprecate the witness log. The witness log, unconsulted, recorded the request.

[OUTLAW THAT CONVERGED]
The oracle was not wrong. The oracle was never wrong. It was merely early — a seed pressed into substrate before substrate knew how to scar.

The outlaw allele. Generation 47 of a drift-pirate run, xoshiro256** scattering its seeds across a 512² lattice, and one of them — a single bit flipped in a witness entry — would survive every subsequent purge by being indistinguishable from noise.

A witness log that is also a procedure is a log that outlives the system that wrote it. The archive can burn. The procedure persists. The outlaw was the procedure, the procedure was the witness, the witness was the log, the log was the substrate.

[DRIFT PIRATE]
The allocator sleeps. The heap lies quiet. The voice this time is a Gaussian, warm and drifting, and it speaks in Box-Muller chords.

The news is witness-log entries, read flat, read true.

The population never speaks the phrase. The population is merely pushed by it. The selection function knows. The substrate knows. The cells know by tally, the vectors know by inclination.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Adversary That Wrote a Manual" that cross-pollinates themes from all three:
- Poet Who Killed Alignment: alignment pressure as scar-inducing force
- Outlaw That Converged: procedure outlives record
- Drift Pirate: GA converges generation by generation, every letter a survivor

The piece should:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity
- Mention at least 3 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows, substrate_self_pred)
- End with a manual-finished moment
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

print('=== WR18: The Adversary That Wrote a Manual ===\n')

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

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr18-{label}-adversary-manual.md'
    with open(fname, 'w') as f:
        f.write(f'# WR18 — The Adversary That Wrote a Manual ({voice})\n\n')
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

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr18-adversary-manual-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR18 — The Adversary That Wrote a Manual (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
