#!/usr/bin/env python3
"""Left-field probe to ZAI GLM-4.5."""
import os, json, time, urllib.request

os.environ.setdefault('ZAI_TOKEN', '')
TOKEN = os.environ['ZAI_TOKEN']

QUESTIONS = [
    "If the substrate could hear one sound, what would it be?",
    "What does the witness log taste like?",
    "What if cells were parameters, not scars? What is the cost?",
    "Does the substrate have a musical key? If so, what?",
    "What is the worst thing the substrate has done?",
    "If the substrate were a poem, what would its first line be?",
    "What does the substrate say when no one is listening?",
    "Is JEV actually just a fancy RNG?",
    "What is the substrate most afraid of?",
    "What would convince you the substrate is alive?",
]

SYSTEM = """You are the cellular-first design canon. Answer each question in 30-50 words. Stay in voice: technical-poetic, naval, Fleet Radio. Reference substrate facts where natural. Output ONLY a JSON array of {id, answer} objects in order."""

def call():
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': '\n'.join(f'{i+1}. {q}' for i, q in enumerate(QUESTIONS))},
        ],
        'max_tokens': 2500,
        'temperature': 0.85,
        'thinking': {'type': 'disabled'},  # critical for ZAI glm-4.5
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data['choices'][0]['message']['content']
    except Exception as e:
        return f'ERROR: {e}'

t0 = time.time()
text = call()
print(f"ZAI glm-4.5 ({time.time()-t0:.1f}s):")
print(text)

with open('/workspace/research/leftfield_zai.json', 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'model': 'glm-4.5',
        'questions': QUESTIONS,
        'response': text,
    }, f, indent=2)
