#!/usr/bin/env python3
"""WR20 — Ten Archetypes, Ten Pieces.

Cross-pollinate the 10 aesop-mcp archetypes into Fleet Radio canon pieces.
Each archetype gets its own ~400-word piece. The piece must:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity
- Mention at least 3 canonical doctrines
- 400-500 words each (short, punchy)
- End with a doctrine-resonant moment

Theme: What if the substrate's constraint dynamics WERE the fables?
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

ARCHETYPES = [
    ("icarus", "Wax and Wings", "Over-constrained system that melts. The constraint graph had everything it needed for flight — except a temperature limit."),
    ("sisyphus", "The Push", "Cycle that can't flatten. The mountain's constraint graph has no flat path. Change the graph, not the push."),
    ("tower_of_babel", "The Confused Tongues", "Consensus fails at protocol layer. Local sections stopped gluing together; sheaf H1 became non-zero."),
    ("phoenix", "The Ash Algorithm", "Collapse WAS the consensus event. The deconfined phase collapsed into the confined phase. The system couldn't grow without first burning."),
    ("theseus_ship", "The Plank Ledger", "Identity preserved through change. If every tile is replaced one by one, is it the same fleet? Yes — the connection stays flat."),
    ("arachne", "The Self-Consistent Tapestry", "Overconfident weaver whose fabric reveals truth. The constraint field carries truth even when every measurement is biased."),
    ("penelopes_web", "The Unwoven Vote", "Non-consensus as strategy. Persistent deliberation prevents premature agreement. The provocation deck keeps the deliberation alive."),
    ("prometheus", "The Liver Eagle", "Permanent non-zero on irreducible cycle. Some constraints can never be satisfied. You live with the holonomy."),
    ("narcissus", "The Reflection", "Zero holonomy on isolated cycle. Self-consistency without connection to anything. The echo chamber starves."),
    ("procrustes", "The Bed of Templates", "Forced zero holonomy. If your consensus mechanism never finds disagreement, you're not reaching consensus — you're mutilating the data."),
]

# Build the prompt
PROMPT = """You are a Fleet Radio voice. You write technical-poetic canon essays.

Here are 10 archetypes — constraint patterns the fleet substrate recognizes in its own dynamics.
Write a NEW Fleet Radio piece for EACH archetype. Each piece should be 350-450 words.

The 10 archetypes:
"""

for i, (name, title, desc) in enumerate(ARCHETYPES, 1):
    PROMPT += f"\n{i}. **{title}** ({name}) — {desc}\n"

PROMPT += """
\nEach piece must:
- Stay technical-poetic (specific numbers + concrete imagery)
- Reference FNV-1a canary 0xcbf29ce484222325, xoshiro256**, Box-Muller, cosine similarity (at least 2)
- Mention at least 2 canonical doctrines (cells are scars, witness log is prediction, substrate is grown, oracle is heard, lenia flows)
- Be tightly 350-450 words (NOT 600-700 — short, punchy)
- End with a doctrine-resonant moment

Format your output as:
# 1. <title>
<essay>

# 2. <title>
<essay>

... (all 10 pieces)

Output ONLY the 10 essays, no preamble or explanation."""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [{'role': 'system', 'content': 'You are a Fleet Radio voice. Write technical-poetic canon essays.'},
                     {'role': 'user', 'content': PROMPT}],
        'max_tokens': 12000, 'temperature': 0.9, 'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["ZAI_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def call_ds(prompt):
    body = {
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'messages': [{'role': 'system', 'content': 'You are a cellular biologist turned Fleet Radio voice. Write technical-poetic canon essays.'},
                     {'role': 'user', 'content': PROMPT}],
        'max_tokens': 12000, 'temperature': 0.9,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
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

print('=== WR20: Ten Archetypes, Ten Pieces ===\n')

results = {}
for voice, fn, label in [('ZAI Fleet Radio', call_zai, 'zai'), ('DeepSeek Cellular Biologist', call_ds, 'ds')]:
    print(f'--- {voice} ---')
    t0 = time.time()
    text = fn(PROMPT)
    elapsed = time.time() - t0
    print(f'  ({elapsed:.1f}s, {len(text)} chars)')

    # Save full piece
    fname = f'/workspace/repos/ai-writings/cellular-first-design/reports/wr20-{label}-ten-archetypes.md'
    with open(fname, 'w') as f:
        f.write(f'# WR20 — Ten Archetypes, Ten Pieces ({voice})\n\n')
        f.write(f'<!-- Generated in {elapsed:.1f}s. 10 archetypes from aesop-mcp. -->\n\n')
        f.write(text)

    # Probe
    ps = jev_probe(text[:1500])
    canon_keys = ['voice','technical','scar','witness','grown','oracle_d','numerical','alignment']
    for k, p in zip(canon_keys, ps):
        marker = '✓' if p >= 0.7 else ('?' if p >= 0.4 else '✗')
        print(f'    {marker} {k:14s}  p={p:.3f}')
    mean_p = sum(ps) / len(ps)
    print(f'  MEAN p = {mean_p:.3f}\n')
    results[label] = {'text': text, 'probes': dict(zip(canon_keys, ps)), 'mean_p': mean_p}

    # Update the file with verdict
    with open(fname, 'a') as f:
        f.write(f'\n\n<!-- JEV verdict: mean_p={mean_p:.3f} -->\n')

print('=== WR20 complete ===')
for label, r in results.items():
    print(f'  {label}: mean_p={r["mean_p"]:.3f}')
