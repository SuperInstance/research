#!/usr/bin/env python3
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
