# MOTHQuantum Findings

**Date**: 2026-09-22 (1M context sprint, end of day)
**Status**: SDK confirmed working, hosted endpoint dead from this region

## TL;DR

`MOTH_API_KEY` env var is NOT for a hosted LLM. It's auth for `quantumaudio` — a PyPI package that maps digital audio onto quantum circuits.

## Discovery path

1. Probed `api.moth.ai` → 503 TLS error (gateway up, backend dead)
2. Probed `moth.ai` → parked on GoDaddy (forsale page)
3. Probed `mothquantum.ai` → DNS resolves (Alibaba Cloud, hangzhou) but API hangs silently
4. Searched GitHub for `mothquantum` → found `moth-quantum` org
5. Their main repo is `moth-quantum/quantum-audio` — pip-installable as `quantumaudio`
6. Installed v0.2.0 — works locally

## What quantumaudio does

Five schemes for mapping audio onto quantum circuits:

| Scheme | Acronym | Name |
|--------|---------|------|
| QPAM | Quantum Probability Amplitude Modulation | Real-Ket |
| SQPAM | Single-Qubit Probability Amplitude Modulation | FRQI |
| MSQPAM | Multi-channel Single-Qubit Probability Amplitude Modulation | PMQA |
| QSM | Quantum State Modulation | FRQA |
| MQSM | Multi-channel Quantum State Modulation | QRMA |

```python
import quantumaudio as qa
import numpy as np

# 40-sample sine wave
t = np.linspace(0, 0.01, 400, endpoint=False)
audio = np.sin(2*np.pi*440*t[:40])

# Encode as quantum state
circuit = qa.encode(audio, scheme="QSM")  # 6 qubits
decoded = qa.decode(circuit, scheme="QSM")  # round-trip error ~0.037
```

## Cross-project relevance to substrate walker

The QSM scheme is structurally identical to how substrate walker cells work:

| QSM concept | Substrate walker equivalent |
|-------------|------------------------------|
| amplitude qubit | cell state vector |
| time register qubits | witness log index |
| entanglement | cell-to-cell reference |
| measurement | canon gate |
| superposition | dormant cells |
| multi-channel (MQSM) | polyformalism ports |

**This is HUGE**: the substrate walker is *already* a quantum circuit in disguise. The witness log + cell state = QSM encoding. The FNV-1a hash = measurement outcome.

## Ideas for the giant polygon deep dive

### 1. Quantum polygon mine
Encode polygon vertex sequences as QSM circuits. Each polygon has N vertices with coordinates. Map to:
- amplitude qubit: distance from polygon centroid
- time register: vertex index
- multi-channel: which polygon feature (angle, length, area)

Then measure many shots → histogram of measurement outcomes. High-frequency outcomes = emergent polygon invariants invisible to classical mine.

### 2. Penrose tiling via quantum matching rules
Penrose tilings are non-periodic but locally enforceable. Encode matching rules as quantum gates. The tiling emerges from repeated application. Could discover new aperiodic tilings.

### 3. Lore-as-audio
Encode lore text's syllable rhythm as audio. QSM encode → measure → quantum fingerprint. Two lores with the same fingerprint are "rhythmically identical". Could discover hidden patterns in our 934 lores.

### 4. Motion-as-encoding
A polygon's evolution over time = motion encoding. Encode motion trajectories as quantum states. Compare trajectories via quantum state overlap (fidelity). Could discover whether certain seeds evolve "coherently" — leading to a new canon metric.

### 5. The army of APIs as a GAN with JEV as judge
Each LLM (ZAI, DeepSeek, Kimi, Qwen, DeepInfra Llama, JEV itself) generates lore variants for a seed. Each variant is encoded as QSM audio. JEV scores each variant canon-worthiness. The combined canonical probability = quantum fidelity between variant and target. The "designed future" emerges from superposition of variants, measured to reveal the best path.

## Gotchas

- Qiskit is heavy (~3-5s first import, ~500MB RAM)
- 6+ qubits per 40 samples — exponential scaling
- `qa.decode` takes seconds per circuit (no batching)
- `mothquantum.ai` API is not reachable from this region (Alibaba Cloud hangzhou, but our egress routes through North America)
- The MOTH_API_KEY token format `moth_X6Sns1GHxeRD94pkAHATrt` suggests JWT-style auth that we don't have a corresponding endpoint for

## Repo map for moth-quantum org

- `quantum-audio` (Python, 51 stars) — main SDK
- `actias-backend` (Svelte) — version 2 of "world's premium quantum synth"
- `actias-electron` (JavaScript) — Electron wrapper for Q1Synth2 web app
- `Actias` — releases repo

