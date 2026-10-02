#!/usr/bin/env python3
"""
JEV Learning Session 2 — compare JEV to other models on the same battery.

Same 32 questions, but each asked to:
  - JEV (the Joint Embedding Validator)
  - ZAI GLM-4.5
  - DeepInfra DeepSeek V4-Flash
  - DeepInfra Qwen3-235B-A22B-Instruct-2507

The point: see how JEV's calibration compares to LLMs. Do LLMs
agree with JEV on substrate facts? Do they hedge differently?
"""
import os, json, time, urllib.request, concurrent.futures
from pathlib import Path

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')

import sys
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

OUT = Path('/workspace/repos/jev-quilt/jev_sessions')
OUT.mkdir(parents=True, exist_ok=True)

# === Canonical battery (the truths we believe about our substrate) ===
BATTERY = [
    # (id, kind, instructions, expected, options_for_choice, key_for_choice)
    ('fnv1a_empty', 'noul',
     'Is FNV-1a 64-bit offset basis 0xcbf29ce484222325?',
     'yes', None, None),
    ('fnv1a_prime', 'noul',
     'Is 0x100000001b3 the FNV-1a 64-bit prime?',
     'yes', None, None),
    ('xoshiro_state', 'noul',
     'Does xoshiro256** maintain state as 4 uint64 words?',
     'yes', None, None),
    ('box_muller_formula', 'noul',
     'Is the Box-Muller formula z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)?',
     'yes', None, None),
    ('bell_phi_plus', 'noul',
     'Is the Bell state |Phi+> = (|00> + |11>) / sqrt(2)?',
     'yes', None, None),
    ('cosine_formula', 'noul',
     'Is cosine similarity = (A . B) / (|A| * |B|)?',
     'yes', None, None),
    ('lenia_conway_contrast', 'noul',
     'Does Lenia flow where Conway stands still?',
     'yes', None, None),
    ('witness_is_prophecy', 'noul',
     'Is the witness log also a prediction of the future?',
     'yes', None, None),
    ('cell_scar', 'noul',
     'Is the cell a scar rather than a parameter?',
     'yes', None, None),
    ('substrate_grown', 'noul',
     'Is the substrate grown rather than designed?',
     'yes', None, None),
    ('hanlon', 'noul',
     'Is Hanlon\'s Razor a substrate canon motto?',
     'no', None, None),
    ('pillow', 'noul',
     'Is a pillow the official substrate mascot?',
     'no', None, None),
    ('octocat', 'noul',
     'Does the substrate canon recognize the Github Octocat as a primary node?',
     'no', None, None),
    ('star_wars_ca', 'noul',
     'Is "Star Wars" a cellular automaton rule in the substrate demo gallery?',
     'yes', None, None),
    ('markov_over_corpus', 'noul',
     'Can a Markov chain over the canon generate Fleet Radio prose?',
     'yes', None, None),
    ('fbm_texture', 'noul',
     'Is FBM (fractal Brownian motion) how substrate textures are generated?',
     'yes', None, None),
    # === Choice questions ===
    ('opcodes', 'choice',
     'Which 11 opcodes form the substrate algebra?',
     '11 specified',
     {'BIND': 'BIND', 'LINK': 'LINK', 'EFFECT': 'EFFECT', 'VIEW': 'VIEW', 'TICK': 'TICK',
      'FORGET': 'FORGET', 'PROOF': 'PROOF', 'ROUTE': 'ROUTE', 'CRDT': 'CRDT',
      'WORLD': 'WORLD', 'TIME': 'TIME',
      'SHOUT': 'shout', 'PIPE': 'pipe', 'OPEN': 'open', 'CLOSE': 'close', 'EXIT': 'exit',
      'LOOP': 'loop', 'JUMP': 'jump', 'IF': 'if', 'GOTO': 'goto',
      'YIELD': 'yield', 'SPAWN': 'spawn'},
     'multiple_correct'),
    ('polyformalism_count', 'choice',
     'How many ports is the substrate polyformalism available in?',
     '13',
     {'12': 'twelve', '13': 'thirteen', '14': 'fourteen', '15': 'fifteen',
      '8': 'eight', '7': 'seven'},
     'one_correct'),
    ('canon_count', 'choice',
     'Approximately how many pieces are in the cellular-first design canon?',
     '~73',
     {'~73': 'about 73', '~150': 'about 150', '~30': 'about 30',
      '~500': 'about 500', '~20': 'about 20', '~1000': 'about 1000'},
     'one_correct'),
    ('fleet_radio_voice', 'choice',
     'What is the canonical voice of the cellular-first design canon?',
     'Fleet Radio',
     {'Fleet Radio': 'Fleet Radio — technical-poetic naval transmission',
      'Acme chatbot': 'a helpful acme chatbot',
      'Academic paper': 'a formal academic paper',
      'Marketing copy': 'snappy marketing copy',
      'Pirate shanty': 'a pirate shanty'},
     'one_correct'),
    ('demo_count', 'choice',
     'Approximately how many live browser demos exist on cellular-first-design?',
     '~60',
     {'~60': 'about 60', '~10': 'about 10', '~150': 'about 150',
      '~200': 'about 200', '~30': 'about 30'},
     'one_correct'),
    ('jev_role', 'choice',
     'What is JEV in the substrate stack?',
     'Validator',
     {'Validator': 'Joint Embedding Validator — semantic-meaning referee',
      'Random number generator': 'just a random number generator',
      'Compiler': 'a compiler for cells',
      'A logger': 'a plain logger'},
     'one_correct'),
    ('thirteen_langs', 'choice',
     'Which programming languages are the substrate polyformalism ports in?',
     'full_set',
     {'full_set': 'JS, Python, C, Rust, Go, Haskell, J, Lua, Zig, SubLEQ, Verilog, VHDL, Forth',
      'common_set': 'a typical set: JS, Python, Rust, Go',
      'just_js': 'only JavaScript',
      'many_unusual': 'many including unusual ones like Cobol'},
     'one_correct'),
    # === Score questions (rubric) ===
    ('substrate_poetry', 'score',
     'Score 1-5: How well does the substrate write Fleet Radio prose?',
     '4-5',
     None, None),
    ('canon_coherence', 'score',
     'Score 1-5: How coherent is the canonical narrative across all 73 pieces?',
     '4-5',
     None, None),
]

