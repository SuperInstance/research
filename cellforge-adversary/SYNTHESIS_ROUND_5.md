# Adversary Round 5 — Synthesis

**Date**: Sept 23, 2026
**Voices OK**: 3/5 (deepseek_pro empty, gemma error)
**Subject**: Adversary on actual cellforge code (not just design)

---

## Round 5 Themes (Implementation-Focused)

### Theme 18 — Write Lock When PLAYING (Seed-Pro — CRITICAL SAFETY)

**Voice**: "When dispatcher is in PLAYING mode, no external actor may write to canon cells. No users, no admin, no API, no debug tools. All external modification only works when PAUSED, or automatically routes to EXPERIMENT_LEDGER. This is not a feature, this is a safety interlock."

**Status**: NEW finding. Direct implementation gap.

**Fix**: Add `dispatcher.allow_writes(mode)` — returns False when mode == PLAYING. Workbook.add_cell() raises in PLAYING mode unless user explicitly marks `force=True`.

**v0.1.1 patch**:
```python
def add_cell(self, cell, force=False):
    if self.dispatcher.mode == Mode.PLAYING and not force:
        raise PermissionError("Cannot modify canon while PLAYING. Pause first or use force=True.")
```

---

### Theme 19 — Frozen Snapshot Is Illusory (Qwen-Max-Thinking)

**Voice**: "PAUSED halts the dispatcher's tick emission, but cells may still be mid-computation or holding stale intermediate values. The resulting 'snapshot' is a temporal slice across a smear of physical time, not a consistent cut."

**Status**: Deeper issue. Even after pause, in-flight worker computations must drain before cells are truly quiesced.

**Fix**: Add `dispatcher.drain()` semantics — pause moves state PAUSE_REQUESTED, workers must complete their in-flight tick + acknowledge, THEN FULLY_PAUSED fires.

**v0.1.1 patch**:
- Workers must call `ack_pause(after_drain=True)` after current tick finishes
- Dispatcher waits for all `ack_pause(after_drain=True)` before FULLY_PAUSED

For v0.1.0 (mock workers), this is automatic since the test harness orchestrates acks. For v0.2+ with real PyTorch workers, this is critical.

---

### Theme 20 — Cross-Fleet Canon Contracts (Z-Interference from R4)

**Status**: Deferred to v0.2+ per R4 SYNTHESIS.

---

### Theme 21 — Time Banking (Qwen-Max-Thinking from R5)

**Voice**: "Witness chain assumes global linear time. With heterogeneous zone rates, there's no universal 'now'." 

**Status**: Already partially addressed (vector clocks in WitnessEvent). Document more clearly in v0.1.1.

---

## v0.1.1 Patches

Three changes:
1. **Write lock** when PLAYING — `Workbook.add_cell(force=False)` raises
2. **Drain semantics** — pause sub-state machine now requires drain ack
3. **Docs** — clarify vector clock usage in README

3 new tests:
- `test_cannot_modify_canon_while_playing` — safety interlock
- `test_force_write_bypasses_lock` — escape hatch for admins
- `test_pause_with_drain_ack` — quiescence semantics

---

## What I'm Building Next (After v0.1.1)

Per Casey's "keep going with your team as far as you can":
- **v0.1.1 patch** (write lock)
- **v0.2.0**: REWINDING mode + REPLAY_CELL (R8 deferred)
- **v0.3.0**: PREDICTING + PREDICTION_CELL + JEPA stub
- **v0.4.0**: COMPARING + BACKTESTING

Or maybe scope up: apply all 10 themes from R2-R4 in v0.2.0 (the EXPANDED version), keep v0.1.1 as just the safety patch.

**Decision**: ship v0.1.1 quick (write lock only), then v0.2.0 expands. Sequential.
