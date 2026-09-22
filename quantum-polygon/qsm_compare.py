"""Compare quantum fingerprints of polygon seeds.

Hypothesis: lores that come from similar polygon seeds should have similar
quantum fingerprints. The fidelity between two quantum states tells us how
"close" two polygons are in the substrate's geometric space.
"""
import sys
import math
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")
import qsm_polygon as qp


def statevector_from_audio(audio: np.ndarray):
    """Get the QSM statevector (not measured)."""
    qa = qp._qrun()
    circuit = qa.encode(audio, scheme="QSM")
    # Get the statevector from the simulator
    try:
        from qiskit_aer import AerSimulator
        from qiskit import transpile
        # Save statevector
        circuit.save_statevector()
        sim = AerSimulator(method="statevector")
        t_circuit = transpile(circuit, sim)
        result = sim.run(t_circuit).result()
        sv = result.get_statevector()
        return np.array(sv)
    except Exception as e:
        return None


def fidelity(sv1, sv2):
    """Quantum state fidelity |<psi1|psi2>|^2."""
    if sv1 is None or sv2 is None:
        return None
    overlap = np.abs(np.vdot(sv1, sv2)) ** 2
    return float(overlap)


if __name__ == "__main__":
    # Compare top canon seeds
    top5 = [70051917, 4685000, 3289967, 57322595, 90625407]
    # And a few "control" seeds (presumably lower quality)
    controls = [1234567, 9999999, 314159, 2718281, 1618033]

    print("Computing statevectors for top-5 canon seeds...")
    canon_svs = {}
    for seed in top5:
        audio = qp.polygon_to_audio(seed, 16)
        sv = statevector_from_audio(audio)
        if sv is not None:
            canon_svs[seed] = sv
            print(f"  seed {seed}: sv norm={np.linalg.norm(sv):.3f}, dim={len(sv)}")

    print("\nComputing statevectors for control seeds...")
    control_svs = {}
    for seed in controls:
        audio = qp.polygon_to_audio(seed, 16)
        sv = statevector_from_audio(audio)
        if sv is not None:
            control_svs[seed] = sv
            print(f"  seed {seed}: sv norm={np.linalg.norm(sv):.3f}, dim={len(sv)}")

    # Fidelity matrix for canon seeds
    print("\nFidelity matrix (canon):")
    print("       ", "  ".join(f"{s:>9}" for s in top5))
    for s1 in top5:
        row = [f"{s1:>9}"]
        for s2 in top5:
            if s1 == s2:
                row.append(f"{'1.000':>9}")
            else:
                f = fidelity(canon_svs.get(s1), canon_svs.get(s2))
                row.append(f"{f:>9.4f}")
        print(" ".join(row))

    # Fidelity matrix for controls
    print("\nFidelity matrix (controls):")
    print("       ", "  ".join(f"{s:>9}" for s in controls))
    for s1 in controls:
        row = [f"{s1:>9}"]
        for s2 in controls:
            if s1 == s2:
                row.append(f"{'1.000':>9}")
            else:
                f = fidelity(control_svs.get(s1), control_svs.get(s2))
                row.append(f"{f:>9.4f}")
        print(" ".join(row))

    # Cross fidelity (canon vs control)
    print("\nCross fidelity (canon vs control):")
    print("       ", "  ".join(f"{s:>9}" for s in controls))
    for s1 in top5:
        row = [f"{s1:>9}"]
        for s2 in controls:
            f = fidelity(canon_svs.get(s1), control_svs.get(s2))
            row.append(f"{f:>9.4f}")
        print(" ".join(row))
