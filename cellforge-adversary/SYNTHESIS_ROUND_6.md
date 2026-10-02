# Adversary Round 6 — Synthesis & v0.2 Build Plan

**Date**: Sept 23, 2026
**Method**: Sequential multi-LLM Adversary on cellforge v0.1.2 (real code)
**Voices OK**: 5/5
**Result**: 15 findings, 5 deep themes → direct v0.2 build plan

---

## v0.2 Build Decision: REWINDING + REPLAY_CELL ONLY

**Per seed_pro (most important voice):**
- v1 needs only 4 modes (IDLE/PLAYING/PAUSED/REWINDING) — not 7
- Ship 1 new cell (REPLAY_CELL) — not 5
- Killer demo: "pause a running training job at tick N, rewind 200 ticks, change one weight, press play, watch it diverge"

**Killer demo**: pause at tick 1472891, rewind 200 ticks, change one weight, press play, watch it diverge.

---

## The 5 Themes

### Theme 22 — Qwen: Recursive Embedding of Predictions into Canon

**Voice**: "If a prediction at t=100 is promoted to canon, then at t=200, JEPA uses that promoted state (which was once speculative) as ground truth. The witness chain no longer records 'what was observed' but 'what we decided to believe.'"

**Generator's response**: WITNESS_CELL vs PREDICTION_CELL must be **fundamentally different** in storage. Predictions live in a separate namespace. v0.2 PREDICTING mode writes to a different namespace by default. Promotion requires explicit ack.

(For v0.2 just enforce separate storage; v0.3+ adds the merge operator.)

### Theme 23 — Qwen: Tick Windows for Learning

**Voice**: "Learning requires temporal context: gradients flow through sequences, not instants. The state machine has no notion of temporal extent."

**Generator's response**: Add `dispatcher.tick_window` config. PLAYING mode advances by window size. Default 1 (current behavior), set to 32 for transformer training. Witness events still happen per-tick, but learning sees windowed context.

### Theme 24 — Gemma: REWINDING is Read-Only

**Voice**: "A student tries to 'fix' a mistake in a previous training run by scrubbing back to tick N. They find they cannot edit the cell because they are in REWINDING mode. To fix it, they must understand forks, EXPERIMENT_LEDGER, etc."

**Generator's response**: REWINDING is read-only. To "fix" the past, user must:
1. PAUSE (or stay REWINDING)
2. Create a fork at that tick
3. Edit the fork's state
4. RESUME (replay with the fork)

This is the correct mental model. The UI should make it explicit.

### Theme 25 — Gemma: JEPA→JEV "Black Box" Promotions

**Voice**: "The system has effectively gaslit the user by merging the 'What If' with the 'What Was'."

**Generator's response**: For v0.2, NO automatic promotion. JEPA predictions are explicitly PREDICTION_CELLs. User manually promotes via CLI `cellforge promote <prediction_id>`. JEV gate logs the promotion as a witness event.

(For v0.3+ add auto-promotion with explicit thresholds.)

### Theme 26 — Mistral: Combine PREDICTING+BACKTESTING into EXPERIMENTAL

**Voice**: "Combine PREDICTING and BACKTESTING into a single EXPERIMENTAL mode."

**Generator's response**: Defer to v0.3. For v0.2, ship REWINDING only. PREDICTING/BACKTESTING come in v0.3 with the EXPERIMENTAL consolidation.

---

## v0.2 Build Scope

### 1 new mode
- **REWINDING** — read-only backward traversal of witness chain

### 1 new cell kind
- **REPLAY_CELL** — holds historical witness chain to replay

### 5 new tests
1. `rewind_to_tick(N)` moves rewind pointer to tick N
2. cells are read-only in REWINDING mode (no writes)
3. REPLAY_CELL holds witness chain snapshot
4. resume from REWINDING continues from rewind point
5. end-to-end: pause → rewind → change weight → resume → divergence detected

### CLI additions
- `cellforge rewind <tick>` — enter REWINDING at tick N
- `cellforge cell-set <cell_id> <value>` — set cell value (only when PAUSED or with force)
- `cellforge witness-tail [N]` — show last N witness events

### Killer demo (the v0.2 thing)
- Train mock linear regression for 50 ticks
- PAUSE at tick 30
- REWIND to tick 25
- Modify the weight cell (with force=True)
- RESUME → training continues with modified weight
- Witness log shows the divergence

---

## What v0.2 DOES NOT include

- PREDICTING, COMPARING, BACKTESTING (v0.3)
- PREDICTION_CELL, TIMELINE_CELL, EXPERIMENT_LEDGER (v0.3+)
- Master/child dispatcher hierarchy (v0.4+)
- JEPA integration (v0.5+)
- Cross-fleet canon contracts (v0.6+)

---

## Build Steps (Right Now)

1. Add `REWINDING` to `Mode` enum
2. Add rewind pointer + read-only flag to Dispatcher
3. Add REPLAY_CELL dataclass
4. Add cell-set CLI command
5. Add 5 tests
6. Run all tests (25 total: 20 existing + 5 new)
7. Update README + version
8. Push v0.2.0 to GitHub
