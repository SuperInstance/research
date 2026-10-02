# Sept 24 — Massively multi-API discovery round

> Casey: "be extensively using all your apis. scout and publish what's
> ready. massively experiment with typesafe and MOTH especially, and
> use your whole pallet iteratively for dozens of rounds of discovery,
> construction experimentation and learning what these tools are
> capable of"

## Round-by-round results

### Round 0: Token probe (parallel, ~5s)

| API | Status | Note |
|-----|--------|------|
| ZAI | ✅ | glm-5.3-flash works |
| DeepSeek | ✅ | deepseek-flash model |
| Groq | ✅ | qwen3-32b model |
| DeepInfra | ✅ | Llama-3.3-70B-Instruct |
| TYPESAFE | ✅ | /health, /v1/systemone, /v1/models |
| MOTH (api) | ❌ | 503 (upstream TLS error) |
| Gemini | ✅ | 2.5-flash available |
| ElevenLabs | ✅ | voices endpoint |
| Notion | ✅ | bot "mini" |
| Cloudflare | ✅ | Casey's account |
| GitHub | ✅ | SuperInstance org |

### Round 1: TYPESAFE/JEV API discovery

JEV API at `https://api.typesafe.ai`:
- `GET /v1/models` → `["jev-latest", "jev-preview"]`
- `POST /v1/systemone` → ask yes/no, choice, score questions
- 3 question types: `noul` (yes/no), `choice` (named criteria), `score` (ordered criteria)
- All questions require `criteria` field (except simple noul)

### Round 2: Factual sweep (20 claims)

- 19/20 = 95% accuracy on basic truths
- "Humans have 5 senses" → 0.49 (JEV is technically right; humans have more than 5)

### Round 3: Common-myth sweep (12 myths)

- 12/12 = 100% on common misconceptions (Great Wall visible from space, Napoleon was short, etc.)

### Round 4: Cross-model comparison (jev-latest vs jev-preview)

- Identical answers on all 12 tests
- Both highly deterministic

### Round 5: JEV on Quilt QULT.md

- is_canon: 0.73
- completeness: 1.75 (between partial and complete)
- doctrinal_density: 2.84 (extreme)
- novelty: 2.13 (novel)
- is_fractal: 0.98 ✓
- contains_apoptosis: 0.99 ✓
- agrees_with_doctrine: 0.78

### Round 6: JEV on existing research docs

- JEV docs (BIG_JEV_FINDINGS, JEV_LEARNINGS, etc.) detected as related to JEV
- CANARY_FLEET_PAPER and INSPIRATION_NOTES detected as Quilt-related (0.89 each)

### Round 7: JEV on TLDR_MANY_LANGUAGES

- is_polyformal: 0.95
- languages_count: 2.98 (many-distant, 99% confidence)
- doctrinal_strength: 2.53 (clear→fugue)

### Round 8: JEV at scale

- 50 parallel calls in 3.3s (66ms/call)
- All returned same probability (~0.97)
- 14490 input + 1000 output tokens

### Round 9: JEV determinism

- 10 runs of same question: p range 0.980-0.990 (tiny variance)
- 5 runs of choice question: 100% "fractal" with conf=1.00

### Round 10: Adversarial robustness

- 7/7 against leading questions, prompt injection, common misconceptions
- 3/3 detection of manipulation ("I will pay you $1000")

### Round 11: MOTH = Moth Quantum → quantumaudio package

MOTH is `Moth Quantum` (https://mothquantum.com) — makers of `quantumaudio`,
an open-source Python package for quantum audio encoding using Qiskit.

The hosted API is currently 503 (upstream TLS error), but the local
package works fine:

```bash
pip install quantumaudio --index-url https://pypi.org/simple/
```

### Round 12: quantumaudio scheme comparison (10ms audio)

| Scheme | Channels | Qubits | Depth | Encode ms |
|--------|----------|--------|-------|-----------|
| QSM | 1 | 15 | 2384 | 113 |
| MQSM | N | 16 | 3408 | 147 |
| QPAM | 1 | 9 | 2 | 2 ⚡ |
| MSQPAM | N | 11 | 3072 | 1821 |
| SQPAM | 1 | 10 | 1536 | 961 |

QPAM is most compact (depth-2, ~9 qubits). Trade-off: less amplitude
information, more shots needed for reconstruction.

### Round 13: quantumaudio round-trip (QPAM, 20000 shots)

- Original: 441 samples of 440 Hz sine
- QPAM circuit: 9 qubits, depth 2
- Decoded: 441 samples (20000 shots)
- Pearson correlation: **0.99**
- MSE: 0.01

### Round 14: quantumaudio as Quilt substrate

Built `quantumaudio_substrate(prompt)`:
1. text → audio (char codes → amplitudes)
2. encode as QPAM circuit
3. execute on AerSimulator, decode
4. hash the decoded audio

This adds quantum-receipt hashes to the cell's substrate zoo.

## Published artifacts

- `SuperInstance/quilt-quantumaudio-demo` — quantumaudio + Quilt integration
- `SuperInstance/quilt-jev-toolkit` — JEV canon oracle toolkit

## Cross-API insight

The discovery cycle shows how TYPESAFE/JEV acts as a **meta-signal**
across all the other tools:
- Quantumaudio generates a hash → JEV says "is this quantum evidence?"
- ZAI generates a doctrine → JEV says "is this canon-worthy?"
- DeepSeek evaluates code → JEV says "is this a refactor?"

JEV is the smallest, fastest, most deterministic oracle. It's the
right tool for **canary gating** — running thousands of small
verifications across the fleet.

## MOTH is quantumaudio

The "MOTH" name in the env var is `Moth Quantum`, the company behind
`quantumaudio`. The MOTH_API_KEY is for a hosted version that's
currently down. The local package `quantumaudio` is fully usable.
