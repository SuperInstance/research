# Cellforge Ideation — Round 0

*Casey's directive: "invert the relationship between state and execution. The Quilt cell matrix must be the permanent destination, and the low-level mathematical engines must be treated as disposable, hot-swappable utility workers."*

*Naming*: I'm going with **`cellforge`** for the production repo. Rationale: "cell" = substrate (matches `ax-quilt` family), "forge" = industrial training, transformation. An agent seeing the name + a one-line description should reach for it correctly.

---

## 1. Generator's Reading of the Architecture

The town-and-laborers metaphor is correct. Let me restate it in cellforge vocabulary:

| Layer | Casey term | cellforge term | Lifetime |
|-------|-----------|----------------|----------|
| 1 | Archival Canvas | **state_grid** (the cells, append-only ledger) | **permanent** — survives worker turnover |
| 2 | Contract Protocol | **op_manifest** (declarative ops between cell blocks) | **semi-stable** — versioned but doesn't break |
| 3 | Transient Workers | **forge_runtime** (PyTorch/JAX/CUDA backends) | **transient** — loaded per task, disposed |

The state_grid is what humans and agents see. The op_manifest is what bridges to the math. The forge_runtime is the disposable GPU work.

**The killer insight**: because the state_grid is the source of truth, **the grid outlives every model architecture**. Train a transformer today; train a state-space model tomorrow; train a diffusion model next week — they all read/write the same grid. The grid is the immutable substrate; the math is hot-swappable.

## 2. Adversary's Hidden-Assume Pokes

Let me play Adversary to the Generator's pitch and find what's hidden.

### Poke #1 — The Grid Schema Is Not Specified

