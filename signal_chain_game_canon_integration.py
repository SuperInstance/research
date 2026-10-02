#!/usr/bin/env python3
"""
Kimi Plan Round 7: Signal-chain-game canon integration.

Refactor the signal-chain-game so:
1. Levels are procedurally generated from canon items
2. Player scores feed back into a witness log
3. JEPA could train on this data later

The game already exists at /workspace/repos/ai-writings/cellular-first-design/signal-chain-game/.
This script generates canon-derived levels and a witness-log bridge.
"""
import os, json, time, random
import hashlib

# ============ Canon items to derive levels from ============
CANON_ITEMS = [
    # Bedrock canon
    {'kind': 'doctrine', 'name': 'cells are scars', 'p': 0.98, 'hash': '0xcbf29ce484222325'},
    {'kind': 'doctrine', 'name': 'witness log is the prediction', 'p': 0.98, 'hash': '0xcbf29ce484222325'},
    {'kind': 'doctrine', 'name': 'substrate is grown', 'p': 0.99, 'hash': '0xcbf29ce484222325'},
    {'kind': 'doctrine', 'name': 'oracle is heard', 'p': 0.98, 'hash': '0xcbf29ce484222325'},
    {'kind': 'doctrine', 'name': 'lenia flows', 'p': 0.98, 'hash': '0xcbf29ce484222325'},
    # Numerical canon
    {'kind': 'fact', 'name': 'fnv-1a canary 0xcbf29ce484222325', 'p': 0.77, 'hash': '0xcbf29ce484222325'},
    {'kind': 'fact', 'name': 'xoshiro256**', 'p': 0.65, 'hash': '0xcbf29ce484222325'},
    {'kind': 'fact', 'name': 'box-muller', 'p': 0.93, 'hash': '0xcbf29ce484222325'},
    {'kind': 'fact', 'name': 'cosine similarity', 'p': 0.94, 'hash': '0xcbf29ce484222325'},
    {'kind': 'fact', 'name': 'eleven opcodes', 'p': 0.13, 'hash': '0xcbf29ce484222325'},  # Note: JEV rejects literal
    {'kind': 'fact', 'name': 'thirteen ports', 'p': 0.08, 'hash': '0xcbf29ce484222325'},  # Note: JEV rejects literal
    {'kind': 'fact', 'name': 'substrate_self_pred', 'p': 0.75, 'hash': '0xcbf29ce484222325'},  # NEW canon
    # Distractors (for canon-vs-noise distinction)
    {'kind': 'distractor', 'name': 'cells are parameters', 'p': 0.04, 'hash': '0x0000'},
    {'kind': 'distractor', 'name': 'witness log is past only', 'p': 0.13, 'hash': '0x0000'},
    {'kind': 'distractor', 'name': 'substrate is designed', 'p': 0.03, 'hash': '0x0000'},
    {'kind': 'distractor', 'name': 'oracle is stored', 'p': 0.03, 'hash': '0x0000'},
    {'kind': 'distractor', 'name': 'transformer attention', 'p': 0.69, 'hash': '0x0000'},  # canon-as-distractor
]

# ============ Level generation ============
def generate_level(level_num, canon_items, n_canons=5, n_distractors=5):
    """One level = some canon items + some distractors, in random order."""
    canon_pool = [c for c in canon_items if c['kind'] != 'distractor']
    distractor_pool = [c for c in canon_items if c['kind'] == 'distractor']

    canons = random.sample(canon_pool, min(n_canons, len(canon_pool)))
    distractors = random.sample(distractor_pool, min(n_distractors, len(distractor_pool)))
    items = canons + distractors
    random.shuffle(items)
    return {
        'level': level_num,
        'items': items,
        'expected_score': sum(c['p'] for c in items) * 100,
        'n_canon': len(canons),
        'n_distract': len(distractors),
    }

