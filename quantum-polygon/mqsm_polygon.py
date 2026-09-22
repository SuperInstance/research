"""MQSM (Multi-channel Quantum State Modulation) for polygon features.

JEV says (p=0.37): try MQSM. Each polygon feature (angles, lengths, radii)
becomes a quantum channel. The multi-channel encoding preserves more geometric
structure than single-channel QSM.

Hypothesis: canon polygons cluster in MQSM state space; random polygons don't.
"""
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")
import qsm_polygon as qp


def polygon_multichannel(seed, n_vertices=8):
    """Encode polygon features as multi-channel audio."""
    rng = np.random.default_rng(seed)
    base = rng.uniform(0, 2 * np.pi, n_vertices)
    angles = np.sort(base)
    lengths = 1.0 + 0.3 * np.sin(angles * (seed % 7 + 1))
    radii = np.sqrt(lengths**2 + np.sin(angles)**2)
    return np.array([angles, lengths, radii])  # 3 channels x 8 samples


def mqsm_statevector(seed, n_vertices=8):
    """Encode polygon as MQSM and get statevector."""
    import quantumaudio as qa
    mc = polygon_multichannel(seed, n_vertices)
    # Flatten multi-channel into single signal: ch0, ch1, ch2, ch0, ch1, ch2, ...
    audio = mc.flatten()
    circuit = qa.encode(audio, scheme="QSM")
    
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    circuit.save_statevector()
    sim = AerSimulator(method="statevector")
    tc = transpile(circuit, sim)
    res = sim.run(tc).result()
    return np.array(res.get_statevector()), mc


def mqsm_circuit_signature(seed, n_vertices=8):
    """Get MQSM circuit structure as signature."""
    import quantumaudio as qa
    mc = polygon_multichannel(seed, n_vertices)
    audio = mc.flatten()
    circuit = qa.encode(audio, scheme="QSM")
    
    n_mcx = sum(1 for instr in circuit.data if instr.operation.name == 'mcx')
    return {
        'seed': seed,
        'depth': circuit.depth(),
        'size': circuit.size(),
        'n_mcx': n_mcx,
        'n_qubits': circuit.num_qubits,
    }


def run_study():
    # 30 canon + 30 random
    gm = json.load(open('/workspace/research/substrate-walker/playtest/great_moments.json'))
    canon_seeds = [m['seed'] for m in sorted(gm, key=lambda x: -x.get('score', 0))[:30]]
    
    import random
    random.seed(42)
    random_seeds = random.sample(range(1, 100_000_000), 30)
    
    canon_sigs = []
    random_sigs = []
    
    print("Canon signatures (MQSM):")
    for seed in canon_seeds:
        sig = mqsm_circuit_signature(seed)
        canon_sigs.append(sig)
        print(f"  seed {seed}: depth={sig['depth']} size={sig['size']} mcx={sig['n_mcx']}")
    
    print("\nRandom signatures (MQSM):")
    for seed in random_seeds:
        sig = mqsm_circuit_signature(seed)
        random_sigs.append(sig)
        print(f"  seed {seed}: depth={sig['depth']} size={sig['size']} mcx={sig['n_mcx']}")
    
    # Stats
    from statistics import mean, stdev
    canon_mcx = [s['n_mcx'] for s in canon_sigs]
    random_mcx = [s['n_mcx'] for s in random_sigs]
    
    canon_depth = [s['depth'] for s in canon_sigs]
    random_depth = [s['depth'] for s in random_sigs]
    
    print("\n=== MQSM RESULTS ===")
    print(f"Canon n={len(canon_mcx)}: MCX mean={mean(canon_mcx):.2f} std={stdev(canon_mcx):.2f}")
    print(f"Random n={len(random_mcx)}: MCX mean={mean(random_mcx):.2f} std={stdev(random_mcx):.2f}")
    print(f"Difference: {mean(canon_mcx) - mean(random_mcx):+.2f}")
    print(f"Depth: canon={mean(canon_depth):.2f}, random={mean(random_depth):.2f}")
    
    # Save
    output = {
        'canon': canon_sigs,
        'random': random_sigs,
        'canon_mean_mcx': mean(canon_mcx),
        'canon_std_mcx': stdev(canon_mcx),
        'random_mean_mcx': mean(random_mcx),
        'random_std_mcx': stdev(random_mcx),
    }
    with open('/workspace/research/quantum-polygon/mqsm_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nSaved mqsm_results.json")
    return output


if __name__ == "__main__":
    run_study()
