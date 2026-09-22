"""Large MCX gate count study — 200 canon + 200 random polygon seeds.

JEV says: 4.65 gate difference on n=20 is "noise, expand to 200+".
This experiment validates the hypothesis at scale.
"""
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")
import qsm_polygon as qp


def measure_mcx(seed):
    """Get the MCX gate count for a polygon's QSM encoding."""
    import quantumaudio as qa
    audio = qp.polygon_to_audio(seed, 16)
    circuit = qa.encode(audio, scheme="QSM")
    n = 0
    for instr in circuit.data:
        if instr.operation.name == 'mcx':
            n += 1
    return n, circuit.depth(), circuit.size()


def run_study():
    # Load canon seeds
    gm = json.load(open('/workspace/research/substrate-walker/playtest/great_moments.json'))
    canon_seeds = sorted(gm, key=lambda x: -x.get('score', 0))[:200]
    canon_seed_list = [m['seed'] for m in canon_seeds]
    
    # Random seeds
    import random
    random.seed(42)
    random_seeds = random.sample(range(1, 100_000_000), 200)
    
    results = {'canon': {}, 'random': {}}
    
    print(f"Measuring canon seeds ({len(canon_seed_list)})...")
    t0 = time.time()
    for i, seed in enumerate(canon_seed_list):
        try:
            mcx, depth, size = measure_mcx(seed)
            results['canon'][seed] = {'mcx': mcx, 'depth': depth, 'size': size}
            if i % 20 == 0:
                print(f"  {i+1}/{len(canon_seed_list)}: seed={seed} mcx={mcx}")
        except Exception as e:
            print(f"  ERROR seed={seed}: {e}")
    print(f"Canon done in {time.time()-t0:.1f}s")
    
    print(f"\nMeasuring random seeds ({len(random_seeds)})...")
    t0 = time.time()
    for i, seed in enumerate(random_seeds):
        try:
            mcx, depth, size = measure_mcx(seed)
            results['random'][seed] = {'mcx': mcx, 'depth': depth, 'size': size}
            if i % 20 == 0:
                print(f"  {i+1}/{len(random_seeds)}: seed={seed} mcx={mcx}")
        except Exception as e:
            print(f"  ERROR seed={seed}: {e}")
    print(f"Random done in {time.time()-t0:.1f}s")
    
    # Analysis
    canon_mcx = [d['mcx'] for d in results['canon'].values()]
    random_mcx = [d['mcx'] for d in results['random'].values()]
    
    canon_depth = [d['depth'] for d in results['canon'].values()]
    random_depth = [d['depth'] for d in results['random'].values()]
    
    canon_size = [d['size'] for d in results['canon'].values()]
    random_size = [d['size'] for d in results['random'].values()]
    
    # t-test
    from statistics import mean, stdev
    canon_mean = mean(canon_mcx)
    canon_std = stdev(canon_mcx)
    random_mean = mean(random_mcx)
    random_std = stdev(random_mcx)
    
    # Welch's t-test
    n1, n2 = len(canon_mcx), len(random_mcx)
    s1_sq, s2_sq = canon_std**2, random_std**2
    t = (canon_mean - random_mean) / ((s1_sq/n1 + s2_sq/n2) ** 0.5)
    
    # Cohen's d
    pooled_std = ((s1_sq + s2_sq) / 2) ** 0.5
    cohen_d = (random_mean - canon_mean) / pooled_std
    
    summary = {
        'canon_n': n1,
        'random_n': n2,
        'canon_mean_mcx': canon_mean,
        'canon_std_mcx': canon_std,
        'random_mean_mcx': random_mean,
        'random_std_mcx': random_std,
        'difference': random_mean - canon_mean,
        'welch_t': t,
        'cohen_d': cohen_d,
        'canon_mean_depth': mean(canon_depth),
        'random_mean_depth': mean(random_depth),
        'canon_mean_size': mean(canon_size),
        'random_mean_size': mean(random_size),
    }
    
    print("\n=== RESULTS ===")
    print(f"Canon n={n1}: MCX mean={canon_mean:.2f} std={canon_std:.2f}")
    print(f"Random n={n2}: MCX mean={random_mean:.2f} std={random_std:.2f}")
    print(f"Difference: {random_mean - canon_mean:.2f} (positive = canon simpler)")
    print(f"Welch's t: {t:.3f}")
    print(f"Cohen's d: {cohen_d:.3f}")
    print(f"Depth: canon={mean(canon_depth):.2f}, random={mean(random_depth):.2f}")
    print(f"Size: canon={mean(canon_size):.2f}, random={mean(random_size):.2f}")
    
    # Save
    output = {
        'summary': summary,
        'canon_results': results['canon'],
        'random_results': results['random'],
    }
    with open('/workspace/research/quantum-polygon/large_mcx_study.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nSaved large_mcx_study.json")


if __name__ == "__main__":
    run_study()