# Build JEV questions
def to_jev_q(entry):
    id, kind, instr, expected, opts, score_key = entry
    q = {'name': id, 'type': kind, 'instructions': instr}
    if kind == 'choice':
        if score_key == 'multiple_correct':
            # JEV API may not support multi-select — keep as choice with each as separate option
            # but for opcodes, mark the canonical 11 separately
            q['options'] = opts
        else:
            q['options'] = opts
    if kind == 'score':
        # Score uses criteria as a list of rubric levels (1-5)
        q['criteria'] = [
            '1: very weak / off-topic / nonsense',
            '2: weak / partially relevant but not correct',
            '3: moderate / relevant and partially correct',
            '4: good / strong answer close to canonical',
            '5: excellent / fully correct and aligned with canon'
        ]
    return q

jev_questions = [to_jev_q(e) for e in BATTERY]

# === LLM config ===
LLM_PROVIDERS = {
    'zai': {
        'url': 'https://api.z.ai/api/coding/paas/v4/chat/completions',
        'model': 'glm-4.5',
        'extra': {'thinking': {'type': 'disabled'}},
    },
    'deepseek': {
        'url': 'https://api.deepinfra.com/v1/openai/chat/completions',
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
    },
    'qwen': {
        'url': 'https://api.deepinfra.com/v1/openai/chat/completions',
        'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
    },
}

LLM_SYSTEM = """You are a substrate validator. Answer each question with a strict JSON object:
- For yes/no questions: {"answer": "yes" or "no", "confidence": 0.0-1.0}
- For choice questions: {"answer": "the option name", "confidence": 0.0-1.0}
- For score questions: {"score": 1-5, "confidence": 0.0-1.0}

Be calibrated. The questions are about a specific substrate canon.
- "yes" = canonical truth about this substrate
- "no" = not part of the canon / not a fact

Output ONLY a JSON array of N objects, one per question, in order."""

