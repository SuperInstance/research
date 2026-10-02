#!/usr/bin/env python3
"""Vibecoder Round 2 — Multi-objective optimization.

The LLM proposes configs optimizing 3 objectives:
1. Score (high)
2. Best streak (high) — long runs of canonical
3. Diversity (high) — exposure to novel phrases

Pareto-front exploration: trade-off between score and streak.

This goes beyond Round 1's single-objective.
"""
import os, json, time, urllib.request, random

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

NOVEL_PHRASES = [
    'cell mitosis',
    'noise floor rose',
    'first jev spike',
    'witness log grew',
    'oracle sighting',
    'cluster 7',
    'starboard horizon',
    'salvage vessel',
    'phospholipid bilayer',
    'arithmetic tamper detection',
]


class Cell:
    def __init__(self, config, rng):
        self.config = config
        self.rng = rng
        self.p = 0.5
        self.score = 0
        self.canonical_streak = 0
        self.best_streak = 0
        self.distractor_streak = 0
        self.diversity = set()
        self.witness_log = []
        self.t = 0

    def tick(self):
        self.t += 1
        canon_p = self.config.get('canon_bias', 0.5)
        novel_p = self.config.get('novel_bias', 0.1)
        # Decide phrase category
        r = self.rng.random()
        if r < canon_p:
            phrase = random.choice(CANON_PHRASES)
            kind = 'canon'
        elif r < canon_p + novel_p:
            phrase = random.choice(NOVEL_PHRASES)
            kind = 'novel'
        else:
            phrase = random.choice(DISTRACTOR_PHRASES)
            kind = 'distract'

        self.diversity.add(phrase)

        # True p-value
        if kind == 'canon':
            true_p = 0.85 + self.rng.random() * 0.10
        elif kind == 'distract':
            true_p = 0.10 + self.rng.random() * 0.10
        else:
            true_p = 0.40 + self.rng.random() * 0.20

        # JEV spike
        threshold = self.config.get('spike_threshold', 0.5)
        detected_p = true_p + self.rng.uniform(-0.05, 0.05)
        spike_passes = detected_p >= threshold

        # Reward
        reward = 0
        if spike_passes and kind == 'canon':
            reward = int(detected_p * 100)
            self.canonical_streak += 1
            self.distractor_streak = 0
            self.best_streak = max(self.best_streak, self.canonical_streak)
        elif spike_passes and kind == 'distract':
            reward = -50
            self.canonical_streak = 0
            self.distractor_streak += 1
        else:
            self.canonical_streak = 0

        self.score += reward
        self.witness_log.append({
            't': self.t, 'phrase': phrase[:30], 'p': round(detected_p, 3),
            'kind': kind, 'spike_passes': spike_passes, 'reward': reward,
        })
        if len(self.witness_log) > 100:
            self.witness_log = self.witness_log[-100:]
        return reward

    def summary(self):
        canon = sum(1 for w in self.witness_log if w['kind'] == 'canon')
        distract = sum(1 for w in self.witness_log if w['kind'] == 'distract')
        novel = sum(1 for w in self.witness_log if w['kind'] == 'novel')
        mean_p = sum(w['p'] for w in self.witness_log) / max(1, len(self.witness_log))
        return {
            'score': self.score,
            'best_streak': self.best_streak,
            'diversity': len(self.diversity),
            'canon': canon,
            'distract': distract,
            'novel': novel,
            'mean_p': round(mean_p, 3),
            'config': self.config,
        }


