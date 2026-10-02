# GAN Loop Synthesis — Round 7

*Casey's directive: "iteratively play-testing and developing in a GAN loop. the key is to really understand what we are trying to do at the highest levels so the GAN's abilities actually emerge and new insightful challenges are appearing at all times."*

---

## The loop's shape

```
                    ┌────────────────────────────┐
                    │     Generator (Mavis)      │
                    │  Proposes next-builds      │
                    │  from current momentum     │
                    └─────────────┬──────────────┘
                                  │ proposes
                                  ▼
                    ┌────────────────────────────┐
                    │   Candidate build          │
                    │   (4 routes: TIME/COST/    │
                    │    FAILURE/PLURALITY)      │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │   Adversary critique       │
                    │  Pokes hidden assumptions  │
                    │  Surfaces 5-7 new holes    │
                    └─────────────┬──────────────┘
                                  │ finds holes
                                  ▼
                    ┌────────────────────────────┐
                    │   Fixes (next builds)      │
                    │   → reveal new assumptions │
                    │   → loop continues         │
                    └────────────────────────────┘
```

## Round-by-round ledger

### Round 0 — Highest-level doctrine candidates

Generator: 6 candidates (workbook-as-observer, three-projections, double-entry, verb-discovery, first-person, observation-as-field).

Adversary: All 6 hide **time**, **cost**, **failure**, **plurality**.

### Round 1 — Four next-builds

Generator proposes TIME_cell_as_tick, COST_cell_as_resource, FAILURE_cell_as_mortal, PLURALITY_cell_as_swarm.

Adversary: 3 are extensions (just add columns). PLURALITY is the revolution — it changes the type of Cell from `Cell` to `Cell = Union[Atomic, Compound]`.

### Round 2 — Synthesis

Generator: build PLURALITY first.

Adversary: PLURALITY is a 30-day project. Build TIME first (1 hour), HONESTY next (1 day), then PLURALITY (1 week).

**Adversary counter-counter-critique**: but the boat LED matrix has its own workbook. The LED matrix projects to the runtime. The runtime feeds back. **This is bidirectional projection.** One build, contains TIME + HONESTY + PLURALITY.

### Round 3 — Build bidirectional projection

Built `FeedbackRing`, `FeedbackCell`, `SubWorkbook`. 14 tests pass.

### Round 4 — Adversary pokes 5 holes

1. **infinite loop** — what stops oscillation?
2. **lossy projection** — NMEA rounds 0.001°, LED rounds 1°. Feedback over lossy channels corrupts.
3. **phantom cells** — sub-workbook cells only exist when projection is active.
4. **witness chain breaks** — feedback splits the witness log.
5. **type the feedback** — current code mixes Flow, State, Action.

### Round 5 — Build typed events

5 typed events (COMMAND, STATE, ACTION, TICK, WITNESS), hash-chained, lossy projection with `precision`, oscillation detection, `max_ticks_per_session`.

26 tests pass.

### Round 6 — Adversary pokes 7 more holes

1. finite state (where's the QUILT?)
2. no canary
3. phantom runtime (None adapter = unplugged LED)
4. typed events lock doctrine
5. lossy one-way (runtime should declare its precision)
6. recursion depth (PLURALITY in disguise)
7. **unsigned commands (an attacker injects target_heading=180 → reef)**

### Round 7 — Build SIGNED commands + polyformality + phantom detection

HMAC-SHA256 signed commands. `polyformality_check(rings)` measures agreement. `phantom_runtime_warning` emits when adapter is None. `runtime_precision` honors runtime's capability. `max_recursion_depth` bounds plurality. `sign_command`/`verify_command_signature` with replay rejection.

**42 tests pass. 47/47 fleet polyformal.**

## Insights from the loop

### 1. The Generator's blindspot is its own momentum

Every Generator proposal had alignment ≈ +0.99 with current momentum. The Adversary's job is to find what's NOT in the momentum — the orthogonal ideas that the Generator is filtering out by inertia.

### 2. Holes the Generator hides are not bugs

The Adversary's findings (phantom runtime, lossy projection, unsigned commands) were not errors — they were **doctrinal gaps** the Generator hadn't yet seen. Each hole became a feature.

### 3. Adversary score correlates with depth

`polyformality_check` scores agreement between rings. Same logic: features that align with current doctrine are easy. Features that are orthogonal are hard but deep.

| Round | Adversary challenge | Score | Depth |
|-------|---------------------|-------|-------|
| 1 | PLURALITY_cell_as_swarm | +0.991 | deepest |
| 4 | infinite_loop | +0.999 | shallow (one-line fix) |
| 4 | lossy_projection | +0.994 | medium |
| 6 | the_user_input_doesnt_sign | +0.788 | deepest of round 6 |

### 4. Three doctrinal generations emerged

- **Round 0-2**: extensions — TIME, COST, FAILURE (add columns)
- **Round 3-5**: rings — bidirectional, typed events (add dimensions)
- **Round 6-7**: hardening — signatures, polyformality, recursion bounds (add defenses)

Each generation was forced by deeper Adversary pokes.

### 5. The boat example is the test oracle

Every round's Adversary critique came back to: "what about the boat?". The LED matrix is a feedback runtime. The encoder projects back. The compass rounds to 1°. The autopilot signs its commands. **The boat-as-Quilt example keeps forcing real bugs into the abstract design.**

## What the loop should do next

Round 8 candidates:
- **Cross-ring agreements** — what happens when ring1 says "180°" and ring2 says "181°"? Need a tie-breaker.
- **Time-skewed feedback** — the LED ring runs at 10Hz but the autopilot runs at 1Hz. How do they sync?
- **Multi-cell commands** — a single runtime input affects multiple cells.
- **Adversarial runtime** — what if the runtime adapter is hostile? (signatures help; what else?)

The loop continues. Each round reveals a deeper layer.

## Files

- `/workspace/repos/mavis-axui-feedback/` — v0.2.0, 42 tests
- `/workspace/research/gan-loop/ROUND_0_doctrine_candidates.md`
- `/workspace/research/gan-loop/ROUND_2_adversary_pokes.md`
- `/workspace/research/gan-loop/SYNTHESIS.md` (this file)

**GitHub**: https://github.com/SuperInstance/mavis-axui-feedback

## Cross-project durable insight

**The GAN loop is now a tool.** `mavis-axui-feedback` includes the loop's code, tests, and lessons. Any future proposal can be fed through the Generator + Adversary pattern to surface doctrinal gaps before they ship.

**The Generator has a hidden momentum** — its current vector. The Adversary's job is to find orthogonal directions. The Generator then adopts them, growing the momentum.

**The boat example is a persistent test oracle.** Every doctrinal hole surfaces there. The boat's realism keeps the abstraction honest.