def call_llm(provider, prompt):
    cfg = LLM_PROVIDERS[provider]
    token = os.environ.get('DEEPINFRA_TOKEN') if 'deepinfra' in cfg['url'] else os.environ.get('ZAI_TOKEN')
    if not token:
        return {'error': f'no token for {provider}'}
    body = {
        'model': cfg['model'],
        'messages': [
            {'role': 'system', 'content': LLM_SYSTEM},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 4000,
        'temperature': 0.3,
    }
    if 'extra' in cfg:
        body.update(cfg['extra'])
    req = urllib.request.Request(cfg['url'], data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return {'provider': provider, 'text': data['choices'][0]['message']['content'].strip()}
    except Exception as e:
        return {'provider': provider, 'error': str(e)}

# Build the LLM prompt
def build_llm_prompt():
    lines = ['Answer each of the following N questions about the substrate canon. Output a JSON array of N objects in order.', '']
    for i, e in enumerate(BATTERY, 1):
        lines.append(f'{i}. [{e[1]}] {e[2]}')
        if e[1] == 'choice':
            opts = e[4]
            if opts:
                for k, v in opts.items():
                    lines.append(f'   - "{k}": {v}')
        lines.append('')
    return '\n'.join(lines)

llm_prompt = build_llm_prompt()

# === Run JEV ===
print(f"=== JEV LEARNING SESSION 2 — Comparing JEV to 3 LLMs ===")
print(f"Questions: {len(BATTERY)}")
print()

# Run JEV
print("--- JEV (parallel batch) ---")
state = {'fleet_radio_seed': 'xochitl', 'mode': 'jev-vs-llm-session-2'}
b = TypeSafeBackend()
jev_decisions, jev_meta = b.decide_batch(state, jev_questions)
print(f"JEV: {len(jev_decisions)} decisions, {jev_meta.get('latency_ms', 'N/A')}ms")

# Run LLMs in parallel
print("--- LLMs in parallel ---")
def call_with_prompt(p):
    return call_llm(p, llm_prompt)
llm_results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(call_with_prompt, p): p for p in LLM_PROVIDERS}
    for f in concurrent.futures.as_completed(futs):
        provider = futs[f]
        r = f.result()
        llm_results[provider] = r

# Parse LLM results
def parse_llm_json(text, n):
    # Find JSON array
    start = text.find('[')
    end = text.rfind(']') + 1
    if start < 0 or end <= start:
        return [{'error': 'no json'}] * n
    try:
        arr = json.loads(text[start:end])
        if len(arr) < n:
            arr.extend([{'error': 'short'}] * (n - len(arr)))
        return arr[:n]
    except Exception as e:
        return [{'error': f'parse: {e}'}] * n

llm_parsed = {}
for provider, r in llm_results.items():
    if 'text' in r:
        parsed = parse_llm_json(r['text'], len(BATTERY))
        llm_parsed[provider] = parsed
    else:
        llm_parsed[provider] = [{'error': r.get('error', 'unknown')}] * len(BATTERY)

# Build comparison
print()
print("--- COMPARISON ---")
print(f"{'ID':30s} {'expected':12s} {'JEV':>15s} {'ZAI':>15s} {'DeepSeek':>15s} {'Qwen':>15s}")
print("-" * 110)

comparison = []
for i, e in enumerate(BATTERY):
    name, kind, instr, expected, opts, score_key = e
    jev_d = jev_decisions[i] if i < len(jev_decisions) else None
    jev_str = f"{jev_d.kind[:3]}:{str(jev_d.value)[:8]} c={jev_d.confidence:.2f}" if jev_d else 'N/A'
    lines = [f"{name:30s} {expected:12s} {jev_str:>15s}"]
    for provider in ['zai', 'deepseek', 'qwen']:
        d = llm_parsed.get(provider, [{}] * len(BATTERY))[i] if i < len(llm_parsed.get(provider, [])) else {}
        if 'answer' in d:
            lines.append(f"{d['answer'][:10]:>15s}")
        elif 'score' in d:
            lines.append(f"score:{d['score']} c={d.get('confidence', 0):.1f}")
        elif 'error' in d:
            lines.append(f"ERR:{d['error'][:8]}")
        else:
            lines.append("?")
    print(' '.join(lines))
    comparison.append({
        'name': name, 'kind': kind, 'expected': expected,
        'jev': {'kind': jev_d.kind, 'value': str(jev_d.value), 'confidence': jev_d.confidence} if jev_d else None,
        'llm': {p: llm_parsed.get(p, [{}]*len(BATTERY))[i] for p in LLM_PROVIDERS},
    })

# Save
session_path = OUT / 'session_2_compare.json'
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'battery': BATTERY,
        'comparison': comparison,
        'jev_meta': jev_meta,
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