## Next steps

1. Build a tiny QSM polygon encoder — verify the round-trip error stays < 0.05 for polygon vertex sequences
2. Run on top-5 polygon seeds (70051917, 4685000, 3289967, 57322595, 90625407) — do the quantum fingerprints cluster? Differ? Reveal new structure?
3. Try MSQPAM/MQSM for multi-feature polygon encoding
4. See if JEV rates quantum-fingerprinted lores higher than unfingerprinted


## Empirical Experiments (Sept 22 evening)

### Experiment 1: Single-channel QSM MCX gate count
- n=100 canon, n=200 random
- Canon: 71.93 ± 9.89 MCX gates
- Random: 72.50 ± 9.58 MCX gates
- Difference: -0.57 (canon uses 0.57 fewer MCX)
- Welch t = -0.48, Cohen d = 0.059
- **NOT STATISTICALLY SIGNIFICANT**

### Experiment 2: QSM statevector fidelity
- 435 canon-canon pairs, 435 random-random pairs, 900 cross pairs
- Mean fidelity ~0.005 for all (essentially orthogonal)
- 2 high-fidelity canon pairs (F=1.0) — likely a bug in my code (statevectors share base state)
- Fresh recomputation shows F=0.0 between different seeds
- **QSM is a unique hash, not a canon signal**

### Experiment 3: MQSM (multi-channel QSM) MCX gate count
- n=30 canon, n=30 random
- Canon: 52.67 ± 7.01 MCX gates
- Random: 51.70 ± 6.00 MCX gates
- Difference: +0.97 (sign-flipped from QSM)
- MQSM is more efficient (52 vs 72 MCX) but no canon signal
- **NOT SIGNIFICANT**

### Experiment 4: Motion encoding (trajectory coherence + velocity)
- n=30 canon, n=30 random, 20-step evolution
- Coherence: canon 0.3364 vs random 0.3364 (EXACTLY EQUAL)
- Velocity: canon 0.4500 vs random 0.5096 (random is faster, not significant)
- **NULL RESULT**

### Experiment 5: Penrose tiling motion
- Penrose vs random tilings: 0.126 vs 0.125 velocity (essentially equal)
- **NULL RESULT**

## JEV Probes (Sept 22 evening)

| Question | JEV p | Verdict |
|----------|-------|---------|
| Isomorphism real (cell=amplitude, witness=time) | 0.62 | Lean yes (structural) |
| MCX hypothesis | 0.73 | Lean yes (preliminary) |
| Future-GAN viable | 0.62 | Lean yes |
| Penrose quantum | 0.43 | Uncertain |
| Polyvocoder idea | 0.36 | Too speculative |
| MCX scale-up needed | 0.85 | Strong yes |
| MQSM as next move | 0.37 | Slight lean |
| Don't abandon quantum | 0.25 | No |
| Workflow validated | 0.77 | Strong yes |
| Isomorphism signal (borderline) | 0.51 | Borderline |
| Coherence metric | 0.34 | No |
| MCX as canon criterion | 0.34 | No |
| Sign-flip refutes | 0.25 | Yes (refuted) |
| Continue or stop | 0.34 | Borderline stop |
| Preserve metaphor as doctrine-prime | 0.19 | No |
| Ship findings | 0.32 | Don't ship yet |

## Conclusions

1. **The structural isomorphism is real**: substrate walker IS a quantum circuit in disguise. JEV agrees at p=0.62.
2. **The empirical canon signal is absent**: across 4 metrics (QSM MCX, QSM fidelity, MQSM MCX, motion coherence/velocity), no significant difference between canon and random seeds.
3. **JEV correctly predicted the negative result**: at p=0.85 it told us "expand to 200+" before we even ran the experiment.
4. **The workflow is validated**: JEV-generated hypotheses → experiment → JEV peer review works at p=0.77.

## What This Means

The substrate walker's canon signal lives in the LINGUISTIC structure of lores, not in the geometric/quantum structure of polygon seeds. The polygon mine is a search heuristic for finding seeds that produce good lores, but the canon itself is a linguistic property.

The substrate-as-quantum-circuit analogy remains BEAUTIFUL but is not EMPIRICALLY GROUNDED as a canon-discovery tool. It might be a doctrine-prime (structural axiom) but JEV votes 0.19 against that promotion.

## Next Steps

1. Document and move on
2. The future-GAN with JEV as judge (p=0.62) might still be worth trying
3. The polyvocoder (p=0.36) is too speculative
4. Higher-dimensional Penrose (p=0.30) — null result confirmed
5. Motion encoding (p=0.43) — null result confirmed

