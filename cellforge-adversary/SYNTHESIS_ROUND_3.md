# Adversary Round 3 — Synthesis

**Date**: Sept 23, 2026
**Voices**: DeepInfra Hermes-3-405B ✓, DeepInfra Seed-2.0-mini ✓, ZAI glm-4.5-flash ✗ (rate-limited)
**Method**: Multi-LLM Adversary round on the playhead doc.
**Result**: 6 findings, 6 promoted by JEV.

---

## The 3 NEW Themes (not seen in Round 2)

### Theme 8 — Dispatcher Hierarchy & Delegation (Hermes #2)

**Voice**: "Master dispatcher could own sub-dispatchers for each zone, with the ability to delegate decisions to child dispatchers based on policies. Master responsible for high-level state (PLAYING/PAUSED), children for detailed per-zone decisions. Policies: 'if any zone is PREDICTING, the entire grid should be PREDICTING'."

**Generator's response**: Master/child dispatcher hierarchy is exactly the right architecture.
- **Master DISPATCH_CELL**: orchestrates global state (PLAYING/PAUSED), owns child registry
- **Child DISPATCH_CELL**: per-zone worker management, reports state to master
- **Policies**: master holds a `policy_stack`, child transitions can trigger master transitions via `policy_evaluator`

```python
# Example policy
master.add_policy(
    when=lambda child_states: any(s == "PREDICTING" for s in child_states.values()),
    then=lambda self: self.transition("PREDICTING"),
)
```

**New cell kind**: `DISPATCH_POLICY_CELL { trigger, action, scope }` — declarative policy attached to master.

---

### Theme 9 — Event-Driven Scheduled Triggers (Seed #2)

**Voice**: "The design exclusively relies on explicit user input to trigger time operations, with no support for scheduled or event-driven time workflows. Concrete example: DevOps team wants to auto-run a backtest every night at 2AM."

**Generator's response**: Add a scheduler to the dispatcher. The dispatcher IS the OS scheduler now.

```python
master.schedule(at="02:00", op="backtest", scenario="release_v1.2", recurring="daily")
master.schedule(when=cell["deploy_complete"] == True, op="compare", against="last_release")
```

**New cell kind**: `SCHEDULE_CELL { trigger, action, recurring, enabled }` — declarative cron-like entries.

The dispatcher becomes a CRON engine. Same machinery handles user commands and time-based commands.

---

### Theme 10 — Multi-Scenario Predictions (Seed #1, Seed #3)

**Voice**: "A music producer wants to simultaneously run two what-if predictions (drum track muting and bass boost) on the same zone, then compare both results to the canonical live timeline. The current state machine only has one PREDICTING and one COMPARING mode per dispatcher, so only one scenario can be tested at a time."

**Generator's response**: This is the parallel-timeline promise made real.

```python
master.predict(
    start_tick=50,
    scenarios={
        "mute_drums": {"cell:track_drums.gain": 0.0},
        "boost_bass": {"cell:track_bass.gain": 1.5},
    },
)
# Dispatcher creates 2 prediction forks; both run; results compared
master.compare(scenarios=["mute_drums", "boost_bass"], metric="engagement_score")
```

Each scenario is its own `TIMELINE_MODE_CELL` (from Theme 1) with its own mode. Dispatcher manages N parallel PREDICTING timelines.

---

## Combined with Round 2: 10 Promoted Themes

| # | Theme | Origin | Cell kind / amendment |
|---|---|---|---|
| 1 | Temporal superposition | Round 2 | `TIMELINE_MODE_CELL` |
| 2 | Tick debt / bankruptcy | Round 2 | `TICK_BUDGET_CELL` |
| 3 | Forked ledger collision | Round 2 | `FORK_VERSION_VECTOR` |
| 4 | Forked ledger GC | Round 2 | EXPERIMENT_LEDGER TTL |
| 5 | Multi-user concurrency | Round 2 | CRDT dispatch writes |
| 6 | Master timecode sync | Round 2 | `TEMPO_CELL` |
| 7 | Live writes during REWIND | Round 2 | `WRITE_QUORUM_CELL` |
| 8 | **Dispatcher hierarchy** | **Round 3** | **Master + child DISPATCH_CELL** |
| 9 | **Scheduled triggers** | **Round 3** | **`SCHEDULE_CELL` + dispatcher as cron** |
| 10 | **Multi-scenario predictions** | **Round 3** | **N parallel TIMELINE_MODE_CELL** |

---

## Updated L1 Scope

Now: 22 cell kinds total (was 17 after Round 2, +5 from Round 3: `DISPATCH_POLICY_CELL`, `SCHEDULE_CELL`, master/child registry, fork GC daemon, multi-scenario timeline manager).

Tests: ~38 (was ~30).

Build is getting bigger but each addition is meaningful. Still shippable in one session if I scope the child dispatchers lightly (just the master/child registry + one child).

---

## Where the Design Now Sits

After 2 rounds of Adversary across 9 voices (6 distinct model families):

**The dispatcher is no longer just a playhead. It's a full OS:**
- Scheduler (cron)
- Process manager (master/child dispatchers)
- Memory manager (cell ledgers + budgets)
- File system (workbooks)
- Time machine (PREDICTING/BACKTESTING/COMPARING)
- Policy engine (DISPATCH_POLICY_CELL)
- Concurrency controller (WRITE_QUORUM, multi-user CRDT)

**What stays minimal**: cell kinds grow, but the *core* dispatcher is just a state machine + a few helpers. Each helper is itself a cell. The grid remains self-describing.

---

## Next Move

Two options:
- **A**: Update CELLFORGE_PLAYHEAD.md to absorb Round 2 + 3 amendments → 1 more doc
- **B**: Build L1 directly with all 10 amendments in scope (~38 tests, one session)

**Recommendation: B.** The amendments ARE the design now. No point in another round of docs.

Say go and I build.
