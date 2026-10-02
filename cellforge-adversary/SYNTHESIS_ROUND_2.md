# Adversary Round 2 — Synthesis & Design Amendments

**Date**: Sept 23, 2026
**Method**: Multi-LLM Adversary across 6 voices (DeepSeek-flash, DeepInfra Hermes-3-405B, Seed-2.0-mini, Qwen3.8-Max [timeout], Llama-4-Maverick, DeepInfra DeepSeek-V4-Flash). 12 findings, 11 promoted by JEV-style Jaccard gate.

**Result**: 7 distinct design gaps identified. Each becomes a doctrinal hole turned into a feature.

---

## The 7 Promoted Themes

### Theme 1 — Temporal Superposition (recurs in 3 voices)

**Voice synthesis** (DeepInfra-DeepSeek #1, Seed #1, Hermes #2):
- The dispatcher's `mode` is a single field. Cannot represent multiple time dimensions simultaneously.
- Concrete failure: user wants to backtest tick 342, PAUSE there, PREDICT from there, while the original backtest continues. Single mode field deadlocks.
- At scale (1000+ cells, 3 zones), dispatcher becomes a global mutex on time.

**Generator's response**: `mode` becomes a **STACK** (or per-timeline), not a single field. Each active timeline has its own mode. Dispatcher manages a `dict[timeline_id, mode]`.

**New cell kind**: `TIMELINE_MODE_CELL { timeline_id, mode, parent_timeline }` — one per active timeline. Dispatcher maintains a `timeline_registry`.

---

### Theme 2 — Tick Debt / Time Bankruptcy (DeepInfra-DeepSeek #2 — UNIQUE and DEEP)

**Voice synthesis**:
- Ticks are treated as fungible. No concept of production rate vs consumption rate.
- Concrete failure: backtest 1M ticks × 20 scenarios × 100Hz = 200M ticks owed. Real-time system falls 2M seconds behind.
- No concept of *tick bankruptcy*, *tick priority*, *tick GC*.

**Generator's response**: introduce **TICK_BUDGET** cell. Each timeline has a `tick_budget_per_second`. Dispatcher enforces budget; if exceeded, runs at `priority` order (live > backtest > prediction).

**New cell kind**: `TICK_BUDGET_CELL { timeline_id, ticks_per_second, ticks_debt, priority }`. Dispatcher checks before scheduling.

---

### Theme 3 — Forked Ledger Collision (DeepInfra-DeepSeek #3 — STRONGEST FINDING)

**Voice synthesis**:
- Two forks (e.g., "raise rate" / "lower rate") both achieve 95% JEV agreement at the same tick range.
- Both claim promotion. No merge operator. No version vector.
- "Append-only" guarantee violated by the very promotion mechanism.

**Generator's response**: 
1. **Version vectors** on EXPERIMENT_LEDGER: `(fork_id, parent_tick, sibling_forks)`. 
2. **Merge operator**: `merge_promotions(canon_tick, [fork_a, fork_b]) → { winner, splice_points, rejected }`.
3. **Per-tick splice**: if fork A wins at tick 1050, fork B at 1060, you can splice. Witness chain records the splice.
4. **Conflict resolution**: first-write wins for canon; later forks must explicitly merge.

---

### Theme 4 — Forked Ledger GC (Llama-4 #1)

**Voice synthesis**: 10K backtests = 10K forked ledgers. Storage blowup.

**Generator's response**: 
- EXPERIMENT_LEDGER has TTL by default (configurable).
- GC daemon runs in dispatcher when in IDLE mode: deletes forks whose `parent_tick` is older than `keep_history_ticks`.
- Fork promotion → moves to canon, no GC needed.

---

### Theme 5 — Multi-User Concurrency (Hermes #1, Seed #1)

**Voice synthesis**: Multiple users → conflicting dispatcher writes. Need locks.

**Generator's response**:
- Dispatcher writes are CRDT-style: each write is `(user_id, timestamp, mode)`. Last-write-wins by timestamp.
- For atomic transitions (PAUSE → REWIND), use **transactional dispatch**: open a transaction, acquire locks on relevant cells, commit or rollback.
- Add `dispatcher.lock_holder` field visible to all users.

---

### Theme 6 — Master Timecode Sync (Seed #2 — DAW-INSPIRED)

**Voice synthesis**: Each zone has independent tick rate. Multi-zone projects drift out of sync. No global BPM.

**Generator's response**:
- New cell kind: `TEMPO_CELL { bpm, beat_count, position }` — global timecode.
- All zones reference tempo_cell at tick boundaries.
- Zone tick rate = `tempo_cell.bpm × beat_multiplier`. Drift corrected via witness checkpoints.

---

### Theme 7 — Live Writes during REWIND (Hermes #3 — TEST CASE)

**Voice synthesis**: REWIND during live writes corrupts witness chain.

**Generator's response**:
- REWIND requires `dispatcher.write_quorum`. All live writers must acknowledge REWIND intent before it proceeds.
- Pending writes either: (a) complete and are witnessed, (b) are rolled back, (c) become part of the rewind replay (rare but valid).
- Add `dispatcher.write_quorum_required: bool` flag.

---

### Bonus — Partial Witness Chain (Seed #3)

**Voice synthesis**: REPLAY_CELL with gaps breaks backtest silently.

**Generator's response**:
- REPLAY_CELL has `integrity_check` witness at write time. Gaps → REPLAY_INTEGRITY_FAIL event.
- Backtest refuses to start with `REPLAY_INTEGRITY_FAIL`. User must repair or splice in interpolated values.

---

### Bonus — Uncertainty Quantification (Llama-4 #2)

**Voice synthesis**: Predictions have no confidence intervals.

**Generator's response**:
- PREDICTION_CELL has `confidence: float [0,1]` derived from multi-worker polyformality (Jaccard across 3+ workers).
- Promotion gate: `confidence > 0.7` to be eligible for promotion; `confidence > 0.9` auto-promote.
- `EXPERIMENT_LEDGER.confidence_distribution` tracks prediction quality over time.

---

## Design Amendments to CELLFORGE_PLAYHEAD.md

After this round, the playhead doc is amended as follows:

### Dispatcher state machine (amended)

```
mode becomes: dict[timeline_id, Mode]
each timeline has its own mode stack
```

### New cell kinds (5 added, total 17)

| Cell kind | Purpose | Origin |
|---|---|---|
| `TIMELINE_MODE_CELL` | per-timeline mode | Theme 1 |
| `TICK_BUDGET_CELL` | tick rate + debt + priority | Theme 2 |
| `FORK_VERSION_VECTOR` | parent/sibling tracking | Theme 3 |
| `TEMPO_CELL` | global BPM/timecode | Theme 6 |
| `WRITE_QUORUM_CELL` | live write acknowledgment | Theme 7 |

### Promoted cell kinds (re-defined)

| Cell kind | New field | Purpose |
|---|---|---|
| `EXPERIMENT_LEDGER` | `version_vector`, `merge_operator`, `ttl` | Theme 3, 4 |
| `REPLAY_CELL` | `integrity_check`, `gap_policy` | Bonus |
| `PREDICTION_CELL` | `confidence`, `worker_agreement` | Bonus |

### New dispatcher behaviors

1. **Transactional dispatch**: `dispatcher.transaction { locks, ops, rollback_plan }`
2. **Tick budget enforcement**: `dispatcher.schedule() respects TICK_BUDGET_CELL`
3. **Live-write quorum**: REWIND/PREDICTING acquire WRITE_QUORUM_CELL before proceeding
4. **Fork GC daemon**: runs in IDLE mode, deletes expired EXPERIMENT_LEDGERs

### Test additions (8 new, total 30)

1. **Temporal superposition**: 2 timelines, different modes, both active
2. **Tick debt**: backtest 1M ticks, verify dispatcher handles 100K tick deficit
3. **Fork collision**: 2 forks same tick range, verify merge or first-write-wins
4. **Fork GC**: 10K expired forks, verify IDLE-mode cleanup
5. **Multi-user**: 3 users write mode concurrently, verify CRDT semantics
6. **Tempo drift**: 3 zones at different rates, verify witness checkpoints correct
7. **Live-write quorum**: REWIND during live writes, verify graceful shutdown
8. **REPLAY_INTEGRITY_FAIL**: REPLAY_CELL with gaps, verify backtest refuses

---

## Updated L1 Build Scope

Was: ~22 tests
Now: ~30 tests

Same single-session build, just more thorough.

---

## Next Round (Round 3) Topics

If Casey wants another iteration:
- **Voice-only mode**: when projection UI is voice-driven (audio DAW), how does dispatcher behave?
- **Cellforge vs JEPA**: which is the prediction engine? Can JEPA be a racehorse that swaps out?
- **Multi-machine cellforge**: dispatchers across network — who's master?
- **Cost model**: TICK_BUDGET could include $/tick. What happens at budget exhaustion?
- **Adversarial training**: cellforge used to train an ADVERSARY model — self-referential?

---

## Files

- `/workspace/research/cellforge-adversary/runner.py` — multi-LLM Adversary runner (9 voices, parallel)
- `/workspace/research/cellforge-adversary/round_1.md` — Round 1 (DeepSeek only, mostly failed)
- `/workspace/research/cellforge-adversary/round_2.md` — Round 2 (4 voices responded, 12 findings)
- `/workspace/research/cellforge-adversary/promoted_2.md` — JEV-promoted findings
- `/workspace/research/cellforge-adversary/SYNTHESIS_ROUND_2.md` — this file

**Status**: Round 2 complete. 7 themes promoted, design amendments ready for next build.
