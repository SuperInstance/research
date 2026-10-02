#!/usr/bin/env python3
"""Left-field probe to DeepSeek-V4-Flash."""
import os, json, time, urllib.request

os.environ.setdefault('DEEPINFRA_TOKEN', '')
TOKEN = os.environ['DEEPINFRA_TOKEN']

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
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'messages': [
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': '\n'.join(f'{i+1}. {q}' for i, q in enumerate(QUESTIONS))},
        ],
        'max_tokens': 2500,
        'temperature': 0.85,
    }
    req = urllib.request.Request('https://api.deepinfra.com/v1/openai/chat/completions',
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
print(f"DeepSeek-V4-Flash ({time.time()-t0:.1f}s):")
print(text)

# Save
with open('/workspace/research/leftfield_deepseek.json', 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'model': 'deepseek-ai/DeepSeek-V4-Flash',
        'questions': QUESTIONS,
        'response': text,
    }, f, indent=2)