def generate_levels(n_levels=20, canon_items=None):
    """Generate n procedural levels from canon."""
    if canon_items is None:
        canon_items = CANON_ITEMS

    levels = []
    for i in range(1, n_levels + 1):
        # Difficulty scales: more distractors at higher levels
        n_d = min(8, 3 + i // 5)
        n_c = max(2, 6 - i // 10)
        level = generate_level(i, canon_items, n_canons=n_c, n_distractors=n_d)
        levels.append(level)
    return levels

# ============ Witness log bridge ============
def simulate_game_session(levels, player_id='player_1'):
    """Simulate a player going through levels. Record witness log."""
    witness = []
    state = '0xcbf29ce484222325'  # FNV-1a canary

    for level in levels:
        score = 0
        streak = 0
        for item in level['items']:
            # Player clicks canon/distractor
            # True model: canon items have p > 0.5, distractors p < 0.5
            is_canon = item['kind'] != 'distractor'
            spike_p = item['p']
            spike_passed = spike_p > 0.5  # threshold

            if is_canon and spike_passed:
                score += int(spike_p * 100)
                streak += 1
            elif not is_canon and spike_passed:
                score -= 50
                streak = 0
            else:
                streak = 0

            # Witness entry
            witness.append({
                'level': level['level'],
                'phrase': item['name'],
                'kind': item['kind'],
                'p': spike_p,
                'spike_passed': spike_passed,
                'reward': int(spike_p * 100) if (is_canon and spike_passed) else (-50 if spike_passed else 0),
                'streak': streak,
            })

        # FNV-1a chaining: next state = hash(prev + level)
        prev_state = state
        state = hashlib.sha1(f"{state}|L{level['level']}|S{score}".encode()).hexdigest()

    return {
        'player_id': player_id,
        'final_score': sum(w['reward'] for w in witness),
        'best_streak': max(w['streak'] for w in witness),
        'witness': witness,
    }

def main():
    print('=== Signal-Chain Game: Canon Integration ===\n')

    print('Generating 20 levels from canon...')
    levels = generate_levels(20)
    print(f'Levels: {len(levels)}')
    print(f'Sample level 1: {levels[0]["n_canon"]} canons + {levels[0]["n_distract"]} distractors')
    print(f'Sample level 20: {levels[19]["n_canon"]} canons + {levels[19]["n_distract"]} distractors\n')

    print('Simulating 3 players...')
    results = []
    for pid in ['player_1', 'player_2', 'player_3']:
        r = simulate_game_session(levels, player_id=pid)
        results.append(r)
        print(f'  {pid}: final_score={r["final_score"]}  best_streak={r["best_streak"]}  witness_entries={len(r["witness"])}')

    # Save level generator script for game
    out = {
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'levels': levels,
        'simulations': results,
        'canon_items_count': len(CANON_ITEMS),
    }

    fname = '/workspace/research/signal_chain_game_canon_levels.json'
    with open(fname, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: {fname}')

    # Print level generator (Python)
    gen_py = '''#!/usr/bin/env python3
"""Generated canon-level generator for signal-chain-game.

Reads /api/jev/canon-oracle to get canon pieces, then generates levels.
"""
import json
import urllib.request
import random

CANON_ITEMS_URL = '/api/canon?kind=canon&limit=50'

def fetch_canon():
    """Fetch canon pieces from the live API."""
    with urllib.request.urlopen(f'http://localhost:8787{CANON_ITEMS_URL}') as r:
        return json.loads(r.read())

def generate_levels(canon_items, n_levels=20):
    levels = []
    for i in range(1, n_levels + 1):
        n_d = min(8, 3 + i // 5)
        n_c = max(2, 6 - i // 10)
        items = random.sample(canon_items, min(n_c + n_d, len(canon_items)))
        random.shuffle(items)
        levels.append({'level': i, 'items': items, 'n_canon': n_c, 'n_distract': n_d})
    return levels

if __name__ == '__main__':
    canon = fetch_canon()
    levels = generate_levels(canon, n_levels=20)
    print(json.dumps(levels, indent=2))
'''
    with open('/workspace/research/canon_level_gen.py', 'w') as f:
        f.write(gen_py)
    print('Saved: /workspace/research/canon_level_gen.py')

if __name__ == '__main__':
    main()
