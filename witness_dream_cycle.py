#!/usr/bin/env python3
"""Witness Dream Cycle — REM sleep for the substrate's witness log."""
import json, os, time, glob
from collections import defaultdict

def fnv1a(s):
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

def main():
    print('=== Witness Dream Cycle ===\n')

    session_files = sorted(glob.glob('/workspace/repos/jev-quilt/jev_sessions/*.json'))
    print(f'Found {len(session_files)} session files')

    dream_pool = []
    for sf in session_files:
        try:
            with open(sf) as f:
                d = json.load(f)
            session = os.path.basename(sf).replace('.json', '')

            if 'results' in d and isinstance(d['results'], list):
                for r in d['results']:
                    if 'mean_p' in r:
                        text = r.get('file', r.get('phrase', '?'))
                        success = r['mean_p'] >= 0.70
                        dream_pool.append({
                            'id': fnv1a(text) & 0xFFFFFFFF,
                            'input': text,
                            'success': success,
                            'reward': r['mean_p'],
                            'source': session,
                            'verdict': r.get('verdict', ''),
                        })

            elif 'decisions' in d and isinstance(d['decisions'], list) and 'questions' in d:
                qs = d['questions']
                ds = d['decisions']
                for q, dec in zip(qs, ds):
                    # Question: ['name', 'type', 'instructions']
                    # Decision: ['type', 'value_str', value_float, receipt]
                    if isinstance(q, list) and len(q) >= 3 and isinstance(dec, list) and len(dec) >= 3:
                        text = q[2] if isinstance(q[2], str) else str(q[2])
                        try:
                            p = float(dec[2])  # value as float
                        except:
                            try:
                                p = float(dec[1])  # value as string
                            except:
                                p = 0
                        success = p >= 0.70
                        dream_pool.append({
                            'id': fnv1a(text) & 0xFFFFFFFF,
                            'input': text,
                            'success': success,
                            'reward': p,
                            'source': session,
                            'verdict': '',
                        })
        except Exception as e:
            print(f'  Skip {os.path.basename(sf)}: {e}')
            continue

    print(f'Loaded {len(dream_pool)} experiences from {len(session_files)} sessions\n')

    successes = [e for e in dream_pool if e['success']]
    failures = [e for e in dream_pool if not e['success']]
    print(f'  Successes (p >= 0.70): {len(successes)}')
    print(f'  Failures (p < 0.70):   {len(failures)}')
    if dream_pool:
        print(f'  Success rate: {len(successes)/len(dream_pool):.3f}')

    print('\n--- Failure clusters (top 15) ---')
    clusters = defaultdict(list)
    for f in failures:
        prefix = f['input'][:30].strip()
        clusters[prefix].append(f)

    patterns = []
    for prefix, items in sorted(clusters.items(), key=lambda x: -len(x[1]))[:15]:
        avg_reward = sum(i['reward'] for i in items) / len(items)
        patterns.append({
            'description': f'Cluster around: "{prefix}..."',
            'sample_count': len(items),
            'avg_reward': avg_reward,
            'tags': ['failure-cluster'],
            'is_success_pattern': False,
            'examples': [i['input'][:80] for i in items[:3]],
        })
        print(f'  {prefix[:33]:35s}  count={len(items):3d}  avg_p={avg_reward:.3f}')

    print('\n--- Success clusters (top 15) ---')
    success_clusters = defaultdict(list)
    for s in successes:
        prefix = s['input'][:30].strip()
        success_clusters[prefix].append(s)

    success_patterns = []
    for prefix, items in sorted(success_clusters.items(), key=lambda x: -len(x[1]))[:15]:
        avg_reward = sum(i['reward'] for i in items) / len(items)
        success_patterns.append({
            'description': f'Success cluster: "{prefix}..."',
            'sample_count': len(items),
            'avg_reward': avg_reward,
            'tags': ['success-cluster'],
            'is_success_pattern': True,
            'examples': [i['input'][:80] for i in items[:3]],
        })
        print(f'  {prefix[:33]:35s}  count={len(items):3d}  avg_p={avg_reward:.3f}')

    out = {
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'dream_pool_size': len(dream_pool),
        'successes': len(successes),
        'failures': len(failures),
        'success_rate': len(successes)/len(dream_pool) if dream_pool else 0,
        'failure_patterns': patterns[:10],
        'success_patterns': success_patterns[:10],
    }
    fname = '/workspace/research/witness_dream_cycle_results.json'
    with open(fname, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: {fname}')

if __name__ == '__main__':
    main()
