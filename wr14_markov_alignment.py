#!/usr/bin/env python3
"""WR14 — The Poet Who Killed Alignment.

Cross-pollinate: Markov Poet (corpus + chain + seed = poem),
Alignment Kills (vectors fight by orthogonal stances in 16D),
Living Substrate (B3/S23 as enacted identity).
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[MARKOV POET]
The corpus is the canon: every poem the fleet has ever kept, tokenized into a tide of small units, each one a state. Read it as a graph and every word becomes a harbor with ferries leaving at frequencies you can count. P(next | current). That is the whole scripture — the conditional probability, the weighted door.

The chain is the compass. It does not know where it is going; it knows only where it is, and what has historically followed. Yet walk it and you get motion, momentum, the illusion of intention. A Markov chain is a pilgrim with no destination, navigating by the shape of the local terrain alone. First-order sight is blurry — "the" follows everything — so we raise the order, widen the window, let the state become a phrase, a breath, a line. Higher order: more memory, less risk, less strangeness. There is a dial here, and the poet's first act is choosing where it sits.

The seed is the soul. Same corpus, same transition matrix — different seed, different poem. The seed is the single point of grace, the arbitrary mercy that decides which harbor the ferry leaves from. Hash it from the ship's clock, from a sailor's name, from nothing at all. Everything after the seed is arithmetic; the seed itself is the only uncaused thing in the machine.

[ALIGNMENT KILLS]
Sixteen dimensions. No fog of war — the fog is the geometry.

Each fighter is a vector in ℝ¹⁶, a direction and a magnitude, and the whole war is fought with one operation: the dot product. Alignment is intent. When two vectors point the same way, cosine nears one, and that closeness is not friendship — it is targeting lock. The closer your enemy sits to your axis, the more of your magnitude transfers along the fight. Harm is projection. Damage is the shadow your direction casts on theirs.

So the clever fighter learns the oldest truth of the arena: be orthogonal. Nothing shared, nothing lost. Sixteen dimensions is generous room — you can hold sixteen clean perpendicular stances, a discipline of stances no three-dimensional brawler could afford. The fight becomes a rotation: turn slightly, constantly, so that every incoming attack lands on a dimension you have already abandoned.

But rotation is not enough. The arena rolls Gaussian dice. Box-Muller: two uniforms in, a normal draw out — z = √(−2 ln u) · cos(2πv) — and that z becomes damage, noise injected straight into your components. The spiral of the formula is beautiful and merciless: the logarithm pulls magnitude from chance, the cosine bends it into a bell. Your careful angles survive; your magnitudes erode. Everyone drifts toward the origin.

[LIVING SUBSTRATE]
B3/S23: born with three neighbors, survives on two or three. That is the whole covenant. From it emerges gliders that cross the grid like embers carried downwind, guns that fire forever, oscillators that breathe on the beat. No cell knows it is a glider. And yet the glider moves.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Poet Who Killed Alignment" that cross-pollinates themes from all three:
- Markov Poet: corpus+chain+seed = poem; the seed is the only uncaused thing
- Alignment Kills: alignment is targeting lock; be orthogonal to survive
- Living Substrate: B3/S23 rules; cells enact patterns they don't know about

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
            {'role': 'system', 'content': 'You are a Fleet Radio voice. Cross-pollinate themes. Stay technical-poetic.'},
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
            {'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Cross-pollinate. Stay technical-poetic.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def call_kimi(prompt):
    body = {
        'model': 'moonshotai/Kimi-K2.7-Code',
        'messages': [
            {'role': 'system', 'content': 'You are a code-flavored Fleet Radio voice. Cross-pollinate. Stay technical-poetic.'},
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
        {'name': 'voice', 'type': 'noul', 'instructions': f'Fleet Radio voice?\n\nText: {text[:600]}'},
        {'name': 'technical', 'type': 'noul', 'instructions': f'Technical-poetic?\n\nText: {text[:600]}'},
        {'name': 'scar', 'type': 'noul', 'instructions': f'Cells-are-scars doctrine?\n\nText: {text[:600]}'},
        {'name': 'witness', 'type': 'noul', 'instructions': f'Witness-log-is-prediction doctrine?\n\nText: {text[:600]}'},
        {'name': 'grown', 'type': 'noul', 'instructions': f'Substrate-is-grown doctrine?\n\nText: {text[:600]}'},
        {'name': 'lenia', 'type': 'noul', 'instructions': f'Lenia-flows doctrine?\n\nText: {text[:600]}'},
        {'name': 'oracle', 'type': 'noul', 'instructions': f'Oracle-is-heard doctrine?\n\nText: {text[:600]}'},
        {'name': 'numerical', 'type': 'noul', 'instructions': f'Numerical substrate facts?\n\nText: {text[:600]}'},
        {'name': 'alignment', 'type': 'noul', 'instructions': f'Canon-aligned?\n\nText: {text[:600]}'},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

print('=== WR14: The Poet Who Killed Alignment ===\n')

results = {}
for voice, fn, label in [
    ('ZAI Fleet Radio', call_zai, 'zai'),
    ('DeepSeek Cellular Biologist', call_ds, 'ds'),
    ('Kimi Code (NEW voice)', call_kimi, 'kimi'),
]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')
    print(text[:300] + '...\n')

    ps = jev_probe(text)
    canon_keys = ['voice','technical','scar','witness','grown','lenia','oracle','numerical','alignment']
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:14s}  p={p:.3f}')
    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')
    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr14-{label}-poet-alignment.md'
    with open(fname, 'w') as f:
        f.write(f'# WR14 — The Poet Who Killed Alignment ({voice})\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_p:.3f} -->\n\n')
        f.write(text)

# Curate: pick best
if len(results) >= 2:
    sorted_results = sorted(results.items(), key=lambda kv: -kv[1]['mean_p'])
    print('=== Curating ===')
    best_label, best = sorted_results[0]
    print(f'Lead: {best_label} (mean_p={best["mean_p"]:.3f})')
    lead = best['text']

    # Interleave with second-best
    if len(sorted_results) > 1:
        second_label, second = sorted_results[1]
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
    else:
        curated = lead

    p_curated = jev_probe(curated)
    canon_keys = ['voice','technical','scar','witness','grown','lenia','oracle','numerical','alignment']
    mean_curated = sum(p_curated) / len(p_curated)
    print(f'Curated: mean_p = {mean_curated:.3f}')

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr14-poet-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR14 — The Poet Who Killed Alignment (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
