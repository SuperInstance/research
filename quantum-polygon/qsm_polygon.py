"""Quantum polygon encoding — encode polygon vertex sequences as QSM quantum states.

This is the giant polygon deep-dive. The hypothesis: encoding polygon vertex
sequences as quantum states reveals invariants invisible to classical mining.

Each polygon vertex (angle, length, radius) becomes:
- amplitude qubit: the vertex value (normalized)
- time register qubits: the vertex index

The QSM circuit encodes the polygon's "rhythm" as a quantum state. Then we:
1. Measure many shots → histogram
2. Compute statevector fidelity between polygons
3. Look for clustering that maps to lore quality

References:
- quantumaudio QSM: https://github.com/moth-quantum/quantum-audio
- QSM original paper: FRQA — https://doi.org/10.1016/j.tcs.2017.12.025
"""
import sys
import time
import json
import math
import numpy as np
from pathlib import Path

sys.path.insert(0, "/usr/local/lib/python3.11/dist-packages")

# Lazy qiskit import (slow)
_QRUN = None


def _qrun():
    global _QRUN
    if _QRUN is None:
        import quantumaudio as qa
        _QRUN = qa
    return _QRUN


def polygon_to_audio(seed: int, n_vertices: int = 16, sample_rate: int = 4000) -> np.ndarray:
    """Map a polygon seed to an audio waveform.

    The vertex angles are computed from seed % polygon_number(n).
    Polygon number P(s, n) = (s/4)(n-2)(n-2s+2) for s-sided polygons.

    For P(n) = n(n-1)/2 (triangular numbers), the nth polygon has n sides.
    """
    # Use seed as starting angle, generate n vertex angles via the seed
    rng = np.random.default_rng(seed)
    base = rng.uniform(0, 2 * np.pi, n_vertices)

    # Sort angles for closed polygon
    angles = np.sort(base)

    # Compute edge lengths as a function of (angle, seed)
    lengths = 1.0 + 0.3 * np.sin(angles * (seed % 7 + 1))

    # Interleave angles and lengths into a single signal
    signal = np.zeros(n_vertices * 2)
    signal[0::2] = np.sin(angles)
    signal[1::2] = lengths - 1.0  # centered

    return signal * 0.5  # normalize to [-0.5, 0.5]


def encode_polygon_qsm(seed: int, n_vertices: int = 16):
    """Encode a polygon as a QSM quantum circuit.

    Returns: (circuit, decoded_audio, error)
    """
    qa = _qrun()
    audio = polygon_to_audio(seed, n_vertices)
    n = len(audio)
    n_qubits = int(math.ceil(math.log2(max(n, 2))))

    t0 = time.time()
    circuit = qa.encode(audio, scheme="QSM")
    enc_time = time.time() - t0

    t0 = time.time()
    decoded = qa.decode(circuit, scheme="QSM")
    dec_time = time.time() - t0

    err = float(np.abs(audio - decoded[:n]).mean())

    return {
        "seed": seed,
        "n_vertices": n_vertices,
        "audio_len": n,
        "n_qubits": circuit.num_qubits,
        "circuit_depth": circuit.depth(),
        "encode_time_s": enc_time,
        "decode_time_s": dec_time,
        "roundtrip_error": err,
    }


def quantum_fingerprint(seed: int, n_vertices: int = 16, n_shots: int = 1000):
    """Get a measurement histogram as a 'quantum fingerprint' for the polygon.

    The histogram captures the dominant basis states when the circuit is measured.
    Two polygons with similar fingerprints have similar geometric structure.
    """
    qa = _qrun()
    audio = polygon_to_audio(seed, n_vertices)

    circuit = qa.encode(audio, scheme="QSM")

    # Try to get measurement results
    try:
        from qiskit_aer import AerSimulator
        from qiskit import QuantumCircuit, transpile
        sim = AerSimulator()
        circuit.measure_all()
        t_circuit = transpile(circuit, sim)
        result = sim.run(t_circuit, shots=n_shots).result()
        counts = result.get_counts()
    except Exception as e:
        counts = {"error": str(e)}

    # Compute Shannon entropy of the histogram
    valid_counts = {k: v for k, v in counts.items() if not str(k).startswith("error")}
    total = sum(valid_counts.values())
    if total > 0:
        probs = [v / total for v in valid_counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
    else:
        entropy = 0.0

    # Top-3 measurement outcomes (deterministic structure)
    sorted_counts = sorted(valid_counts.items(), key=lambda x: -x[1])[:5]

    return {
        "seed": seed,
        "n_unique_outcomes": len(counts),
        "shannon_entropy": entropy,
        "top_outcomes": sorted_counts[:3],
        "n_shots": n_shots,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("QUANTUM POLYGON ENCODER — Giant polygon deep dive")
    print("=" * 60)
    print()

    # Test on the top-5 substrate walker canon seeds
    top5_seeds = [70051917, 4685000, 3289967, 57322595, 90625407]

    results = []
    for seed in top5_seeds:
        print(f"\nSeed {seed}:")
        try:
            enc = encode_polygon_qsm(seed, n_vertices=16)
            print(f"  Qubits: {enc['n_qubits']}, Depth: {enc['circuit_depth']}")
            print(f"  Encode: {enc['encode_time_s']:.2f}s, Decode: {enc['decode_time_s']:.2f}s")
            print(f"  Round-trip error: {enc['roundtrip_error']:.4f}")

            fp = quantum_fingerprint(seed, n_vertices=16, n_shots=500)
            print(f"  Quantum fingerprint: {fp['n_unique_outcomes']} unique outcomes")
            print(f"  Shannon entropy: {fp['shannon_entropy']:.3f}")
            print(f"  Top outcome: {fp['top_outcomes'][0] if fp['top_outcomes'] else 'none'}")

            results.append({"encode": enc, "fingerprint": fp})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"seed": seed, "error": str(e)})

    out_path = Path("/workspace/research/quantum-polygon/results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
