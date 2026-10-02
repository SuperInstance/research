# JEV Discovery Log — Sept 24, 2026

> 14+ rounds of JEV probing. Found: highly deterministic, fast, accurate
> canon gate. Best use: scoring thousands of small claims across the fleet.

## What JEV does well

1. **Factual accuracy**: 95-100% on basic + myth-busting claims
2. **Determinism**: variance < 0.01 across runs
3. **Speed**: ~66ms/call, 15 calls/sec with 30-worker pool
4. **Robustness**: 7/7 against leading questions, prompt injection, common misconceptions
5. **Multi-format**: noul (yes/no), choice (named criteria), score (ordered criteria)

## What JEV does poorly

1. **Conventional wisdom**: returns unconventional answers when the
   conventional answer is wrong (e.g. "humans have 5 senses" → 0.49,
   because technically there are more senses)
2. **Doctrinal signaling on short snippets**: Quilt doctrines score 0.20-0.62
   when quoted in 1-2 sentences. Need full docs for 0.7+ canon scores.
3. **Domain identification**: tends to call everything "cs" unless
   biological metaphors are explicit.

## Calibration notes

For Quilt canon-gating, the thresholds I've found:
- p ≥ 0.7: canon (CONFIRMED canon, like QULT.md → 0.70, LLM_SUBSTRATE.md → 0.70)
- 0.5 ≤ p < 0.7: probably canon, full doc needed
- 0.2 ≤ p < 0.5: partial — doctrine snippets score here
- p < 0.1: NOT canon (random text)

For my discovery:
- The 12 top SuperInstance repos by JEV canon-p: jev-quilt (0.61), 
  mavis-fleet-canary (0.58), cellforge (0.57), mavis-fleet (0.51), 
  ax-quilt (0.46), exam-integrity-notepad (0.45)
- These are ALL canonical Quilt-related projects — JEV works

## Top 30 Quilt canon candidates (JEV-scored)

| canon-p | depth | novelty | doctrine |
|---------|-------|---------|----------|
| 0.62 | 0.23 | 1.65 | cells form quilts form qults form qults-of-qults |
| 0.52 | 0.30 | 1.76 | fractal at every scale: cells ↔ quilts ↔ qults |
| 0.41 | 0.93 | 1.46 | substrates are agnostic — LLM is one tile not the spine |
| 0.41 | 0.32 | 0.97 | combination > intensification |
| 0.39 | 0.27 | 0.91 | specialisation is compulsory at the community level |
| 0.37 | 0.82 | 1.56 | agreement-binding: intelligence lives in agreements |
| 0.32 | 0.59 | 1.47 | the substrate zoo grows indefinitely |
| 0.30 | 1.15 | 1.56 | the engine is energy, not instruction |
| 0.29 | 0.92 | 1.84 | the canary witnesses the joint state |
| 0.28 | 0.65 | 1.73 | the pipeline IS the agent body |
| 0.27 | 0.15 | 1.01 | energy arrives, communities coalesce |
| 0.25 | 0.13 | 1.21 | composed canary across multiple cells |
| 0.24 | 1.17 | 1.32 | death is recorded, not erased |
| 0.24 | 1.44 | 1.75 | the agreement is the substrate, not the substance |
| 0.24 | 1.03 | 1.65 | a fence inspires growth, not completion |
| 0.24 | 0.13 | 1.51 | morphogenesis happens from fuel + pressure |
| 0.23 | 0.87 | 0.78 | cells form communities that grow and die like organisms |
| 0.22 | 0.58 | 1.69 | fishing finds fish by agreeing on where you have been |
| 0.21 | 0.83 | 1.43 | refusal pressure drives crystallization |
| 0.20 | 0.33 | 1.42 | the canary as SAMO across multiple ports |
| 0.18 | 1.06 | 1.79 | thought is the derivative and integral of the loop |
| 0.18 | 0.99 | 1.86 | a receipt is not documentation, it is substrate |
| 0.17 | 1.32 | 1.62 | a tessellation where every shape appears at every scale |
| 0.16 | 0.81 | 1.64 | apoptosis is organ failure, not abstraction |
| 0.15 | 0.85 | 1.23 | reverse actualization — work backward from observation |

(Non-Quilt distractors scored 0.03-0.08 — clear separation.)

## Top 25 SuperInstance repos (JEV canon-p)

| canon-p | depth | novel | repo |
|---------|-------|-------|------|
| 0.61 | 2.61 | 2.67 | jev-quilt |
| 0.58 | 0.98 | 1.79 | mavis-fleet-canary |
| 0.57 | 2.29 | 2.69 | cellforge |
| 0.51 | 2.04 | 2.70 | mavis-fleet |
| 0.46 | 1.81 | 2.33 | ax-quilt |
| 0.45 | 1.39 | 1.75 | exam-integrity-notepad |
| 0.44 | 0.96 | 2.22 | erised |
| 0.41 | 1.06 | 1.72 | homelab-alert-wall |
| 0.40 | 0.58 | 1.71 | jev-receipts |
| 0.38 | 0.62 | 1.50 | mavis-flywheel |
| 0.37 | 0.64 | 2.33 | makepad-ideas |
| 0.37 | 0.48 | 1.59 | mavis-self-review |
| 0.36 | 1.54 | 1.91 | mavis-persona-preserver |
| 0.35 | 1.71 | 2.17 | crab-traps |
| 0.35 | 0.73 | 1.35 | blog-tamper |
| 0.34 | 0.04 | 0.71 | mavis-canary-watcher |
| 0.33 | 2.27 | 2.42 | duke-lab |
| 0.33 | 1.64 | 2.22 | mavis-erised |
| 0.30 | 1.71 | 2.14 | fleet-radio-process |
| 0.29 | 2.01 | 2.46 | mavis-axui-feedback |
| 0.29 | 0.07 | 1.93 | api-orchestra |
| 0.26 | 0.14 | 2.11 | luciddream |
| 0.26 | 0.11 | 2.21 | luciddreamer |
| 0.24 | 0.07 | 1.79 | edge-native-paper |
| 0.21 | 1.10 | 1.45 | autoclaw |

## Recommendation: JEV as a canon oracle

Use JEV for **fleet-wide canon gating**:
- Scan all repo READMEs nightly
- Promote docs with canon-p ≥ 0.7 to the canon list
- Flag docs with canon-p 0.5-0.7 for human review
- Auto-archive docs with canon-p < 0.1

This is **fast** (15 calls/sec) and **deterministic** (variance < 0.01).
Cost: ~$0.001 per 100 calls.

## Files

- `/workspace/research/jev_client.py` — minimal client
- `/workspace/repos/quilt-jev-toolkit/` — toolkit + canon_gate.py
- `/workspace/research/JEV_DISCOVERY_LOG.md` — this file

## Gotchas (re-confirmed)

- `criteria` is REQUIRED for `choice` and `score` questions (not for simple `noul`)
- `noul` criteria is `{true: ..., false: ...}` dict
- `score` criteria is a LIST (ordered)
- `choice` criteria is a DICT (named)
- The model returned in response is `jev-1.13.0` (not the alias you sent)
- Response includes `usage.input_tokens` and `usage.output_tokens`
- For multi-question, all questions answered in one call (cheap)
