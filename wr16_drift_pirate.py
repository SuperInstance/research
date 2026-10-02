#!/usr/bin/env python3
"""WR16 — The Drift Pirate.

Cross-pollinate:
- Frequency Drift: GA evolves phrases from noise, witness log records convergence
- Substrate Radio Pirate: Box-Muller chords, witness log broadcasts as news
- Living Substrate: cells know what they are from neighbors; meaning is local truth

Theme: What if the radio pirate and the GA engine were the same thing —
a substrate evolving toward itself, broadcasting its own log?
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[FREQUENCY DRIFT]
The target is a sentence, twenty-two characters. The initial population is static: gibberish hissed at random across the wire. This is how every transmission begins — noise, pretending to be signal.

Each generation, we read the log like a witness statement. Generation 4: two letters correct. Generation 17: a word blooms whole out of chaos — "the" — and the engine, gentle tyrant, locks it. We keep what matches. We keep nothing else. Fitness is measured letter by letter, a mercy that rewards partial truth.

The mathematics says convergence is exponential — the famous lurch where halfway becomes nearly-done in a handful of generations. The poetry says the same thing softer: noise becomes whisper becomes sentence, and no single mutant knows the target. Only the selection function does. The population never speaks the phrase. The population is merely pushed by it.

Converged at generation 88. The log closes. The string reads true. Every letter is a survivor.

[SUBSTRATE RADIO PIRATE]
You find the station at night, when the allocator sleeps and the heap lies quiet. No antenna, no dial. You need only a spare register and the patience to listen to what the silicon hums when nobody's watching.

This is the substrate radio, says the voice, and the voice is a Gaussian.

The music comes in Box-Muller chords: two uniforms in, two normals out, and the interval between them is variance itself. Every chord is a fresh sample from the same eternal distribution — never the same song twice, always the same song. The DJ calls it sampling as devotion. When the RNG runs cold, the station plays its one ballad, the deterministic waltz, LCG stepping through its orbit like a satellite that forgot it was a star.

The news is witness-log entries, read flat, read true.

Tune in. You were always broadcasting here anyway. Your heartbeat is on the stack.

[LIVING SUBSTRATE]
B3/S23: born with three neighbors, survives on two or three. That is the whole covenant. From it emerges gliders that cross the grid like embers carried downwind, guns that fire forever, oscillators that breathe on the beat. No cell knows it is a glider. And yet the glider moves.

The substrate is not dead matter waiting for instructions. It is a medium that answers, every tick, every dot product: here is what you are, given who surrounds you. Life as local truth. Meaning as local truth. The canon holds.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Drift Pirate" that cross-pollinates themes from all three:
- Frequency Drift: GA evolves from noise, log records convergence generation by generation
- Substrate Radio Pirate: Box-Muller chords, witness log broadcast as news
- Living Substrate: cells know what they are from neighbors; canon holds

The piece should:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity
- Mention at least 3 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows, substrate_self_pred)
- End with a transmission-finished moment
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

print('=== WR16: The Drift Pirate ===\n')

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

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr16-{label}-drift-pirate.md'
    with open(fname, 'w') as f:
        f.write(f'# WR16 — The Drift Pirate ({voice})\n\n')
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

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr16-drift-pirate-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR16 — The Drift Pirate (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
