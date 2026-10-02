# Adversary Round 4 — Synthesis & L1 Build Scope

**Date**: Sept 23, 2026
**Method**: SEQUENTIAL multi-LLM Adversary (DeepInfra concurrency-flaky, so went one-at-a-time)
**Voices OK**: 6/7 (deepseek-pro returned None — empty content)
**Result**: 18 promoted findings, 6 deep themes.

---

## The Round 4 Themes

### Theme 11 — Ship Only 3 Modes for v0 (Seed-Pro — MOST IMPORTANT)

**Voice**: "Ship only 3 dispatcher modes, not 7. Delete REWINDING / PREDICTING / COMPARING / BACKTESTING entirely from launch. Only IDLE → PLAYING → PAUSED. This is 100% of the core inversion. The entire trick is that play/pause state is just a cell value that propagates atomically. All the chronoscopic features are 18-month nice-to-haves."

**Voice**: "The killer launch demo is **perfect pause, not prediction**. A 128-GPU distributed training run is live at 100Hz. You write PAUSED to the dispatcher cell. 14ms later every worker, buffer, gradient accumulator, logger has halted on the same tick boundary. No partial states. This does not exist anywhere today. This is what sells cellforge. Nobody will remember the JEPA demo. Everyone will remember the first time they perfectly paused a running training run."

**Generator's response — L1 v0.1.0 SCOPE:**
- **3 modes only**: IDLE, PLAYING, PAUSED
- **1 new cell kind only**: FORK_VERSION_VECTOR (others are v0.2.0)
- **Killer demo**: lock-step pause across 100 simulated workers on the same tick
- **Why this matters**: shipping discipline. The demo tells the whole story.

---

### Theme 12 — Witness Chain Needs Causal Consistency (Qwen-Max-Thinking)

**Voice**: "The design presumes all events can be linearized into one chronological sequence supporting rewind/replay. But in distributed cellular substrate with zones at different rates, there is no physically meaningful global clock. The witness chain implicitly imposes a logical timestamping scheme (Lamport clocks / vector clocks). 'Rewinding to tick N' may conflate causally unrelated states."

**Generator's response**: Use **vector clocks** on each witness event. Each WITNESS_CELL event has `(zone_id, vector_clock, content_hash)`. Rewind to tick N replays events that are causally consistent at that vector clock.

```python
@dataclass
class WitnessEvent:
    tick: int
    zone_id: str          # A, B, C, master, child
    vector_clock: Dict[str, int]  # {zone_id: counter}
    parent_hashes: List[str]  # witness chain
    content_hash: str
    payload: Any
```

---

### Theme 13 — Mode ≠ Computational Reality (Qwen-Max-Thinking)

**Voice**: "The state machine treats mode transitions as instantaneous, but PREDICTING/BACKTESTING are non-instantaneous computations. If UI shows PREDICTING while JEPA is still converging, user may misinterpret incomplete prediction as final."

**Generator's response**: Each mode has a **state sub-machine**:
- `declared_mode: Mode` (what UI shows)
- `actual_state: ModeState` (where: DORMANT, SPINNING_UP, RUNNING, DRAINING, ERROR)
- Transition gate: `declare → spin-up → running → drain → dormant`

For L1: PAUSED has sub-states (`PAUSE_REQUESTED`, `PAUSE_ACKNOWLEDGED`, `FULLY_PAUSED`). All workers report ack before declared PAUSED becomes actual PAUSED.

---

### Theme 14 — State Playback vs Weight Playback (Gemma — Pedagogical)

**Voice**: "In a DAW, the song is a static file. In Cellforge, the song is a live, mutating ML model. The user manipulates the causality of a learning system. A non-expert hits REWIND to see why a model made a mistake, changes an INFLUENCE_CELL to fix it, hits PLAY. But WEIGHT_CELLs have already evolved based on the wrong data. **State Playback** (data) vs **Weight Playback** (learning) conflation."

**Generator's response**: **REWEIGHT_CELL** holds the state of weights at tick N. When user rewinds, REWEIGHT_CELL is the source of truth for what weights SHOULD be at that tick. The rewind restores both state AND weights.

(REWEIGHT_CELL is a flavor of REPLAY_CELL — specialization for weights.)

---

### Theme 15 — Fork Multiverse UI (Gemma — Cognitive Load)

**Voice**: "The system introduces EXPERIMENT_LEDGER and FORK_VERSION_VECTOR. When you move through PLAYING → PREDICTING → COMPARING → PROMOTING, you maintain a mental map of multiple parallel realities. PROMOTING makes the present jump to a fork state. The user asks: did the other forks disappear? Where do I go back to?"

**Generator's response**: A **FORK_GRAPH_VIEW** in the projection agent. Shows all forks as a tree, lets user navigate to any fork's state, has a "return to canon" button. The UI is itself a cell (FORK_GRAPH_CELL with VIEW permission).

---

### Theme 16 — Predecessor Patterns (Hermes — Philosophical)

**Voice**: 
- Eternal Return (Nietzsche) — rewind = cyclical time
- Observer Effect (Heisenberg) — dispatcher alters state
- Counterfactual Thinking (Simon & Newell, GPS 1957) — predict/compare are CS-canonical

