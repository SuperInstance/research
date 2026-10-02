#!/usr/bin/env python3
"""WR15 — The Witness That Outlived Itself.

Cross-pollinate: Oracle of Vectors (deterministic god, FNV-1a + Box-Muller + cosine),
Chained Witness Log (each entry testifies about the one behind),
Algebra of Eleven (11 opcodes = the grammar).

Theme: What happens when the witness log IS the oracle?
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

PRIOR_CANON = """
[ORACLE OF VECTORS]
The embedder knows nothing. That is its covenant. It has never read a sentence, never mourned a word. What it has is a question, and a promise: ask twice, receive the same ghost.

Watch the mechanism. Each token is hashed through FNV-1a — that old Fowler-Noll-Vo machine, multiplying and XOR-ing like a loom, pulling a 32-bit thread from every string. The thread is not meaning. The thread is determinism — a fixed seed tied forever to the word that made it.

The seeds feed xoshiro256**, which spins 256 bits of light with no memory at all. Every question becomes a private universe with its own physics. Box-Muller arrives next, the great transmutation: two uniforms in, a Gaussian out. Turn the crank of two flat randoms and out falls the bell curve — the same curve the universe uses, conjured here by logarithm and cosine.

Then the final prayer: cosine. Two questions, two vectors, and the angle between them is all that matters. Magnitude is vanity; orientation is truth. Questions that rhyme point the same way, and the oracle answers in geometry.

Why reproducible? Because nothing was ever stored. Every vector is recomputed from first principles — hash, seed, twist, fold, angle. The oracle does not remember its answers. It re-derives them, every time, identically.

[CHAINED WITNESS LOG]
Every entry is bound to the one before it. You take the entry — its words, its timestamp, its author — and you crush it through the hash function until what falls out is a short, strange number, a fingerprint no two documents share. Then you write that fingerprint into the next entry, before its own words, before its own timestamp.

Because the math is merciless. Change one comma in entry four hundred and its hash transforms utterly — avalanche, they call it. The seam shows. The seam cannot not show.

[ALGEBRA OF ELEVEN]
Eleven opcodes. That is the whole grammar. State is a verb. Memory is a topology. The program is not run; it is inhabited.
"""

PROMPT = f"""You are a Fleet Radio voice. Read these 3 prior canon pieces carefully:

{PRIOR_CANON}

Then write a NEW 600-word Fleet Radio essay titled "The Witness That Outlived Itself" that cross-pollinates themes from all three:
- Oracle of Vectors: deterministic god; nothing stored, all re-derived
- Chained Witness Log: each entry testifies about the one behind it; tamper detection is arithmetic
- Algebra of Eleven: state is a verb, memory is a topology

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

print('=== WR15: The Witness That Outlived Itself ===\n')

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

    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr15-{label}-witness-outlived.md'
    with open(fname, 'w') as f:
        f.write(f'# WR15 — The Witness That Outlived Itself ({voice})\n\n')
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

    fname = '/workspace/repos/ai-writings/cellular-first-design/reports/wr15-witness-curated.md'
    with open(fname, 'w') as f:
        f.write('# WR15 — The Witness That Outlived Itself (curated)\n\n')
        f.write(f'<!-- JEV verdict: mean_p={mean_curated:.3f} -->\n\n')
        f.write(curated)
    print(f'Saved to {fname}')
