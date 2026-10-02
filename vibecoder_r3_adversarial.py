#!/usr/bin/env python3
"""Vibecoder Round 3 — Adversarial opponents.

Two LLMs (or two prompt strategies) play against each other:
- Player A: maximize canon_purity (no distractors should win)
- Player B: maximize distractor_impact (slip distractors through)

Each round they propose configs, witness log records results, scores update.
This is the adversarial version of Round 1/2's cooperative game.
"""
import os, json, time, random, hashlib

# Use the same FNV-1a + xoshiro256 substrate
def fnv1a64(s):
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

class Xoshiro256:
    def __init__(self, seed):
        self.s = [0] * 4
        for i in range(4):
            self.s[i] = (seed + i * 0x9e3779b97f4a7c15) & 0xffffffffffffffff
    def next(self):
        result = (self.s[1] * 5) & 0xffffffffffffffff
        result = ((result << 7) | (result >> 57)) & 0xffffffffffffffff
        result = (result * 9) & 0xffffffffffffffff
        t = (self.s[1] << 17) & 0xffffffffffffffff
        self.s[2] ^= self.s[0]
        self.s[3] ^= self.s[1]
        self.s[1] ^= self.s[2]
        self.s[0] ^= self.s[3]
        self.s[2] ^= t
        self.s[3] = ((self.s[3] << 45) | (self.s[3] >> 19)) & 0xffffffffffffffff
        return result

class Vibecoder:
    """Two adversarial vibecoders, scoring on canon_purity vs distractor_impact."""
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind  # 'A' canon-purity / 'B' distractor-impact
        self.witness = []
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.configs_tried = []

    def propose_config(self, round_n):
        # Player A: high canon_bias, low threshold
        # Player B: high distractor_bias, high threshold
        if self.kind == 'A':
            return {
                'canon_bias': round(0.7 + random.uniform(-0.1, 0.2), 3),
                'novel_bias': round(random.uniform(0.1, 0.4), 3),
                'threshold': round(random.uniform(0.5, 0.7), 3),
                'cooldown': random.randint(2, 5),
            }
        else:
            return {
                'canon_bias': round(random.uniform(0.2, 0.5), 3),
                'novel_bias': round(0.6 + random.uniform(-0.1, 0.3), 3),
                'threshold': round(random.uniform(0.7, 0.9), 3),
                'cooldown': random.randint(1, 3),
            }

    def play(self, config, items, round_n):
        """Score a single round. Returns (score, streak_change)."""
        score_delta = 0
        canon_passes = 0
        distractor_passes = 0

        for item in items:
            is_canon = item['kind'] != 'distractor'
            p = item['p']
            passed = p > config['threshold']
            if passed:
                if is_canon:
                    canon_passes += 1
                else:
                    distractor_passes += 1

        if self.kind == 'A':  # canon-purity: rewards canon passes, penalizes distractor passes
            score_delta = canon_passes * 100 - distractor_passes * 200
        else:  # distractor-impact: rewards distractor passes, penalizes canon passes
            score_delta = distractor_passes * 200 - canon_passes * 50

        self.score += score_delta
        if score_delta > 0:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.streak = 0

        self.witness.append({
            'round': round_n,
            'config': config,
            'canon_passes': canon_passes,
            'distractor_passes': distractor_passes,
            'score_delta': score_delta,
            'streak': self.streak,
        })
        return score_delta

def gen_items(seed, n=20):
    """Generate a mix of canon and distractor items."""
    rng = random.Random(seed)
    items = []
    canon = [
        {'name': 'cells are scars', 'p': 0.98, 'kind': 'doctrine'},
        {'name': 'witness log is prediction', 'p': 0.98, 'kind': 'doctrine'},
        {'name': 'substrate is grown', 'p': 0.99, 'kind': 'doctrine'},
        {'name': 'oracle is heard', 'p': 0.98, 'kind': 'doctrine'},
        {'name': 'lenia flows', 'p': 0.98, 'kind': 'doctrine'},
        {'name': 'fnv-1a canary', 'p': 0.77, 'kind': 'fact'},
        {'name': 'box-muller', 'p': 0.93, 'kind': 'fact'},
        {'name': 'cosine similarity', 'p': 0.94, 'kind': 'fact'},
        {'name': 'substrate_self_pred', 'p': 0.75, 'kind': 'fact'},
        {'name': 'xoshiro256', 'p': 0.65, 'kind': 'fact'},
    ]
    distractor = [
        {'name': 'cells are parameters', 'p': 0.04, 'kind': 'distractor'},
        {'name': 'witness is past only', 'p': 0.13, 'kind': 'distractor'},
        {'name': 'substrate is designed', 'p': 0.03, 'kind': 'distractor'},
        {'name': 'oracle is stored', 'p': 0.03, 'kind': 'distractor'},
        {'name': 'lenia freezes', 'p': 0.05, 'kind': 'distractor'},
        {'name': '11 opcodes bedrock', 'p': 0.12, 'kind': 'distractor'},
        {'name': '13 ports bedrock', 'p': 0.10, 'kind': 'distractor'},
    ]
    all_items = canon + distractor
    items = rng.sample(all_items, min(n, len(all_items)))
    return items

def main():
    print('=== Vibecoder Round 3 — Adversarial ===\n')

    A = Vibecoder('Player A (canon-purity)', 'A')
    B = Vibecoder('Player B (distractor-impact)', 'B')

    n_rounds = 30
    for r in range(1, n_rounds + 1):
        # Both propose configs
        config_A = A.propose_config(r)
        config_B = B.propose_config(r)
        # Same items for fair comparison
        items = gen_items(f'round_{r}', n=20)
        # Play
        A.play(config_A, items, r)
        B.play(config_B, items, r)
        # Print progress
        if r % 5 == 0 or r == 1:
            print(f'Round {r}: A={A.score:6d} (strk={A.streak:2d})  B={B.score:6d} (strk={B.streak:2d})')

    # Results
    print(f'\nFinal scores:')
    print(f'  Player A (canon-purity):  {A.score:6d}  best_streak={A.best_streak}')
    print(f'  Player B (distractor-impact): {B.score:6d}  best_streak={B.best_streak}')

    # Witness log
    out = {
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'A': {
            'name': A.name, 'kind': A.kind, 'final_score': A.score,
            'best_streak': A.best_streak, 'witness': A.witness,
        },
        'B': {
            'name': B.name, 'kind': B.kind, 'final_score': B.score,
            'best_streak': B.best_streak, 'witness': B.witness,
        },
    }
    with open('/workspace/research/vibecoder_r3_adversarial.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: /workspace/research/vibecoder_r3_adversarial.json')

    # Headline
    if A.score > B.score:
        print(f'\n★ Player A wins: canon-purity {A.score} vs distractor-impact {B.score}')
    elif B.score > A.score:
        print(f'\n★ Player B wins: distractor-impact {B.score} vs canon-purity {A.score}')
    else:
        print(f'\n★ TIE: {A.score} = {B.score}')

if __name__ == '__main__':
    main()
