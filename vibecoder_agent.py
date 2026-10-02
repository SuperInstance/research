#!/usr/bin/env python3
"""
Vibecoder Agent — An LLM loop that proposes signal-chain configurations
and watches witness logs to tune itself.

The loop:
1. Propose config (LLM writes thresholds, sensor weights, output mapping)
2. Run a Quilt-ESP32 cell simulation with that config
3. Watch witness log — how many canonical spikes? Mean p-value? Streak?
4. LLM observes the witness log and refines the config
5. Repeat

This is what "vibecoding the chain" means. The substrate is the LLM's
training set; every firing is a data point.
"""
import os, json, time, urllib.request, random, hashlib

os.environ.setdefault('ZAI_TOKEN', '')

CANON_PHRASES = [
    'cells are scars, not parameters',
    'witness log is the prediction',
    'substrate is grown, not designed',
    'oracle is heard, not stored',
    'lenia flows where conway stands still',
]

DISTRACTOR_PHRASES = [
    'cells are parameters, not scars',
    'witness log is past only',
    'substrate is designed, not grown',
    'oracle is stored, not heard',
    'conway flows where lenia stands still',
]

class Cell:
    """A simulated Quilt-ESP32 cell."""
    def __init__(self, config, rng):
        self.config = config
        self.rng = rng
        self.p = 0.5
        self.canonical_streak = 0
        self.distractor_streak = 0
        self.score = 0
        self.witness_log = []  # (timestamp, phrase, p, kind)
        self.t = 0

    def tick(self):
        """One spike event."""
        self.t += 1
        # Decide phrase: weighted by config
        canon_p = self.config.get('canon_bias', 0.5)
        if self.rng.random() < canon_p:
            phrase = random.choice(CANON_PHRASES)
            kind = 'canon'
            true_p = 0.85 + self.rng.random() * 0.10
        else:
            phrase = random.choice(DISTRACTOR_PHRASES)
            kind = 'distract'
            true_p = 0.10 + self.rng.random() * 0.10

        # JEV spike (in simulation: deterministic given phrase + threshold)
        threshold = self.config.get('spike_threshold', 0.5)
        detected_p = true_p + self.rng.uniform(-0.05, 0.05)
        spike_passes = detected_p >= threshold

        # Reward
        reward = 0
        if spike_passes and kind == 'canon':
            reward = int(detected_p * 100)
            self.canonical_streak += 1
            self.distractor_streak = 0
        elif spike_passes and kind == 'distract':
            reward = -50
            self.canonical_streak = 0
            self.distractor_streak += 1
        else:
            # missed — no spike, no reward, no penalty
            self.canonical_streak = 0

        self.score += reward
        self.witness_log.append({
            't': self.t,
            'phrase': phrase[:30],
            'p': round(detected_p, 3),
            'kind': kind,
            'spike_passes': spike_passes,
            'reward': reward,
        })
        if len(self.witness_log) > 100:
            self.witness_log = self.witness_log[-100:]
        return reward, phrase, kind, detected_p

    def summary(self, n_recent=20):
        recent = self.witness_log[-n_recent:]
        canon = sum(1 for w in recent if w['kind'] == 'canon')
        distract = sum(1 for w in recent if w['kind'] == 'distract')
        passed = sum(1 for w in recent if w['spike_passes'])
        mean_p = sum(w['p'] for w in recent) / max(1, len(recent))
        return {
            'window': len(recent),
            'canon': canon,
            'distract': distract,
            'spikes_passed': passed,
            'mean_p': round(mean_p, 3),
            'best_streak': self.canonical_streak,
            'score': self.score,
            'config': self.config,
        }


def llm_propose_config(history, zai_token):
    """Ask ZAI to propose a new config based on history."""
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': """You are the vibecoder. You tune a Quilt-ESP32 signal-chain config to maximize score.

Config fields:
- canon_bias (0.0-1.0): how often to favor canon phrases vs distractors
- spike_threshold (0.0-1.0): JEV p-value threshold for a spike to count
- cooldown_ticks (1-50): ticks between spikes

Output JSON ONLY: {"canon_bias": 0.7, "spike_threshold": 0.5, "cooldown_ticks": 5, "reasoning": "..."}"""},
            {'role': 'user', 'content': f"""Recent history:

{json.dumps(history[-10:], indent=2)}

Best run so far:
{json.dumps(history, indent=2)[:1000]}

Propose ONE config (output JSON only, no commentary):"""},
        ],
        'max_tokens': 600, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {zai_token}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = json.loads(r.read())['choices'][0]['message']['content']
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
    except Exception as e:
        print(f"  LLM error: {e}")
    return {'canon_bias': 0.5, 'spike_threshold': 0.5, 'cooldown_ticks': 5}


def main():
    token = os.environ.get('ZAI_TOKEN', '')
    print('=== Vibecoder Agent ===')
    print('LLM proposes configs, watches witness log, tunes over rounds.\n')

    rng = random.Random(0xcbf29ce484222325)  # FNV-1a canary seed
    history = []
    best_score = -999
    best_config = None

    for round_num in range(1, 7):
        # Propose config from LLM
        config = llm_propose_config(history, token)
        # Sometimes baseline/seeded configs
        if round_num == 1:
            config = {'canon_bias': 0.5, 'spike_threshold': 0.5, 'cooldown_ticks': 1, 'reasoning': 'baseline'}
        elif round_num == 2:
            config = {'canon_bias': 0.7, 'spike_threshold': 0.7, 'cooldown_ticks': 1, 'reasoning': 'canon-biased'}
        elif round_num == 3:
            config = {'canon_bias': 0.3, 'spike_threshold': 0.3, 'cooldown_ticks': 1, 'reasoning': 'low threshold'}

        print(f'\n--- Round {round_num}: config = {config} ---')
        cell = Cell(config, rng)
        # Run 200 ticks
        for _ in range(200):
            cell.tick()

        s = cell.summary(50)
        s['round'] = round_num
        s['reasoning'] = config.get('reasoning', '')
        history.append(s)
        print(f'Score: {s["score"]}  Best streak: {s["best_streak"]}  Mean p: {s["mean_p"]}  Spikes passed: {s["spikes_passed"]}/50')

        if s['score'] > best_score:
            best_score = s['score']
            best_config = config

    # Save history
    with open('/workspace/research/vibecoder_history.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'history': history,
            'best_score': best_score,
            'best_config': best_config,
        }, f, indent=2)
    print(f'\nSaved: /workspace/research/vibecoder_history.json')
    print(f'Best score: {best_score}  with config: {best_config}')


if __name__ == '__main__':
    main()
