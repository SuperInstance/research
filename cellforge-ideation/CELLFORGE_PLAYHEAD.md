# Cellforge Playhead — The Dispatcher as Time Machine

**Date**: Sept 23, 2026
**Context**: Casey saw that the DISPATCH_CELL is *also* the play button, the freeze control, the rewind mechanism, and the projection-into-future machinery. This doc captures that.

## TL;DR

The dispatcher cell's `mode` IS the play state. The whole chronoscopic UX (rewind, freeze, predict, compare, backtest) is just reads and writes to that one cell kind. The system animates itself.

## The dispatcher state machine

```
                 ┌──────────────────────────────────────────┐
                 │                                          │
                 ▼                                          │
   ┌─────────┐  tick()   ┌──────────┐  freeze()  ┌─────────┐
   │  IDLE   │ ────────► │ PLAYING  │ ──────────► │ PAUSED  │
   └─────────┘           └──────────┘             └─────────┘
        ▲                      │                       │
        │                      │ resume()              │ resume()
        │                      ▼                       │
        │               ┌──────────┐                   │
        │               │  TICK    │                   │
        │               └──────────┘                   │
        │                                              │
        │   rewind(N)                                  │
        │   ◄─────────────────────────────             │
        │                                              │
        │   predict(start_tick, scenarios)             │
        │   ─────────────────────────────► ┌──────────┐│
        │                                  │PREDICTING││
        │                                  └──────────┘│
        │                                         │    │
        │                                  commit() │    │
        │                                  ◄────────┘    │
        │                                               │
        │   compare(canon_tick, predicted_tick)         │
        │   ─────────────────────────────────► ┌────────┴──┐
        │                                      │ COMPARING │
        │                                      └───────────┘
        │
        │   backtest(historical_witness_chain)
        │   ───────────────────────────────► ┌────────────┐
        │                                    │BACKTESTING │
        │                                    └────────────┘
        │                                          │
        └──────────────────────────────────────────┘
                         done
```

## The 7 modes (extended)

| Mode | Tick flow | Witness writes | UI state | Use case |
|---|---|---|---|---|
| **IDLE** | none | none | static | system loaded, nothing running |
| **PLAYING** | full zone rates (A=100Hz, B=1Hz) | yes (canon) | live | normal operation |
| **PAUSED** | halted | none | frozen snapshot | inspect a moment |
| **REWINDING** | backward through witness chain | none (read-only) | playback at speed | find a prior state |
| **PREDICTING** | forward into forked ledger | yes (experimental) | shadow display | "what if I change X?" |
| **COMPARING** | halted | none | dual pane | diff canon vs prediction |
| **BACKTESTING** | forward through historical witness chain | yes (replay) | live | "would my model have predicted this?" |

The dispatcher is also a **forkable cell**: PREDICTING and BACKTESTING modes write to **experimental ledgers** that don't pollute canon. Promotion to canon requires JEV-style witness agreement.

## New cell kinds (extending the 8)

| Cell kind | Retention | Zone | Purpose |
|---|---|---|---|
| `REPLAY_CELL` | full_ledger | A, B | Holds historical witness chain to replay |
| `PREDICTION_CELL` | rolling_window_N_32 | A | JEPA's predicted future states |
| `TIMELINE_CELL` | full_ledger | A, B, C | Holds parallel scenes (DAW takes) |
| `EXPERIMENT_LEDGER` | ttl_bearing | C | Forked predictions, auto-expire or promote |

Now 12 cell kinds. The grid grows by 50% but each kind has a single, clear role.

## Cellular DAW analogies

| DAW concept | Quilt equivalent |
|---|---|
| Track | zone or cell group |
| Playhead | dispatcher tick |
| Transport | dispatcher state machine |
| MIDI insert | INFLUENCE_CELL write |
| Audio insert | MOCK sensor with TTL |
| Arm for recording | cell marked `witness_enabled: true` |
| Mute | dispatcher skips this zone/cell |
| Solo | dispatcher priority override |
| Punch-in at tick N | rewind to N + replay + branch |
| Automation lane | INFLUENCE_CELL stream with TTL range |
| Bounce/export | snapshot a workbook with all witnesses |

A user who's never seen a spreadsheet would reach for Quilt if they've used Ableton or Logic. The metaphors are identical.

## Chronoscopic UX (3 dimensions)

```
   ┌────────────────────────────────────────────────────┐
   │                                                    │
   │   PAST          PRESENT         FUTURE             │
   │   ◄──────────── ●───────────────►                  │
   │   witness chain  live ticks     predicted fork     │
   │                                                    │
   │   rewind(N)     tick()         predict(scenario)   │
   │                                                    │
   │   read-only     full read/write  experimental       │
   │                                                    │
   └────────────────────────────────────────────────────┘
```

User moves the playhead freely. The system shows:
- **Past**: what was witnessed, frozen, replayable
- **Present**: what is ticking now
- **Future**: what could happen (forked ledger, no commitment)

Diff view shows where predictions diverged from canon. **Promotion** moves a prediction from experimental → canon ledger.

## JEPA + JEV racehorses

