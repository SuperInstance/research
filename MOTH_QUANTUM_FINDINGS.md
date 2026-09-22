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

