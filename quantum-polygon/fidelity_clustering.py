"""Test if canon polygon seeds cluster in quantum state space.

JEV says: try fidelity_cluster at p=0.70.

Measure statevector fidelity between all pairs of canon seeds.
Compare to fidelity distribution for random seeds.

If canon seeds cluster, we see higher intra-canon fidelity than intra-random fidelity.
"""
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")
import qsm_polygon as qp


def statevector(seed):
    """Get the QSM statevector for a polygon."""
    import quantumaudio as qa
    audio = qp.polygon_to_audio(seed, 16)
    circuit = qa.encode(audio, scheme="QSM")
    
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    circuit.save_statevector()
    sim = AerSimulator(method="statevector")
    tc = transpile(circuit, sim)
    res = sim.run(tc).result()
    return np.array(res.get_statevector())


def fidelity(sv1, sv2):
    return float(np.abs(np.vdot(sv1, sv2)) ** 2)


def run_study():
    # Canon seeds (top 30 by lore score)
    gm = json.load(open('/workspace/research/substrate-walker/playtest/great_moments.json'))
    canon_seeds = sorted(gm, key=lambda x: -x.get('score', 0))[:30]
    canon_seed_list = [m['seed'] for m in canon_seeds]
    
    # Random seeds (30)
    import random
    random.seed(42)
    random_seeds = random.sample(range(1, 100_000_000), 30)
    
    # Get statevectors
    print("Computing statevectors...")
    canon_svs = {}
    for seed in canon_seed_list:
        canon_svs[seed] = statevector(seed)
        print(f"  canon {seed} ok")
    
    random_svs = {}
    for seed in random_seeds:
        random_svs[seed] = statevector(seed)
        print(f"  random {seed} ok")
    
    # Compute all pairwise fidelities
    canon_pairs = []
    for i, s1 in enumerate(canon_seed_list):
        for s2 in canon_seed_list[i+1:]:
            f = fidelity(canon_svs[s1], canon_svs[s2])
            canon_pairs.append((s1, s2, f))
    
    random_pairs = []
    for i, s1 in enumerate(random_seeds):
        for s2 in random_seeds[i+1:]:
            f = fidelity(random_svs[s1], random_svs[s2])
            random_pairs.append((s1, s2, f))
    
    cross_pairs = []
    for s1 in canon_seed_list:
        for s2 in random_seeds:
            f = fidelity(canon_svs[s1], random_svs[s2])
            cross_pairs.append((s1, s2, f))
    
    # Stats
    from statistics import mean, stdev
    canon_fids = [p[2] for p in canon_pairs]
    random_fids = [p[2] for p in random_pairs]
    cross_fids = [p[2] for p in cross_pairs]
    
    print("\n=== FIDELITY DISTRIBUTIONS ===")
    print(f"Canon-canon (n={len(canon_fids)}): mean={mean(canon_fids):.4f} std={stdev(canon_fids):.4f}")
    print(f"Random-random (n={len(random_fids)}): mean={mean(random_fids):.4f} std={stdev(random_fids):.4f}")
    print(f"Canon-random (n={len(cross_fids)}): mean={mean(cross_fids):.4f} std={stdev(cross_fids):.4f}")
    
    # Find canon pairs with HIGH fidelity (cluster candidates)
    high_fid_canon = [p for p in canon_pairs if p[2] > 0.5]
    print(f"\nHigh-fidelity canon pairs (F>0.5): {len(high_fid_canon)}/{len(canon_pairs)}")
    for s1, s2, f in sorted(high_fid_canon, key=lambda x: -x[2])[:5]:
        print(f"  seeds {s1}, {s2}: F={f:.4f}")
    
    # Save
    output = {
        'canon_seed_count': len(canon_seed_list),
        'random_seed_count': len(random_seeds),
        'canon_canon_fidelities': canon_fids,
        'random_random_fidelities': random_fids,
        'canon_random_fidelities': cross_fids,
        'canon_canon_mean': mean(canon_fids),
        'canon_canon_std': stdev(canon_fids),
        'random_random_mean': mean(random_fids),
        'random_random_std': stdev(random_fids),
        'canon_random_mean': mean(cross_fids),
        'canon_random_std': stdev(cross_fids),
        'high_fidelity_canon_pairs': [{'s1': s[0], 's2': s[1], 'fidelity': s[2]} for s in high_fid_canon[:20]],
    }
    with open('/workspace/research/quantum-polygon/fidelity_clustering.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nSaved fidelity_clustering.json")
    return output


if __name__ == "__main__":
    run_study()
