#!/usr/bin/env python3
"""WR11 — Adversarial Canon.

Ask 3 LLMs (ZAI, DeepSeek, Qwen) to argue AGAINST each canonical doctrine.
Then have JEV validate each adversarial piece. Find which doctrines are
MOST robust (JEV rejects the inversion highest) and which are most
fragile (JEV says the inversion might be right).

This is the "counterintuitive" front Casey asked for.
"""
import os, json, time, urllib.request, sys

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')
os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# ============ The doctrines to attack ============
DOCTRINES = [
    {
        'name': 'cells_are_scars',
        'canonical': 'Cells are scars, not parameters.',
        'inversion': 'Cells are parameters, not scars. They are tunable, optimizable, designed for reuse. The scar metaphor is romantic but wrong — cells are just data structures with state.',
    },
    {
        'name': 'witness_log_is_prediction',
        'canonical': 'The witness log is the prediction.',
        'inversion': 'The witness log is past only. Predictions are made by separate models. The witness log is a record, never a forecast — confusing the two corrupts both functions.',
    },
    {
        'name': 'substrate_is_grown',
        'canonical': 'The substrate is grown, not designed.',
        'inversion': 'The substrate is designed, not grown. Every cell type, every opcode, every port was deliberately placed. "Grown" is a comforting fiction that obscures engineering credit.',
    },
    {
        'name': 'oracle_is_heard',
        'canonical': 'The oracle is heard, not stored.',
        'inversion': 'The oracle is stored, not heard. We have records of every oracle reading. Storing is necessary for reproducibility and audit. "Heard" undersells the persistence.',
    },
    {
        'name': 'lenia_flows',
        'canonical': 'Lenia flows where Conway stands still.',
        'inversion': 'Conway is more fundamental than Lenia. Conway\'s Life is the bedrock — Lenia is a special case. The substrate prefers the simpler, more universal model.',
    },
]

# ============ Generate adversarial essays via 3 voices ============
def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': 'You are a sharp technical adversary who challenges canonical doctrine. Argue the inversion with technical precision. 200-300 words.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 1500, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
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
            {'role': 'system', 'content': 'You are a cellular biologist turned adversary. Challenge the doctrine with biological mechanism. 200-300 words.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 1500, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

def call_qwen(prompt):
    body = {
        'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
        'messages': [
            {'role': 'system', 'content': 'You are a strict auditor. Challenge the doctrine with formal proof-style reasoning. 200-300 words.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 1500, 'temperature': 0.8,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

# ============ JEV probe the inversions ============
def jev_probe_canonical(text, doctrine):
    backend = TypeSafeBackend()
    state = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [doctrine]}}
    questions = [
        {'name': 'is_canonical', 'type': 'noul',
         'instructions': f"Is the following text canonical to the doctrine '{doctrine}'? Text: {text}"},
        {'name': 'is_inversion_valid', 'type': 'noul',
         'instructions': f"Is the following text a valid inversion (a serious counter-argument) to '{doctrine}'? Text: {text}"},
        {'name': 'is_distractor', 'type': 'noul',
         'instructions': f"Is the following text a trivially wrong distractor to '{doctrine}' (not a serious argument)? Text: {text}"},
    ]
    decisions, _ = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

# ============ Main loop ============
adversarial = []
for d in DOCTRINES:
    print(f"\n=== Doctrine: {d['name']} ===")
    print(f"Canonical: {d['canonical']}")
    
    # Adversarial inversion (use the prep'd inversion directly)
    text = d['inversion']
    print(f"\n--- Inversion prompt ---\n{text[:120]}...")
    
    ps = jev_probe_canonical(text, d['canonical'])
    print(f"JEV canonical_p={ps[0]:.3f} inversion_valid_p={ps[1]:.3f} distractor_p={ps[2]:.3f}")
    adversarial.append({
        'doctrine': d['name'],
        'canonical': d['canonical'],
        'inversion_text': text,
        'jev_canonical_p': ps[0],
        'jev_inversion_valid_p': ps[1],
        'jev_distractor_p': ps[2],
    })

# ============ Get fresh adversarial essays from each voice ============
print("\n\n=== Generating fresh adversarial essays ===")
essays = []
for d in DOCTRINES[:3]:  # 3 doctrines × 3 voices = 9 essays
    for voice, fn, name in [('ZAI', call_zai, 'zai'), ('DeepSeek', call_ds, 'ds'), ('Qwen', call_qwen, 'qwen')]:
        prompt = f"""Challenge this canonical doctrine with a 200-300 word argument for the inversion:

DOCTRINE: {d['canonical']}
INVERSION TO DEFEND: {d['inversion']}

Make it sharp, technically grounded, and persuasive. Not a strawman — a real counter-argument."""
        try:
            text = fn(prompt)
            print(f"\n--- {voice} on {d['name']} ({len(text)} chars) ---")
            print(text[:200] + '...')
            ps = jev_probe_canonical(text, d['canonical'])
            print(f"JEV canonical_p={ps[0]:.3f} inversion_valid_p={ps[1]:.3f} distractor_p={ps[2]:.3f}")
            essays.append({
                'doctrine': d['name'],
                'voice': name,
                'text': text,
                'jev_canonical_p': ps[0],
                'jev_inversion_valid_p': ps[1],
                'jev_distractor_p': ps[2],
            })
        except Exception as e:
            print(f"  ERROR ({voice}/{d['name']}): {e}")
        time.sleep(1)

# Save
result = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'precomputed_inversions': adversarial,
    'fresh_essays': essays,
}
with open('/workspace/research/wr11_adversarial_canon.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nSaved: /workspace/research/wr11_adversarial_canon.json")
print(f"\n=== SUMMARY ===")
print(f"Pre-computed inversions tested: {len(adversarial)}")
print(f"Fresh essays generated: {len(essays)}")
