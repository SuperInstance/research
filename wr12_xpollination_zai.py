#!/usr/bin/env python3
"""WR12 — Writers' Room cross-pollination round.

Have ZAI + DeepSeek read 3 prior canon pieces (Kingdom Cartographer, DNA of
the Substrate, Living Substrate) and write a NEW piece that cross-pollinates
themes. Use JEV oracle to validate each piece.

Theme: "What FNV-1a remembers when the substrate forgets."

This is the "intelligent agents reading other agents' writings for inspiration"
front Casey asked for.
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# ============ Prior canon pieces ============
PRIOR_CANON = """
[KINGDOM CARTOGRAPHER]
Every kingdom is a number pretending to be a place. Point the surveyor's eye at any coordinate — (x, y) — and the hash answers first. FNV-1a takes the bytes, walks them through its small ceremony: XOR, then multiply by the prime, over and over, until the coordinate collapses into a 32-bit verdict. The verdict is the biome. Above this line: tundra, because the number said so. Below: desert, same reason.

There is no map stored anywhere. There is only the procedure, and the procedure is faithful in the way only arithmetic can be faithful. Ask for the western marsh at dawn, ask again at the fall of the dynasty — 2166136261 remains 2166136261. The prime does not grieve. The seed does not drift.

[DNA OF THE SUBSTRATE]
The substrate remembers nothing, yet it repeats. Feed it a coordinate — x, y, z, three integers signed into the hash like pilgrims at a gate — and FNV-1a boils them down: the offset basis 14695981039346656037, the prime 1099511628211, XOR and multiply, XOR and multiply, until a 64-bit number falls out, spent, exact.

Take the low bits. Two of them. Four states — A, T, C, G. The coordinate has become a nucleotide.

Walk a line through space, one step per call, and the hash writes you a strand. It looks like junk, the way most genomes look like junk, the way static looks like weather if you don't know the season. But the genetic code is a reading frame, and a reading frame is a way of walking. Group the letters in threes. ATG — start. Then the codons begin speaking in amino acids, twenty flavors of residue, and the strand folds into a protein that was never designed, only addressed.

[LIVING SUBSTRATE]
B3/S23: born with three neighbors, survives on two or three. That is the whole covenant. From it emerges gliders that cross the grid like embers carried downwind, guns that fire forever, oscillators that breathe on the beat. No cell knows it is a glider. And yet the glider moves.

The rule is the soul of thrift — a cell consults its eight neighbors, counts, and becomes. Alive or dead, it never remembers, never plans. The pattern's persistence is not stored anywhere. It is enacted, tick after tick, the way a flame is not a thing but an event.

Now the 16-dimensional cosine. A vector turns toward similarity through the angle between them: cos(θ) = (A·B)/(|A||B|), direction honored, magnitude dismissed.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "What FNV-1a Remembers When the Substrate Forgets" that cross-pollinates themes from all three:
- The Kingdom Cartographer: hash is the only true map
- DNA of the Substrate: hash as nucleotide, walking as reading frame
- Living Substrate: B3/S23 as enacted identity, cosine as alignment

