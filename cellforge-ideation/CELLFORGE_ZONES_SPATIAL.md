# Cellforge Spatial Grid Zones — Design

*Picking **B (spatial grid zones)** as the next design move. The spatial structure IS the schema; cells without location are not cells.*

---

## 1. The Three-Zone Topology

The canvas is partitioned into three zones by **topological role**, not by physical location:

```
                    THE CELLFORGE CANVAS
                    (topologically-typed grid)

┌────────────────────────────────────────────────────────────────┐
│ ZONE A — FAST REFLEX ZONE                                     │
│ (autoregressive worker, 1B params, low latency)                │
│                                                                │
│ Cells: tokens, embeddings, attention weights (small),          │
│        activations (rolling window, last N ticks)              │
│ Read/Write: R/W from ZONE A only                               │
│ Worker contract: any pytorch/jax/cuda capable                  │
│ Tick rate: 100 Hz                                               │
└─────────────────────────┬──────────────────────────────────────┘
                          │ (read-only feeds Zone B's input block)
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│ ZONE B — SLOW CRITIC ZONE                                       │
│ (analytical worker, 70B params, high latency)                  │
│                                                                │
│ Cells: critic_weights, critic_state, safety_scores,            │
│        critiques, halt_signals                                 │
│ Read: from ZONE A (activations, attention) — read-only       │
│ Write: to ZONE C — write-only via critic.halt_signal          │
│ Worker contract: must declare reasoning trace on every emit   │
│ Tick rate: 1 Hz                                                 │
└─────────────────────────┬──────────────────────────────────────┘
                          │ (writes to influence cells)
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│ ZONE C — NUDGE FOUNDRY ZONE                                     │
│ (human/agent steering)                                         │
│                                                                │
│ Cells: influence_inputs (TTL-bearing), constraint_priors,      │
│        steer_targets, agent_directives                          │
│ Read: from anywhere — public interface                          │
│ Write: to ZONE A's input block + ZONE B's prior block          │
│ Worker contract: every write must declare TTL and reason       │
│ Tick rate: human/agent-paced                                   │
└────────────────────────────────────────────────────────────────┘
```

**Topology rule**: Zone B reads Zone A's activations but Zone A never reads Zone B. Zone C writes to A's input block and B's prior block. Zones are directional.

## 2. Cell Kinds Per Zone

Every cell on the canvas is one of these kinds:

| Cell kind | Lifetime | Retention | Zone |
|-----------|----------|-----------|------|
| `WEIGHT_CELL` | forever | full history (append-only ledger) | A, B |
| `ACTIVATION_CELL` | rolling N ticks | N most recent | A |
| `GRADIENT_CELL` | forever | full history | A |
| `TOKEN_CELL` | per-tick | last tick only (input data) | A |
| `INFLUENCE_CELL` | TTL-bearing | until tick > valid_until | C |
| `WITNESS_CELL` | forever | full history (signed log) | A, B, C |
| `DISPATCH_CELL` | per-op | last op | A, B |
| `ZONE_BOUNDARY_CELL` | forever | static | A, B, C |

## 3. Schema: How a Cell Block Declares Itself

Following ax-quilt's first-person orientation principle, each cell kind declares its own X/Y/Z axes:

```yaml
cell_kind: WEIGHT_CELL
  # A 70B parameter weight matrix: 80 layers × 64 heads × 128 dim
  axes:
    x_axis: { name: layer,    dtype: int, sorted: true,  monotonic: true }
    y_axis: { name: head,     dtype: int, sorted: true,  monotonic: true }
    z_axis: { name: dim,      dtype: int, sorted: false, monotonic: false }
  retention: full_ledger
  zone: A
  permissions:
    read: [ZONE_A, ZONE_B]   # critic can inspect weights
    write: [ZONE_A]           # only the training worker writes
```

```yaml
cell_kind: ACTIVATION_CELL
  # A 1B transformer activation: batch × seq × dim
  axes:
    x_axis: { name: batch,  dtype: int, sorted: false, monotonic: false }
    y_axis: { name: seq,    dtype: int, sorted: true,  monotonic: true }
    z_axis: { name: dim,    dtype: int, sorted: false, monotonic: false }
  retention: rolling_window_N_32
  zone: A
  permissions:
    read: [ZONE_A, ZONE_B]
    write: [ZONE_A]
```

```yaml
cell_kind: INFLUENCE_CELL
  # A nudge from a human or agent: target_heading=180° for ticks 410..450
  axes:
    x_axis: { name: param_id, dtype: string, sorted: false, monotonic: false }
    y_axis: { name: value,    dtype: float,  sorted: false, monotonic: false }
  retention: ttl_bearing
  zone: C
  permissions:
    read: [ZONE_A]   # worker reads the influence
    write: [ZONE_C]   # only humans/agents write here
  ttl: { valid_until_tick: 450, reason: "agent nudge: bias toward compliance" }
```

## 4. The Op Manifest Schema

When Zone A's dispatcher reads an op, it sees a declarative manifest:

```yaml
op:
  id: op-0042-attention
  name: attention_forward
  tick: 42
  zone: A

  inputs:
    - block: activations.q
      axes: { batch: 8, seq: 512, dim: 128 }
      dtype: float32
    - block: weights.qkv
      axes: { layer: 0, head: 0, dim: 128 }
      dtype: bfloat16
    - block: influence.bias
      axes: { param_id: "compliance" }
      dtype: float32
      ttl_check: must_be_valid_at_tick  # only apply if not expired

  outputs:
    - block: activations.out
      axes: { batch: 8, seq: 512, dim: 128 }
      dtype: float32
      verify:
        - precision >= 1e-5
        - layout == NCHW
        - not dtype_violation

  worker_required:
    capability: matmul_attention
    backends: [pytorch, jax, custom_c]

  witnesses:
    - on_entry: worker reads inputs, signs timestamp
    - on_exit: worker writes outputs, signs result_hash
    - chain: prev_witness_hash
```

