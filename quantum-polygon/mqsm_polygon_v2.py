"""MQSM polygon experiment v2 — properly normalized multi-channel audio."""
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")


def polygon_multichannel(seed, n_vertices=8):
    """Encode polygon as 3-channel audio normalized to [-1, 1]."""
    rng = np.random.default_rng(seed)
    base = rng.uniform(0, 2 * np.pi, n_vertices)
    angles = np.sort(base)
    lengths = 1.0 + 0.3 * np.sin(angles * (seed % 7 + 1))
    radii = np.sqrt(lengths**2 + np.sin(angles)**2)
    
    angles_n = (angles - np.pi) / np.pi
    lengths_n = (lengths - 1.15) / 0.15
    radii_n = (radii - 1.15) / 0.5
    
    return np.clip(np.array([angles_n, lengths_n, radii_n]), -1.0, 1.0)


def mqsm_signature(seed, n_vertices=8):
    """Get MQSM circuit signature."""
    import quantumaudio as qa
    mc = polygon_multichannel(seed, n_vertices)
    audio = mc.flatten()
    
    try:
        circuit = qa.encode(audio, scheme="QSM")
        n_mcx = sum(1 for instr in circuit.data if instr.operation.name == 'mcx')
        return {
            'seed': seed,
            'depth': circuit.depth(),
            'size': circuit.size(),
            'n_mcx': n_mcx,
            'n_qubits': circuit.num_qubits,
        }
    except Exception as e:
        return {'seed': seed, 'error': str(e)}


def run_study():
    gm = json.load(open('/workspace/research/substrate-walker/playtest/great_moments.json'))
    canon_seeds = [m['seed'] for m in sorted(gm, key=lambda x: -x.get('score', 0))[:30]]
    
    import random
    random.seed(42)
    random_seeds = random.sample(range(1, 100_000_000), 30)
    
    canon_sigs = []
    random_sigs = []
    
    print("Canon MQSM signatures:")
    for seed in canon_seeds:
        sig = mqsm_signature(seed)
        if 'error' not in sig:
            canon_sigs.append(sig)
        print(f"  seed {seed}: {sig}")
    
    print("\nRandom MQSM signatures:")
    for seed in random_seeds:
        sig = mqsm_signature(seed)
        if 'error' not in sig:
            random_sigs.append(sig)
        print(f"  seed {seed}: {sig}")
    
    from statistics import mean, stdev
    canon_mcx = [s['n_mcx'] for s in canon_sigs]
    random_mcx = [s['n_mcx'] for s in random_sigs]
    
    print(f"\n=== MQSM RESULTS ===")
    print(f"Canon n={len(canon_mcx)}: MCX mean={mean(canon_mcx):.2f} std={stdev(canon_mcx):.2f}")
    print(f"Random n={len(random_mcx)}: MCX mean={mean(random_mcx):.2f} std={stdev(random_mcx):.2f}")
    print(f"Difference: {mean(canon_mcx) - mean(random_mcx):+.2f}")
    
    output = {
        'canon': canon_sigs,
        'random': random_sigs,
        'canon_mean_mcx': mean(canon_mcx),
        'canon_std_mcx': stdev(canon_mcx),
        'random_mean_mcx': mean(random_mcx),
        'random_std_mcx': stdev(random_mcx),
    }
    with open('/workspace/research/quantum-polygon/mqsm_results_v2.json', 'w') as f:
        json.dump(output, f, indent=2)
    return output


if __name__ == "__main__":
    run_study()