def llm_propose(history, zai_token):
    body = {
        'model': 'glm-4.5',
        'messages': [
            {'role': 'system', 'content': """You are the vibecoder (Round 2, multi-objective). Optimize for:
1. SCORE (high) — total reward
2. STREAK (high) — longest run of canonical hits
3. DIVERSITY (high) — distinct phrases seen

Config fields:
- canon_bias (0.0-1.0): fraction of canon phrases
- novel_bias (0.0-1.0): fraction of novel phrases
- spike_threshold (0.0-1.0): JEV p-value threshold
- cooldown_ticks (1-50): ticks between spikes

Output JSON only: {"canon_bias": 0.7, "novel_bias": 0.2, "spike_threshold": 0.5, "cooldown_ticks": 5, "reasoning": "..."}"""},
            {'role': 'user', 'content': f"""Recent history:

{json.dumps(history[-8:], indent=2)}

Propose ONE config (JSON only):"""},
        ],
        'max_tokens': 600, 'temperature': 0.85, 'thinking': {'type': 'disabled'},
    }
    req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {zai_token}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = json.loads(r.read())['choices'][0]['message']['content']
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
    except Exception as e:
        print(f"  LLM error: {e}")
    return {'canon_bias': 0.5, 'novel_bias': 0.1, 'spike_threshold': 0.5, 'cooldown_ticks': 5}


def main():
    token = os.environ.get('ZAI_TOKEN', '')
    print('=== Vibecoder Round 2 — Multi-objective ===\n')
    rng = random.Random(0xcbf29ce484222325)
    history = []

    # Round 1: baseline
    baseline_configs = [
        {'canon_bias': 0.5, 'novel_bias': 0.0, 'spike_threshold': 0.5, 'cooldown_ticks': 1, 'reasoning': 'baseline'},
        {'canon_bias': 0.7, 'novel_bias': 0.0, 'spike_threshold': 0.7, 'cooldown_ticks': 1, 'reasoning': 'canon-only'},
        {'canon_bias': 0.5, 'novel_bias': 0.3, 'spike_threshold': 0.6, 'cooldown_ticks': 1, 'reasoning': 'diversity'},
    ]
    for cfg in baseline_configs:
        cell = Cell(cfg, rng)
        for _ in range(200):
            cell.tick()
        s = cell.summary()
        s['round'] = len(history) + 1
        history.append(s)
        print(f"R{s['round']} ({cfg['reasoning'][:20]}): score={s['score']} streak={s['best_streak']} div={s['diversity']}")

    # Rounds 4-10: LLM proposes
    for round_num in range(4, 11):
        config = llm_propose(history, token)
        cell = Cell(config, rng)
        for _ in range(200):
            cell.tick()
        s = cell.summary()
        s['round'] = round_num
        s['reasoning'] = config.get('reasoning', '')
        history.append(s)
        print(f"R{s['round']} (LLM {config}): score={s['score']} streak={s['best_streak']} div={s['diversity']}")

    # Best by each objective
    best_score = max(history, key=lambda s: s['score'])
    best_streak = max(history, key=lambda s: s['best_streak'])
    best_diversity = max(history, key=lambda s: s['diversity'])

    print(f'\nBest by SCORE: R{best_score["round"]} score={best_score["score"]}')
    print(f'Best by STREAK: R{best_streak["round"]} streak={best_streak["best_streak"]}')
    print(f'Best by DIVERSITY: R{best_diversity["round"]} div={best_diversity["diversity"]}')

    # Pareto front
    print('\nPareto front (non-dominated):')
    pareto = []
    for s in history:
        dominated = False
        for other in history:
            if other == s: continue
            # o dominates s if o >= s on all objectives and > s on at least one
            if (other['score'] >= s['score'] and other['best_streak'] >= s['best_streak'] and other['diversity'] >= s['diversity'] and
                (other['score'] > s['score'] or other['best_streak'] > s['best_streak'] or other['diversity'] > s['diversity'])):
                dominated = True
                break
        if not dominated:
            pareto.append(s)
            print(f"  R{s['round']}: score={s['score']} streak={s['best_streak']} div={s['diversity']}")

    # Save
    with open('/workspace/research/vibecoder_round2_history.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'history': history,
            'pareto_count': len(pareto),
            'best_score': best_score,
            'best_streak': best_streak,
            'best_diversity': best_diversity,
        }, f, indent=2)
    print(f'\nSaved: /workspace/research/vibecoder_round2_history.json')


if __name__ == '__main__':
    main()