```
WITNESS_CELL (what was)
       │
       ▼
   JEPA predictor
       │
       ▼
PREDICTION_CELL (what might be)
       │
       ▼
   JEV verifier
       │
       ▼
promotion to WITNESS_CELL (what becomes canon)
```

- **JEPA** is the predictor engine. Reads past cell states, predicts future ones. Output → PREDICTION_CELL.
- **JEV** is the promotion gate. Compares prediction vs eventual witness. High agreement → promote. Low → keep in experimental ledger for further review.

JEPA + JEV are **isolated racehorses**: each can be swapped independently. The grid outlives them.

## OS metaphor (the new computer platform)

| OS layer | Quilt equivalent |
|---|---|
| Kernel | state_grid + 11 opcodes |
| System calls | BIND / LINK / EFFECT / VIEW / TICK / FORGET / PROOF / ROUTE / CRDT / WORLD / TIME |
| Processes | DISPATCH_CELLs (one per zone) |
| Files | cells (any of the 12 kinds) |
| Threads | zones (A/B/C) |
| Schedulers | dispatcher state machine |
| Memory | cell ledger (append-only) |
| Filesystem | workbook |
| Programs | workbooks (collections of cells + flows) |
| **Time** | **playhead (REPLAY_CELL + PREDICTION_CELL + dispatcher mode)** |
| **Predictive execution** | **forked ledgers (PREDICTING mode)** |
| **Backtesting** | **REPLAY_CELL-driven BACKTESTING mode** |

The last three rows are what's new. Existing OSes don't have a forkable time dimension. This one does.

## Adversary pokes (full list, 10)

1. Multiple dispatchers — master dispatcher owns sub-dispatchers per zone
2. Frozen UI ≠ frozen dispatcher — separate flags
3. Predictions need polyformality — multi-architecture JEPA agreement
4. Mocks need TTL + MOCK tag — INFLUENCE_CELL insufficient alone
5. DAW needs parallel timelines — TIMELINE_CELL
6. Backtesting needs REPLAY_CELL — historical witness held in cell
7. Interdimension = canon vs experimental — promotion gate required
8. JEPA predictions ≠ witnesses — different retention, drop vs no-drop
9. New computer needs OS metaphor — kernel/syscall/process/thread
10. Animation needs frame budget + tick coalescing — UI redraw rate ≠ tick rate

## Naming doctrine check

- `cellforge` — substrate + purpose (zero-shot ✓)
- `quilt-playhead` — quilt family + time control (zero-shot ✓)
- The dispatcher cell kind: `DISPATCH_CELL` (already canonical)
- New modes: `dispatcher.mode` is a value, not a new cell kind

## Implementation: extend cellforge L1

Add to L1 scope:
- Dispatcher state machine: 7 modes
- 4 new cell kinds: REPLAY_CELL, PREDICTION_CELL, TIMELINE_CELL, EXPERIMENT_LEDGER
- 1 new CLI command: `cellforge dispatch <mode> [--at tick] [--scenarios ...] [--compare ...]`
- 5 new tests: rewind, predict, compare, backtest, promote
- JEPA stub: simple linear predictor (replace with real JEPA later)
- JEV stub: cosine similarity gate (already in mavis-fleet-canary)

L1 size: ~22 tests (was ~15), same single session.

## Files

- `/workspace/research/cellforge-ideation/CELLFORGE_PLAYHEAD.md` — this file
- `/workspace/research/cellforge-ideation/CELLFORGE_ZONES_SPATIAL.md` — original zones doc (will be updated)
- `/workspace/research/cellforge-ideation/GENERATOR_ADVERSARY_ROUND_0.md` — original Round 0

**Status**: Ideation complete. Ready to extend L1 on Casey go-ahead.

---

## v0.4.1 update — Causal-consistency verdict on rewind

**Date**: Sept 23, 2026 (R10 outcome)

Multi-LLM Adversary Round 10 surfaced Theme T5: rewind is a trust claim, not a state operation. The system now returns a verdict dict on `rewind_to()`:

```python
verdict = d.rewind_to(target_tick=50)
# Returns: {
#   'ok': bool,
#   'violations': [(tick_t-1, tick_t), ...],
#   'checks': int,
#   'target_tick': int,
#   'recommended_action': 'proceed' | 'warn' | 'block',
#   'reason': str
# }
```

`Dispatcher.bind_workbook(wb)` wires the workbook in both directions so the verdict can compare consecutive witness tick states via `Workbook.causally_consistent()` (True iff a tick t+1 event references a tick t event in its parent_hashes).

**5 new tests** added (42 total now, was 37):
- rewind_returns_verdict_dict
- rewind_without_bound_workbook_assumes_causal
- rewind_with_witness_chain_detects_non_causal
- rewind_with_properly_chained_witness_is_causal
- bind_workbook_symmetric

**Why this matters**: Without the verdict, users rewind → mutate → resume → divergence is silent. Now divergence triggers a WARN/BLOCK visibility, surfacing the issue honestly rather than letting "future doesn't match past" be a user-surfaced mystery.

**Cross-project insight**: A receipted refusal (warn/block before resume) > silent failure. This is the same principle as moth-ledger's Pacioli canary (refusal bookkeeping preserves honesty as a first-class cell). Both systems make **honesty the default state**.
