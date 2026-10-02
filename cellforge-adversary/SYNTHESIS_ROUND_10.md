# Synthesis R10 — cellforge v0.4.0 (EXPERIMENTAL mode)

8 voices ran sequentially with FIXED User-Agent + arg-order.

## Critical findings (≥4 voices)

### T1: Tick abstraction is a lie
groq_qwen, qwen_thinking, hermes (T1), deepseek_pro
Logical tick ≠ execution tick. In REWINDING/PREDICTING, "tick" means snapshot stepping, not model inversion.
**Action**: v0.4.1 distinguish logical_tick (zone-rate) from execution_tick (real-time).

### T2: 7 modes over-engineered
groq_qwen, seed_pro, mistral, gemma, deepseek_pro
3 orthogonal flags: (is_playing, is_experimental, playhead_position).
**Action**: v0.4.1+ refactor; defer to v0.5 since breaking change.

### T3: TTL on EXPERIMENT_LEDGER is mistake
groq_qwen, seed_pro
Auto-expire silently destroys user's overnight predictions.
**Action**: Manual delete only for v0.4.0; add TTL in v0.5 with opt-in.

### T4: Chronoscopic UX is cockpit-grade
gemma, mistral
3-level UI: Beginner (Play/Pause/Rewind only), Power (3D timeline), God (full inspection).
**Action**: Layered UI for v0.4.1.

## Important (3 voices)

### T5: Causality not enforced by witness chain
qwen_thinking, gemma, deepseek_pro
Rewind may not reproduce witnessed state if writes aren't deterministic functions of neighbors.
**Action**: `rewind_to(tick)` returns causal-consistency verdict (v0.4.1).

### T6: Variable zone tick rates add complexity
groq_qwen, seed_pro, mistral
Hardcode 10Hz uniform for v0.4.0.
**Action**: Drop variable rates; uniform for v0.4.

### T7: Git vocabulary for docs
hermes, deepseek_pro
Use fork/commit/branch/merge/checkout for dispatcher concepts.
**Action**: v0.5 docs.

### T8: JEPA+JEV = prediction marketplace
deepseek_pro, hermes, qwen_thinking
Already supported via `compare_scenarios()`.

### T9: Promotion = truth-claim problem
gemma, qwen_thinking, deepseek_pro
Pedagogical rejection messages needed.
**Action**: v0.4.1.

### T10: Redundant cell kinds
mistral, hermes
TIMELINE_CELL + EXPERIMENT_LEDGER overlap.
**Action**: Don't add new cell kinds in v0.4.0 (already in seed_pro R4 doctrine).

## JEV verdict (v0.4.0)

- canon_score: 0.86/3 (Brilliant paradigm 0.63 probability)
- novelty: 0.76/3 (Notable shift 0.59 probability)
- is_inversion: 0.69
- Confidence: ~0.58

JEV showing canon-score rising 0.55 → 0.61 → 0.78 → 0.86 across versions.
v0.4.0 is canon-worthy. is_inversion holding at ~0.7 suggests "real but proportional inversion" — not "complete".

## Decisions to ship v0.4.1

[T1] logical_tick vs execution_tick
[T5] causal-consistency verdict on rewind
[T9] pedagogical rejection messages

## Decisions to defer

[T2] modes→flags — breaking change, do in v0.5
[T3] TTL — after observation
[T4] UI hierarchy — after UX testing
[T7] git vocab — docs, v0.5
[T10] cell kind reduction — after more usage
[T11] SnapshotStore — v0.5
[T12] UX simplification — after user testing
[T13] "performative intelligence" framing — docs, v0.5
[T14] Cut experimental UI — only if metrics warrant
