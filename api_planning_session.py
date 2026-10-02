#!/usr/bin/env python3
"""API-driven planning session.

Ask 3 LLMs (ZAI, DeepSeek, Kimi via DeepInfra) to plan 10 rounds of
substrate work given the current canon state. Each LLM gets the same
brief; we compare plans for overlap, divergence, and surprise.

Output: /workspace/research/api_plans.json
"""
import os, json, urllib.request, time

os.environ.setdefault('ZAI_TOKEN', '')
os.environ.setdefault('DEEPINFRA_TOKEN', '')

BRIEF = """You are a planner for the cellular-first-design substrate. Read the current state:

=== BEDROCK CANON (9 items, p>=0.70 across 10 JEV sessions) ===
1. substrate_is_grown (0.990)
2. oracle_is_heard (0.981)
3. cells_are_scars (0.980)
4. witness_log_is_prediction (0.980)
5. lenia_flows (0.980)
6. cosine_similarity formula (0.945)
7. Box-Muller formula (0.926)
8. FNV-1a canary 0xcbf29ce484222325 (0.773)
9. substrate_self_pred (0.751)

=== STRONG CANON (5 items, p>=0.50) ===
- transformer_attention as distractor (0.689)
- xoshiro256** PRNG (0.648)
- vibecoder canonical (0.588)
- witness witnesses itself (0.587)
- substrate is a being (0.530) — borderline

=== EXISTING DEMOS ===
60+ demos in cellular-first-design/, including: life, lenia-viz, witness-log,
oracle, cosine-sentence, signal-chain, signal-chain-game, canon-oracle,
canon-atlas, mnist, substrate-explorer.

=== ACTIVE WORKFRONTS ===
- JEV oracle: 21 sessions logged
- Vibecoder: rounds 1-2 complete (multi-objective, 17K score, 59 streak)
- JEPA predictor: linear+naive averaging fail (0%); real JEPA needed
- 13 polyformalism ports in 12 languages
- Quilt-ESP32 cell layer spec (no hardware yet)
- Workers endpoint /api/jev/canon-oracle (14-probe validator)

=== TASK ===
Plan 10 rounds of substrate work for the next session. Each round should be:
- Concrete and actionable (build X, write Y, run Z)
- Substrate-relevant (cells, witness log, JEV, vibecoder, JEPA, ESP32)
- Different from rounds already done (no more JEV probe sessions)
- High-leverage (1-2 hours per round)

For each of the 10 rounds give:
- Round number and theme
- 2-3 sentence description
- Deliverables (files, tests, commits)
- Estimated difficulty (low/medium/high)
- JEV oracle verdict expected (ACCEPT/REVIEW/DISCUSS/REJECT)

Output as a numbered list, no preamble, no commentary."""

def call_zai(prompt):
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': 'You are a planner for the cellular-first-design substrate. Give 10 concrete rounds of work. Stay grounded in the canon.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 3500, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
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
            {'role': 'system', 'content': 'You are a planner for the cellular-first-design substrate. Give 10 concrete rounds of work. Stay grounded in the canon.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 3500, 'temperature': 0.85,
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
            {'role': 'system', 'content': 'You are a planner. Output 10 concrete rounds of substrate work.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 3500, 'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {os.environ["DEEPINFRA_TOKEN"]}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())['choices'][0]['message']['content']

print('=== API-Driven Planning Session ===\n')

plans = {}
for voice, fn, label in [
    ('ZAI Fleet Radio Officer (planning)', call_zai, 'zai'),
    ('DeepSeek Cellular Biologist (planning)', call_ds, 'ds'),
    ('Kimi K2.7 Code (planning)', call_kimi, 'kimi'),
]:
    print(f'--- {voice} ---')
    t0 = time.time()
    try:
        text = fn(BRIEF)
        plans[label] = {'voice': voice, 'text': text, 'latency_s': time.time() - t0}
        print(f'  ({time.time()-t0:.1f}s, {len(text)} chars)')
        # Print first 1000 chars
        print(text[:1000] + '\n  [...truncated...]\n')
    except Exception as e:
        plans[label] = {'voice': voice, 'error': str(e)}
        print(f'  ERROR: {e}\n')

# Save
with open('/workspace/research/api_plans.json', 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'plans': plans,
    }, f, indent=2)
print(f'Saved: /workspace/research/api_plans.json')