The doc says "Row 1: Tokens, Row 2: Latent Embeddings, Row 3: Temporal Gradients." But what's the actual schema? Is it:
- A 2D grid (rows × columns)?
- A 3D tensor with named axes (like `ax-quilt`'s first-person orientation)?
- A hierarchical ledger (cells containing cells)?

**Hidden assumption**: the schema is just "rows and columns." But gradients live in their own time (per-step), tokens live in batch-space, weights live in their own parameter-space. **The grid needs HETEROGENEOUS axes, not just two.**

*Adversary verdict*: Use the **ax-quilt Orientation primitive** (already built). Each cell block declares its own X/Y/Z axes. Tokens: X=batch, Y=position, Z=feature. Gradients: X=parameter_id, Y=tick, Z=step_direction. Weights: X=parameter_id, Y=row, Z=column. Each is a different coordinate system on the same grid.

### Poke #2 — The "Worker Doesn't Remember" Claim Is Strong

The doc says "transient workers have no memory of the future; they simply wake up, look at the canvas at state 400, and begin executing forward passes."

But **how does the worker know it's at state 400?** The canvas is just cells. It needs a `current_tick` cell. Workers wake up, READ the `current_tick` cell, then read the rest of the grid at that tick.

**Hidden assumption**: that workers are stateless. But to do a forward pass you need:
- The current tick
- The cells holding weights at that tick
- The cells holding activations from the previous forward pass

If the previous forward pass's activations are in cells, then **the canvas IS the activation memory**. Workers don't need internal state — they read activation cells, write new activation cells, and exit.

*Adversary verdict*: The grid holds both **persistent state (weights)** and **transient computation (activations)**. Both are cells. The worker is genuinely stateless — the grid is the working memory.

### Poke #3 — Nudges Need TTL Semantics

The doc says "a human or an agent can gracefully write directly into an 'Influence Cell Block' while the system is running."

But what does "gracefully" mean?
- Does the nudge persist forever, or does it have a TTL?
- Does the next nudge override or compose?
- Does the worker know which cell is a "nudge" vs which is a "real value"?

**Hidden assumption**: nudges are persistent inputs. But training is dynamic — a nudge that made sense 10 ticks ago may not anymore.

*Adversary verdict*: Nudges need **TTL cells** with `valid_until_tick`. Workers check the TTL before applying. A nudge that has expired is silently ignored (or worse: the cell becomes a tombstone).

### Poke #4 — Heterogeneous Zones Need Topology

The doc says "Zone A (fast reflex), Zone B (slow critic), Zone C (nudge foundry)."

But how do the zones interact? Are they independent? Do they share cells? Is there a buffer between Zone A's output and Zone B's input?

**Hidden assumption**: zones are independent columns. But in real dual-system designs, **the slow system watches the fast system**. So Zone B reads Zone A's activations but never the other way.

*Adversary verdict*: Zones are **directional zones**. Zone B has Zone A as an INPUT (read-only). Zone A doesn't know Zone B exists. Zone C writes to A's influence cells but never to A's activations directly. **Topology matters.**

### Poke #5 — "Hot-swap Mid-training" Is Afoot with Live Steps

The doc says workers are disposable. But if PyTorch worker A is in the middle of a forward pass and worker B (e.g. JAX) takes over the next pass, **the activations in cells must be compatible**.

If worker A used float32 and worker B uses bfloat16, the activation cells might have stale precision.

**Hidden assumption**: workers can be swapped cleanly. But precision, layout (NCHW vs NHWC), and quantization all affect activation format.

*Adversary verdict*: Each cell block declares a **dtype policy** (e.g. `float32 | bfloat16 | int8`). Workers MUST write back in the declared dtype. Mismatch → cell records a "dtype violation" witness and refuses.

### Poke #6 — The Ledger of Cell Values Needs Compression

The doc says "append-only ledger of cell values" for rewind. But a transformer training run has billions of activations. Storing every activation forever is impossible.

**Hidden assumption**: we can afford full ledger. We can't.

*Adversary verdict*: **Hierarchical ledger**: keep `gradient` and `weight` cells with full history; keep `activation` cells with rolling window (last N ticks); keep `nudge` cells with TTL. Different cell kinds, different retention policies.

### Poke #7 — Who Decides Which Worker Comes?

The doc says "disposable, hot-swappable utility workers that visit the town." But who decides when a worker comes? Is there a scheduler? Is it a cell?

**Hidden assumption**: workers come on demand. But if no scheduler exists, **the worker is the scheduler**, which means the math engine decides when the math engine runs. That's circular.

*Adversary verdict*: There must be a **dispatcher cell** — a special cell that owns the worker lifecycle. The dispatcher cell reads `next_op` from the contract protocol and either spins up a worker (if available) or queues the op. The dispatcher itself is transient — when no ops are queued, it terminates. The town is empty until an op is published.

## 3. Generator's Counter-Critique

Adversary has 7 valid pokes. Some are tactical (TTL), some are deep (schema = orientation), some are existential (scheduler cell).

The deepest is **Poke #1 + #4**: the schema isn't just rows and columns, and zones have topology. Combined, this means **the cellforge Canvas is a heterogeneous, topologically-typed, multi-axis grid** — exactly what ax-quilt's first-person orientation + double-entry bookkeeping gives us.

## 4. The Deep Insight

**Cellforge = ax-quilt extended with three additions**:

1. **Heterogeneous cell kinds** with type-specific retention policies
   - `WEIGHT_CELL` — append-only ledger, every change recorded
   - `ACTIVATION_CELL` — rolling window (last N ticks), garbage-collected
   - `GRADIENT_CELL` — append-only ledger
   - `NUDGE_CELL` — TTL-bearing, expires when tick > valid_until_tick
   - `DISPATCH_CELL` — owns worker lifecycle
   - `WITNESS_CELL` — records every worker visit
   - `ZONE_CELL` — declares topology (what it can read from / write to)

2. **Op Manifest schema** — declarative ops between cell blocks
   ```
   op:
     name: attention_forward
     inputs: [block:activations.q, block:activations.k, block:activations.v]
     outputs: [block:activations.out]
     constraints: {dtype: float32, layout: NCHW, precision: 1e-5}
     worker_required: [pytorch | jax | custom_c]
     tick: 42
   ```

3. **Worker dispatch protocol** — workers come, do, leave
   ```
   1. Dispatcher cell reads next op from manifest
   2. Dispatcher spins up worker (or queues)
   3. Worker reads input cells, executes op
   4. Worker writes output cells (verifying dtype, layout, precision)
   5. Worker writes witness cell (signed timestamp, op id)
   6. Worker terminates
   7. Dispatcher reads next op
   ```

## 5. Adversary's Reply

Three additions is too few. The Adversary demands more:

- **Cross-worker polyformality** — when a PyTorch worker and a JAX worker both touch the same cell, do they agree? `mavis-axui-feedback`'s `polyformality_check` becomes mandatory here. Training must be deterministic across worker kinds.
- **Cell-as-being continuity** — using ax-quilt's "cell-as-being" doctrine from essay-127, each weight cell is a first-person observer of being touched by workers. It records who touched it, when, and what they wrote.
- **Distribution** — the town has multiple quarters. Different processes hold different zones. The cell grid is **distributed** — like ax-quilt's `quilt-spreadsheet` distributed clocks with skew. Workers in one process read cells in another; latency is the witness.

## 6. The Recommendation

**Start with B (spatial grid zones)** because the spatial structure IS the schema. Zones define what kinds of cells exist and how they talk.

**Build a dual-system demo** with three zones:
- Zone A — fast reflex worker (small transformer, 1B params)
- Zone B — slow critic worker (large transformer, 70B params)
- Zone C — nudge foundry (human/agent writes influence cells)

The demo proves:
- Rewind: roll the grid back to tick 400, watch both zones recompute forward
- Nudge: write a constraint into Zone C during training, watch Zone A incorporate it
- Hot-swap: kill Zone A's PyTorch worker, restart with JAX, verify polyformality

**Then layer A (Contract Protocol)** as the declarative surface that ties zones together.

**Naming for production**: `cellforge` (cell substrate + forge = where training happens). An untrained agent sees the name + description and knows it's for ML training on a cell grid. No surprise.

## 7. The Hidden Doctrine (the most interesting find)

When the Adversary pushed on "who decides when a worker comes?", the answer was: a **dispatcher cell**. When the Adversary pushed on "is the grid just rows and columns?", the answer was: use **ax-quilt's first-person orientation**, so each cell kind has its own axes.

Combined: **the dispatcher cell is itself a cell with its own orientation**. It lives in the town as one of the townsfolk. It's not a controller outside the system — it's a citizen. The grid is fully self-describing; no external scheduler exists.

This is **the Quilt doctrine applied to ML**: there is no "training script" outside the grid. The grid IS the training script. The dispatcher cell, the worker cells, the gradient cells, the activation cells, the witness cells — all are first-class citizens of the same town.

**ML training becomes a Quilt workbook.** A workbook is forever; the math is hot-swappable. This is the inversion Casey was asking for.
