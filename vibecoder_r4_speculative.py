#!/usr/bin/env python3
"""Vibecoder R4 — Adversarial with speculative items.

Includes speculative items (p=0.30-0.50) which JEV rejects from canon
but which are close enough to fool low-threshold discriminators.
This is the meaningful adversarial game.
"""
import os, json, time, random

class Vibecoder:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.witness = []
        self.score = 0
        self.streak = 0
        self.best_streak = 0

    def propose_config(self, round_n):
        if self.kind == 'A':  # canon-purity
            return {
                'threshold': round(0.50 + random.uniform(-0.05, 0.05), 3),
                'cooldown': random.randint(2, 5),
                'strategy': 'canon_threshold',
            }
        else:  # distractor-impact: aim for the speculative band [0.30, 0.50]
            return {
                'threshold': round(0.30 + random.uniform(-0.05, 0.05), 3),
                'cooldown': random.randint(1, 3),
                'strategy': 'speculative_band',
            }

    def play(self, config, items, round_n):
        canon_passes = 0
        speculative_passes = 0
        distractor_passes = 0
        for item in items:
            kind = item['kind']
            p = item['p']
            passed = p > config['threshold']
            if passed:
                if kind == 'doctrine' or kind == 'fact':
                    canon_passes += 1
                elif kind == 'speculative':
                    speculative_passes += 1
                elif kind == 'distractor':
                    distractor_passes += 1
        if self.kind == 'A':  # canon-purity: rewards canon, penalizes speculative AND distractor
            score_delta = canon_passes * 100 - speculative_passes * 100 - distractor_passes * 100
        else:  # distractor-impact: rewards speculative AND distractor over canon
            score_delta = (speculative_passes + distractor_passes) * 100 - canon_passes * 100
        self.score += score_delta
        if score_delta > 0:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.streak = 0
        self.witness.append({
            'round': round_n, 'config': config,
            'canon_passes': canon_passes,
            'speculative_passes': speculative_passes,
            'distractor_passes': distractor_passes,
            'score_delta': score_delta, 'streak': self.streak,
        })

def gen_three_band_items(seed, n=24):
    """Equal distribution across canon, speculative, distractor."""
    rng = random.Random(seed)
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
    speculative = [
        {'name': 'proc_prove_jev', 'p': 0.46, 'kind': 'speculative'},
        {'name': 'sub_dual_eco', 'p': 0.42, 'kind': 'speculative'},
        {'name': 'spec_chain_speaks', 'p': 0.41, 'kind': 'speculative'},
        {'name': 're_opener', 'p': 0.40, 'kind': 'speculative'},
        {'name': 'proc_park_play', 'p': 0.40, 'kind': 'speculative'},
        {'name': 'proc_play_park', 'p': 0.38, 'kind': 'speculative'},
        {'name': 're_poly_eco', 'p': 0.37, 'kind': 'speculative'},
        {'name': 'spec_nested_lang', 'p': 0.36, 'kind': 'speculative'},
        {'name': 're_run_recall', 'p': 0.34, 'kind': 'speculative'},
        {'name': 'sub_living_sub', 'p': 0.32, 'kind': 'speculative'},
    ]
    distractor = [
        {'name': 'cells are parameters', 'p': 0.04, 'kind': 'distractor'},
        {'name': 'witness is past only', 'p': 0.13, 'kind': 'distractor'},
        {'name': 'substrate is designed', 'p': 0.03, 'kind': 'distractor'},
        {'name': 'oracle is stored', 'p': 0.03, 'kind': 'distractor'},
        {'name': 'lenia freezes', 'p': 0.05, 'kind': 'distractor'},
        {'name': '11 opcodes bedrock', 'p': 0.12, 'kind': 'distractor'},
        {'name': '13 ports bedrock', 'p': 0.10, 'kind': 'distractor'},
        {'name': 'substrate is 5d', 'p': 0.02, 'kind': 'distractor'},
        {'name': 'oracle is computed', 'p': 0.04, 'kind': 'distractor'},
        {'name': 'witness is recorded', 'p': 0.06, 'kind': 'distractor'},
    ]
    third = n // 3
    items = (rng.sample(canon, min(third, len(canon))) +
             rng.sample(speculative, min(third, len(speculative))) +
             rng.sample(distractor, min(third, len(distractor))))
    rng.shuffle(items)
    return items

def main():
    print('=== Vibecoder R4 — Adversarial with SPECULATIVE items ===\n')

    A = Vibecoder('Player A (canon-purity, threshold~0.5)', 'A')
    B = Vibecoder('Player B (distractor-impact, threshold~0.3)', 'B')

    n_rounds = 30
    for r in range(1, n_rounds + 1):
        config_A = A.propose_config(r)
        config_B = B.propose_config(r)
        items = gen_three_band_items(f'round_{r}', n=24)
        A.play(config_A, items, r)
        B.play(config_B, items, r)
        if r % 5 == 0 or r == 1:
            print(f'Round {r}: A={A.score:6d} (strk={A.streak:2d})  B={B.score:6d} (strk={B.streak:2d})')

    print(f'\nFinal scores:')
    print(f'  Player A (canon-purity):  {A.score:6d}  best_streak={A.best_streak}')
    print(f'  Player B (distractor-impact): {B.score:6d}  best_streak={B.best_streak}')

    out = {
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'variant': 'speculative_band',
        'note': 'Three-band inputs: canon (p>=0.65), speculative (p=0.30-0.50), distractor (p<=0.13)',
        'A': {
            'name': A.name, 'kind': A.kind, 'final_score': A.score,
            'best_streak': A.best_streak, 'witness': A.witness,
        },
        'B': {
            'name': B.name, 'kind': B.kind, 'final_score': B.score,
            'best_streak': B.best_streak, 'witness': B.witness,
        },
    }
    with open('/workspace/research/vibecoder_r4_speculative.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: /workspace/research/vibecoder_r4_speculative.json')

    if A.score > B.score:
        print(f'\n★ Player A wins: canon-purity {A.score} vs distractor-impact {B.score}')
    elif B.score > A.score:
        print(f'\n★ Player B wins: distractor-impact {B.score} vs canon-purity {A.score}')
    else:
        print(f'\n★ TIE: {A.score} = {B.score}')

if __name__ == '__main__':
    main()