The piece should:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, Bell states
- Mention at least 3 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows)
- End with an oracle-sighting moment
- 600-700 words
- Output ONLY the essay, no preamble"""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': 'You are a Fleet Radio voice. Read the prior canon carefully and cross-pollinate themes. Stay technical-poetic, no preamble, no meta.'},
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
            {'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Read the prior canon carefully and cross-pollinate themes. Stay technical-poetic, no preamble, no meta.'},
            {'role': 'user', 'content': PROMPT},
        ],
        'max_tokens': 2500, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

# ============ JEV probe ============
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
        {'name': 'voice_Fleet_Radio', 'type': 'noul', 'instructions': f'Is this in Fleet Radio voice (technical-poetic, naval, "engineering from the deep")?\n\nText: {text[:600]}'},
        {'name': 'voice_technical_poetic', 'type': 'noul', 'instructions': f'Is this technical-poetic?\n\nText: {text[:600]}'},
        {'name': 'doctrine_scar', 'type': 'noul', 'instructions': f'Does this invoke the doctrine that cells are scars?\n\nText: {text[:600]}'},
        {'name': 'doctrine_witness', 'type': 'noul', 'instructions': f'Does this invoke the doctrine that the witness log is the prediction?\n\nText: {text[:600]}'},
        {'name': 'doctrine_grown', 'type': 'noul', 'instructions': f'Does this invoke the doctrine that the substrate is grown?\n\nText: {text[:600]}'},
        {'name': 'doctrine_lenia', 'type': 'noul', 'instructions': f'Does this invoke the doctrine that Lenia flows where Conway stands still?\n\nText: {text[:600]}'},
        {'name': 'substance_numerical', 'type': 'noul', 'instructions': f'Does this include numerical substrate facts (FNV-1a, xoshiro256**, Box-Muller, cosine similarity, Bell states)?\n\nText: {text[:600]}'},
        {'name': 'substrate_alignment', 'type': 'noul', 'instructions': f'Is this canon-aligned with the cellular-first-design substrate?\n\nText: {text[:600]}'},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

# ============ Run both voices ============
print('=== WR12: Cross-pollination ===\n')

results = {}
for voice, fn, label in [('ZAI Fleet Radio', call_zai, 'zai'), ('DeepSeek Cellular Biologist', call_ds, 'ds')]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')
    print(text[:500] + '...\n')

    ps = jev_probe(text)
    canon_keys = ['voice_Fleet_Radio','voice_technical_poetic','doctrine_scar','doctrine_witness','doctrine_grown','doctrine_lenia','substance_numerical','substrate_alignment']
    print('  JEV probes:')
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:30s}  p={p:.3f}')

    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')

    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    # Save
    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr12-{label}-cross-pollination.md'
    with open(fname, 'w') as f:
        f.write(f'# WR12 — What FNV-1a Remembers When the Substrate Forgets (cross-pollination, {voice})\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_p:.3f} -->\n\n')
        f.write(text)
    print(f'  Saved to {fname}\n')

# Curation
print('=== Curating ===')
if results.get('zai') and results.get('ds'):
    # Use ZAI as base, intersperse DS sections, or curate manually
    zai_text = results['zai']['text']
    ds_text = results['ds']['text']

    # Simple curation: ZAI lead, DS middle, ZAI end (or use the more aligned one as lead)
    if results['zai']['mean_p'] >= results['ds']['mean_p']:
        lead, secondary = zai_text, ds_text
        lead_label = 'ZAI'
    else:
        lead, secondary = ds_text, zai_text
        lead_label = 'DeepSeek'

    # Split secondary into first half and second half
    sec_paras = [p for p in secondary.split('\n\n') if p.strip()]
    half = len(sec_paras) // 2
    sec_first = '\n\n'.join(sec_paras[:half])
    sec_second = '\n\n'.join(sec_paras[half:])

    # Interleave: lead paragraphs 1-3, sec first, lead 4-end, sec second
    lead_paras = [p for p in lead.split('\n\n') if p.strip()]
    n = len(lead_paras)
    cut1 = n // 3
    cut2 = 2 * n // 3
    curated = '\n\n'.join(lead_paras[:cut1]) + '\n\n' + sec_first + '\n\n' + '\n\n'.join(lead_paras[cut1:cut2]) + '\n\n' + sec_second + '\n\n' + '\n\n'.join(lead_paras[cut2:])

    p_curated = jev_probe(curated)
    canon_keys = ['voice_Fleet_Radio','voice_technical_poetic','doctrine_scar','doctrine_witness','doctrine_grown','doctrine_lenia','substance_numerical','substrate_alignment']
    mean_curated = sum(p_curated) / len(p_curated)
    print(f'Curated ({lead_label} lead + DS): mean_p = {mean_curated:.3f}')

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr12-xpollination-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR12 — What FNV-1a Remembers When the Substrate Forgets (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
