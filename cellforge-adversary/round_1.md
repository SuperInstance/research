# Adversary Round 1

**Date**: 2026-09-23T16:34:51.063687Z
**Duration**: 10.8s
**Voices**: zai, groq, deepseek, deepinfra_hermes, deepinfra_seed, moth

---

## groq

[groq ERROR: HTTPError: HTTP Error 403: Forbidden]

---

## moth

[moth ERROR: HTTPError: HTTP Error 403: Forbidden]

---

## zai

[zai ERROR: HTTPError: HTTP Error 429: Too Many Requests]

---

## deepinfra_seed

[deepinfra ERROR: HTTPError: HTTP Error 404: Not Found]

---

## deepinfra_hermes

[deepinfra ERROR: HTTPError: HTTP Error 404: Not Found]

---

## deepseek

## Finding 1: The dispatcher assumes tick rate is decoupled from wall-clock, but JEPA/JEV promotion needs a *commitment horizon* — and none is specified

The design says PREDICTING writes to a forked ledger, JEV compares prediction vs eventual witness, high agreement → promote. But **when** does JEV decide? The doc never says. In a real training run this is fatal.

Concrete failure: dispatcher is PLAYING at Zone A = 100Hz. JEPA emits a PREDICTION_CELL for tick N+500 (5 seconds of wall-clock future). To verify, JEV must wait until tick N+500 actually arrives. But if the user hits `freeze()` at tick N+200, or `rewind(N-100)`, or `predict()` again — what happens to the pending prediction? Three sub-cases, none handled:

- **Freeze mid-horizon**: prediction is orphaned. Its witness never arrives. Does it auto-expire? Get marked `unverifiable`? Silently linger in EXPERIMENT_LEDGER forever?
- **Rewind past the prediction's origin**: the prediction was made from a state that "no longer happened." Is it invalidated? The doc says REWINDING is read-only, but the prediction is now a claim about a branch that was rewound away.
- **Second predict() before first resolves**: do you now have overlapping predictions on the same horizon? JEV has to compare N predictions against 1 eventual witness. Which one "wins" promotion?

At 100Hz with JEPA predicting even 1 second ahead, you have 100 in-flight predictions per zone. Multiply by 3 zones and multiple scenarios per predict() call — this is a **backpressure problem the design doesn't acknowledge**. Real transformer training runs at 10-50 steps/sec on the training loop, but the *observation* rate (loss, grad norms, activation stats) is what JEPA would predict on, and that's often logged at every step or every N steps. If predictions pile up faster than witnesses arrive, EXPERIMENT_LEDGER's `ttl_bearing` retention becomes a silent data-loss vector — TTL expires predictions before JEV can verify them.

The hidden assumption: **prediction horizon < time between user interventions**. In a real training run where someone is actively watching loss curves and hitting pause to inspect, this is false. The design needs an explicit `prediction_commitment_tick` on every PREDICTION_CELL and a JEV policy for orphaned/overlapping/superseded predictions. Without it, promotion becomes a race condition.

## Finding 2: Missing concept — **checkpoint/restore semantics for the fork itself**

The design treats "fork the ledger" as free. It's not. A PREDICTING mode fork at tick N doesn't just need the witness chain up to N — it needs the *entire cell state* at N: every PREDICTION_CELL's rolling window, every INFLUENCE_CELL's current value, every MOCK's TTL clock, every zone's rate. In a real training run, that state includes optimizer momentum buffers, RNG state, dataloader position, and EMA weights. You cannot "predict what if I change X" without being able to reconstruct the *exact* state at fork time.

Concrete failure: user is training a transformer, at step 10,000 they want to predict "what if LR were 2x from here?" They call `predict(start_tick=10000, scenarios=[lr_2x])`. The dispatcher forks the ledger. But:

- The fork only contains *witnessed cells*, not the training process's internal state (optimizer, RNG, dataloader).
- JEPA predicts on cell states, but the cells don't contain Adam's second-moment estimates.
- The prediction is therefore about *observable outputs* (loss, activations) not *causal state*. It's a curve fit, not a simulation.

This is the difference between "predicting the loss curve" and "actually running the alternative training." The design conflates them by calling it a "fork." A real fork requires **checkpoint cells** — a new cell kind that snapshots opaque external state (model weights, optimizer, RNG seed, dataloader offset) at a tick, with a `restore()` opcode. Without it, BACKTESTING mode is theater: you're replaying witnesses and asking JEPA to imagine what would have happened, not actually re-running.

The OS metaphor table lists "Predictive execution | forked ledgers" — but real OSes fork *process memory*, not just logs. The design has the log but not the memory. Add `CHECKPOINT_CELL` with retention `pinned_until_released` and a `RESTORE` opcode, or admit that PREDICTING is interpolation, not simulation.

## Finding 3: Test case that breaks the design — **"resume from rewind while a prediction is in flight"**

Setup: 3-zone dispatcher, Zone A at 100Hz. Ticks 0-1000 witnessed. At tick 1000, user calls `predict(start_tick=1000, scenarios=[S1, S2])`. Two PREDICTION_CELLs created, targeting ticks 1000-1500. JEPA is running. At tick 1050 (mid-prediction), user calls `rewind(N=800)` — dispatcher enters REWINDING, playhead moves back to tick 800. Then user calls `resume()` → PLAYING from tick 800. Ticks 800-1000 are re-witnessed (same values, deterministic replay). At tick 1000 again, tick 1001, ... 1050, ... the original prediction's horizon ticks arrive *again*.

Now what?

- **Option A**: JEV compares the original prediction (made from tick 1000's state) against the *re-witnessed* tick 1000-1500. But the re-witness is the same as the first time (deterministic replay), so it should match. Except — did anything change between the two passes? If the user touched an INFLUENCE_CELL during the rewind window, the re-witness diverges. Now JEV is comparing a prediction against a *different* timeline than the one it was made in.
- **Option B**: The prediction is invalidated by the rewind, and JEV never runs. But then PREDICTING silently loses work whenever a user scrubs the timeline — which is the *primary interaction pattern* the design is selling.
- **Option C**: The prediction survives, and JEV compares against the *first* witness (cached), ignoring the re-witness. But then the re-witness and the prediction are both "true," and promotion becomes ambiguous: which witness becomes canon?

The design has no answer because it never defines **identity of a tick**. Is tick 1000 a position in time (replayable, single canonical value) or an event (each occurrence is distinct)? The witness chain implies the former; the forkable ledger implies the latter. You can't have both without an explicit `(tick, branch_id)` coordinate, and the design has no branch_id anywhere.

Concrete transformer example: mid-training, user rewinds to inspect a loss spike at step 8000. They resume. The dataloader shuffles differently (RNG advanced), so step 8000-9000 now see *different batches*. The witnesses diverge. Any prediction made before the rewind is now a prediction about a timeline that no longer exists. JEV either promotes a wrong prediction or drops a correct one. Either way, the "canon" ledger is now a lie about what the model actually trained on.

**Fix**: every tick must be `(tick, branch_id)`, dispatcher mode transitions must emit a `branch_id` fork event, and JEV must refuse to compare predictions across branch boundaries. The design's 1D playhead is actually 2D (time × branch), and the doc flattens it.

---