**Generator's response**: cellforge's design has intellectual heritage. The witness chain is Buddhist impermanence + the Log (Hindu record); the dispatcher is the Operator (Wiener cybernetics); the FORK_VERSION_VECTOR is GIT's DAG. Not novel in concept; novel in substrate (everything is a cell).

(Useful for the eventual whitepaper.)

---

### Theme 17 — Cross-Fleet Interference (Z-Interference)

**Voice**:
1. cellforge REWIND/PAUSE during training disrupts quilt-ai chains
2. Forked predictions conflict with mavis-fleet multi-substrate sync
3. Promotion without consensus breaks ax-quilt data integrity

**Generator's response**: Cross-fleet contracts. Each fleet namespace has its own CANON. cellforge writes to `canon:cellforge`. mavis-fleet writes to `canon:mavis-fleet`. Promotion across fleets requires explicit `canon:merged` event.

(For L1: this is documentation only. Cross-fleet contracts are v0.2+ scope.)

---

## L1 v0.1.0 — FINAL SCOPE (per Adversary consensus)

**Title**: `cellforge` v0.1.0 — The Killer Pause

**Scope**: Minimum that proves the inversion AND ships a memorable demo.

### 3 dispatcher modes
- **IDLE**: no ticks
- **PLAYING**: ticks flow at zone rate (A=100Hz, B=1Hz, C=human-paced)
- **PAUSED**: ALL workers halt on tick boundary within 14ms

### 1 new cell kind
- **FORK_VERSION_VECTOR**: { fork_id, parent_fork, sibling_forks, zone_id } (used by future versions)

### 8 original cell kinds (from Round 14)
- WEIGHT_CELL, ACTIVATION_CELL, GRADIENT_CELL, TOKEN_CELL, INFLUENCE_CELL, WITNESS_CELL, DISPATCH_CELL, ZONE_BOUNDARY_CELL

### 1 dispatcher as cell
- State machine is a value-cell. Writes propagate.

### Killer demo (the thing people remember)
- 100 simulated workers (mock linear regression, no PyTorch)
- Dispatcher ticks at 100Hz
- User writes `PAUSED` to DISPATCH_CELL
- Within 14ms: every worker acks, all halt on tick boundary
- Witness log shows: `TICK 142.0 PAUSE_REQUESTED`, `TICK 142.0 ACK_WORKER_017`, ..., `TICK 142.13 FULLY_PAUSED`
- Difference: max(worker_ack_tick) - min(worker_ack_tick) < 0.02 ticks

### Tests (~15)
1. tick() advances state
2. pause() halts tick within 14ms
3. resume() continues from current tick
4. fork_vector records parent_fork and sibling_forks
5. witness_chain integrity (vector-clock-ordered)
6. multi-worker ack on pause (the killer test)
7. zone A and B can have different pause states (zone-isolated pause)
8. WEIGHT_CELL versions persist across pause cycles
9. INFLUENCE_CELL TTL applied during PLAYING, ignored during PAUSED
10. dispatcher as cell — writing to DISPATCH_CELL propagates
11. PAUSE_REQUESTED → PAUSE_ACKNOWLEDGED → FULLY_PAUSED state machine
12. zonal pause (pause only Zone A)
13. force-pause (kill all workers, no ack required)
14. tick_drift test (pause + resume preserves tick alignment)
15. end-to-end: 100-worker pause (the killer demo test)

### CLI
```
cellforge init [name]                   # scaffold a workbook + dispatcher
cellforge add-cell <kind> <id>          # add WEIGHT_/ACTIVATION_/etc cell
cellforge start                         # dispatcher enters PLAYING
cellforge pause [--zone A] [--force]    # pause (optional zone/force)
cellforge resume                        # resume from current tick
cellforge fork <parent_fork>            # create fork with FORK_VERSION_VECTOR
cellforge status                        # dispatcher state, ack stats
cellforge witness                       # show witness log (vector-clock-ordered)
cellforge test-killer                   # run the 100-worker pause demo
```

### What v0.1.0 DOES NOT include (deferred to v0.2+)
- REWINDING, PREDICTING, COMPARING, BACKTESTING modes (Theme 11)
- REPLAY_CELL, PREDICTION_CELL, TIMELINE_CELL, EXPERIMENT_LEDGER (Theme 11 + Mistral)
- TEMPO_CELL, WRITE_QUORUM_CELL, SCHEDULE_CELL (Rounds 2-3)
- Master/child dispatcher hierarchy (Theme 8)
- Real PyTorch worker (use mock linear regression for L1; v0.2 adds real worker)
- REWEIGHT_CELL (Theme 14)
- FORK_GRAPH_VIEW (Theme 15)
- Cross-fleet canon contracts (Theme 17)

### Why this scope

The seed_pro finding is the most important: ship the inversion proof, ship the killer demo, ship fast. Every other finding can wait. 15 tests, 1 demo, 1 CLI. Ships in one session.

---

## Next Steps (Right Now)

1. **Run JEV-style promotion gate** on Round 4 findings (already noted above)
2. **Build cellforge v0.1.0** at `/workspace/repos/cellforge/`
3. **Run the killer demo** + all tests
4. **Push to GitHub** as `cellforge` (NOT mavis-cellforge — naming doctrine)
5. **Fleet canary check** (47 → 48 repos polyformal)
6. **Next round**: Ideate v0.2.0 with the deferred features