The worker reads this manifest, does the work, writes the outputs (verifying dtype/layout/precision), writes the witness chain entry, and terminates.

## 5. The Dispatcher Cell

The dispatcher is a **cell**, not a controller:

```yaml
cell_kind: DISPATCH_CELL
  zone: A  # one per zone

  state:
    next_op_id: op-0043-ffn
    pending_ops: [op-0043-ffn, op-0044-layer-norm]
    active_workers: [worker-torch-A42]
    worker_pool:
      pytorch: available
      jax: cold_start_required
      custom_c: not_loaded

  on_tick:
    - if active_workers.is_empty():
        spawn worker from worker_pool
    - worker reads next_op
    - worker executes
    - on completion: worker writes outputs + witness
    - worker terminates
    - read next_op

  failsafes:
    - max_wall_time_per_op: 60s
    - max_memory_per_worker: 80GB
    - polyformality_check_required: false  # single worker per op
```

The dispatcher cell is a **first-class citizen** of the canvas. It can be inspected, paused, or replaced (with polyformality check).

## 6. The Polyformality Contract

When multiple worker kinds (PyTorch, JAX, C) compete for the same op, **the canvas enforces polyformality**:

```yaml
polyformality_check:
  op: op-0042-attention
  workers:
    pytorch_result: { hash: 0xa1b2c3d4, precision: 1e-5 }
    jax_result: { hash: 0xa1b2c3d4, precision: 1e-5 }
    custom_c_result: { hash: 0xa1b2c3d5, precision: 1e-6 }
  rule: any_two_agree_means_canon
  action_if_disagree: emit WARN, slow down, ask user
```

If two of three workers produce identical hashes (within tolerance), the result is canon. If they disagree, the canvas emits a WARN witness and asks for human intervention.

This is the **exact pattern** from `mavis-axui-feedback`'s `polyformality_check`, applied to ML training.

## 7. The Witness Chain

Every cell on the canvas participates in a witness chain. The chain is the canvas's memory of who touched what:

```
witness_cell[0]: { tick: 0, op: dispatch_init, actor: dispatcher, prev_hash: 0x000... }
witness_cell[1]: { tick: 1, op: attention_forward, actor: pytorch-A42, prev_hash: 0xa1b2... }
witness_cell[2]: { tick: 1, op: attention_forward, actor: jax-B17,    prev_hash: 0xa1b2... }
witness_cell[3]: { tick: 2, op: ffn_forward, actor: pytorch-A42, prev_hash: 0xc3d4... }
```

`mavis-axui-feedback`'s `FeedbackEvent.compute_hash()` and `prev_hash` chaining is the model.

## 8. Rewind = Truncate the Ledger

To rewind to tick 400:

```
1. Find witness_cell[400] — the snapshot at tick 400
2. For every cell on the canvas, restore its value at tick 400
   (cells with full_ledger retention have all history)
   (cells with rolling_window_N_32 only have last 32 ticks — rewind is bounded)
3. Dispatcher resumes from tick 400
4. Workers come, see the canvas at tick 400, execute forward
```

No GPU state to dump. No checkpoint files. The canvas IS the checkpoint.

**Bounded rewind**: cells with rolling-window retention can only rewind as far as their window allows. This is the trade-off: weight cells can rewind forever; activation cells only rewind to the last N ticks.

## 9. Nudge = Write to Influence Cell

A human or agent nudges the system by writing to a Zone C `INFLUENCE_CELL`:

```
1. Human writes influence.bias = {"compliance": 0.8}
2. Influence cell records: { tick: 42, writer: human, ttl: valid_until_tick: 50, reason: "..." }
3. Next op that includes influence.bias in inputs:
   - Worker reads influence.bias
   - Worker checks TTL: tick 42 <= valid_until_tick 50? YES, apply
   - Worker incorporates the bias into the math
   - Worker writes witness: { tick: 43, applied_nudge: compliance=0.8, ttl: 50 }
4. After tick 50: the influence cell expires; subsequent ops ignore it
```

This is **graceful nudging** without interrupting running kernels. The math engine reads the cell; if the cell has expired, it ignores; if not, it applies.

## 10. The First Build

**Start with a minimal cellforge demo** that proves the architecture:

1. **One WEIGHT_CELL** (a 64x64 weight matrix, no zones)
2. **One ACTIVATION_CELL** (a 8x8 activation tensor)
3. **One DISPATCH_CELL** that runs a `matmul` op
4. **One WITNESS_CELL** that records every dispatch
5. **One pytorch worker** as the transient laborer

The demo shows:
- Worker spawns, reads inputs, executes matmul, writes outputs
- Worker writes witness, terminates
- Canvas survives worker termination (rewind works)
- A second worker (JAX) takes over — polyformality check shows identical results

This is the **L1 (single cell)** of cellforge, before zones. Once L1 works, layer in Zone A → Zone B → Zone C → multi-worker polyformality.

## 11. The Naming Argument

I'm naming the production repo **`cellforge`**:
- "cell" → substrate, matches ax-quilt family
- "forge" → industrial-scale training, transformation, hot
- An untrained agent seeing `cellforge` + description "ML training on a cell-grid canvas with hot-swappable workers" reaches for it correctly
- No "mavis-*" prefix (per Casey: persona internal, production external)

Internal research file: `/workspace/research/cellforge-ideation/` — persona artifact, OK to keep descriptive without prefix.
