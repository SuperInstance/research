# Cellforge Contract Protocol — Design

*After spatial zones (B), the Contract Protocol (A) is the API surface between zones. This is the second design move.*

---

## 1. Why the Contract Is Necessary

The spatial zones answer **where** (which cells exist, in which zone). The Contract Protocol answers **what** (what ops can run, what they read/write, what constraints they satisfy).

Without a contract, a PyTorch worker might write bfloat16 to a cell declared as float32. Without a contract, Zone B's critic might accidentally write to Zone A's activations (breaking the directional topology). Without a contract, the dispatcher has no way to know what worker capabilities are needed.

The Contract Protocol is the **declarative surface** that ties the canvas together.

## 2. The Contract Schema (L1)

A minimal contract has four parts:

```yaml
contract:
  id: contract-attention-001
  version: 1

  op:
    name: attention_forward
    description: |
      Multi-head scaled-dot-product attention.
      Reads q, k, v; computes softmax(QK^T / sqrt(d))V.
    
  inputs:
    - name: q
      block: activations.q
      dtype: float32
      layout: [batch, head, seq, dim]   # NHWC vs NCHW must match
      required: true
      
    - name: k
      block: activations.k
      dtype: float32
      layout: [batch, head, seq, dim]
      required: true
      
    - name: v
      block: activations.v
      dtype: float32
      layout: [batch, head, seq, dim]
      required: true
      
    - name: influence_bias
      block: influence.bias
      dtype: float32
      layout: [param_id]
      required: false
      ttl_required: true   # worker MUST check valid_until_tick
      
  outputs:
    - name: out
      block: activations.out
      dtype: float32
      layout: [batch, head, seq, dim]
      verify:
        - dtype_match: float32
        - layout_match: [batch, head, seq, dim]
        - precision: 1e-5
        - no_nan: true

  workers:
    capability: matmul_attention
    backends_allowed:
      - pytorch
      - jax
      - custom_c
    backends_required_min: 1   # at least one must accept
    
  witnesses:
    on_entry: 
      - cell: witness_chain
        action: append { tick, op_id, worker_id, input_hashes }
    on_exit:
      - cell: witness_chain
        action: append { tick, op_id, worker_id, output_hash, precision }
```

## 3. Contract Versioning (L2)

When workers change (PyTorch 2.0 → PyTorch 3.0), contracts evolve. The canvas must track:

```yaml
contract_lifecycle:
  v1:
    introduced_tick: 0
    deprecated_tick: 1000
    retired_tick: 2000
    
  v2:
    introduced_tick: 1000
    changes_from_v1:
      - inputs.k now optional (allows GQA)
      - outputs.out dtype changed to bfloat16
    polyformality_bridge:
      - "v1 outputs can be converted via contract_translator.float32_to_bfloat16"
```

A **contract translator** cell sits between contracts of different versions. The translator cell is itself a cell on the canvas, with its own witness chain.

## 4. Cross-Zone Contracts

The three zones communicate via contracts. The directional topology is enforced by the **contract's read/write declarations**:

```yaml
contract:
  id: contract-zone-A-to-B-feed
  
  # Zone A's activations feed Zone B
  source:
    zone: A
    block: activations.out
    contract: contract-attention-001
  
  destination:
    zone: B
    block: critic_input.feed
    access: read_only       # Zone B can read but not write
    
  translator:
    - source.layout: [batch, head, seq, dim]
      destination.layout: [batch, seq, head, dim]   # transpose for critic
      loss_tolerance: 1e-7                          # translator introduces loss
```

Zone B's contract says `access: read_only` for the feed. Any Zone B worker that tries to write to `activations.out` triggers a contract violation witness and is rejected.

## 5. The Dispatcher's View

When Zone A's dispatcher reads the contract, it sees:

```yaml
dispatch_plan:
  contract: contract-attention-001
  tick: 42
  
  inputs_available:
    activations.q: { present: true, dtype: float32 }
    activations.k: { present: true, dtype: float32 }
    activations.v: { present: true, dtype: float32 }
    influence.bias: { present: true, valid_until_tick: 50 }
    
  outputs_target:
    activations.out: { capacity: 32KB, dtype: float32 }
    
  workers_available:
    pytorch: ready
    jax: cold_start_required
    custom_c: not_loaded
    
  selection_strategy: round_robin_with_fallback
  fallback_chain: [pytorch, jax, custom_c]
  
  expected_wall_time: 200ms
  expected_memory: 8GB
```

The dispatcher picks the first available worker and dispatches. If it fails, the next in the fallback chain tries.

## 6. The Nudge Contract

When a human or agent nudges via Zone C, the contract specifies what they can and cannot do:

```yaml
contract:
  id: contract-nudge-001
  
  writer:
    role: [human, agent]
    authentication: signed_with_nudge_key
    
  allowed_writes:
    - block: influence.bias
      ttl_required: true
      max_value_range: [-10.0, 10.0]
      requires_reason: true
      
    - block: steer_targets
      ttl_required: true
      max_value_range: [-1.0, 1.0]
      requires_reason: true
      
  forbidden_writes:
    - block: weights.*           # weights are training's domain
    - block: gradients.*          # gradients are training's domain
    - block: activations.*        # activations are transient
  
  on_write:
    - cell: witness_chain
      action: append { tick, writer, block, value, reason, ttl }
```

Zone C writes to influence cells. Zone C **cannot** write to weights, gradients, or activations. The contract enforces the boundary.

## 7. The Witness Contract

Every cell that participates in the chain has a witness contract:

```yaml
contract:
  id: contract-witness-001
  
  witness_format:
    schema_version: 1
    fields:
      - tick: int
      - op_id: string
      - actor: string         # worker_id, dispatcher_id, or human/agent
      - cell_block: string    # which block was touched
      - action: enum          # read | write | dispatch | terminate
      - prev_hash: string     # chain link
      - hash: string          # this entry's hash
      
  signing:
    algorithm: hmac-sha256
    key_derivation: cell_id + cell_kind + zone
    
  retention: full_ledger    # witness chain is forever
  pruning: never             # casey doctrine: NO DELETION
```

## 8. The Hot-Swap Contract

When the dispatcher swaps worker kinds mid-flight, the swap follows a contract:

```yaml
contract:
  id: contract-hot-swap-001
  
  trigger:
    - user_command: "swap pytorch → jax"
    - automatic: worker_error_threshold_exceeded
    - automatic: better_worker_available
  
  pre_conditions:
    - all_pending_ops_drained: true
    - current_worker_terminated: true
    - witness_chain_complete: true
    
  steps:
    - pause_dispatcher
    - wait_for_active_workers_to_terminate
    - verify_witness_chain_complete
    - signal_new_worker_to_cold_start
    - resume_dispatcher
  
  guarantees:
    - no_op_lost: true
    - no_state_corrupted: true
    - rewind_to_pre_swap_state: possible
```

The hot-swap contract is itself a contract on the canvas. The dispatcher follows it like any other op.

## 9. Putting It Together

The Contract Protocol + Spatial Zones = the full cellforge architecture:

```
┌────────────────────────────────────────────────────────────┐
│ THE CELLFORGE CANVAS                                       │
│                                                            │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│   │ ZONE A       │    │ ZONE B       │    │ ZONE C       │ │
│   │ Fast Reflex  │───▶│ Slow Critic  │    │ Nudge        │ │
│   │              │    │              │◀───│ Foundry      │ │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
│          │                   │                   │         │
│          ▼                   ▼                   ▼         │
│   ┌────────────────────────────────────────────────────┐  │
│   │              CONTRACT PROTOCOL                      │  │
│   │  - op contracts (attention, ffn, layer-norm)        │  │
│   │  - cross-zone contracts (A→B feed, B→C halt)       │  │
│   │  - nudge contracts (influence writes, TTL)          │  │
│   │  - witness contracts (chain, signing)               │  │
│   │  - hot-swap contracts (worker dispatch)              │  │
│   └────────────────────────────────────────────────────┘  │
│                          │                                 │
│                          ▼                                 │
│   ┌────────────────────────────────────────────────────┐  │
│   │              TRANSIENT WORKERS                      │  │
│   │  PyTorch, JAX, custom C, future TPU, neuromorphic   │  │
│   └────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

## 10. The First Build (Updated)

After spatial zones + contract protocol, the **first build** is:

1. **One WEIGHT_CELL** (a 64x64 weight)
2. **One ACTIVATION_CELL** (a 8x8 activation)
3. **One DISPATCH_CELL** that runs a `matmul` op via `contract-matmul-001`
4. **One WITNESS_CELL** recording every dispatch via `contract-witness-001`
5. **One pytorch worker** as the transient laborer
6. **One translator cell** between contract v1 and v2 (forward-compatible from day one)

The demo proves:
- Worker spawns, reads contract, executes matmul, writes outputs
- Worker writes witness, terminates
- Canvas survives worker termination (rewind works)
- A second worker (JAX) takes over via `contract-hot-swap-001` — polyformality check shows identical results
- The contract can be upgraded to v2 without breaking the canvas

This is the **L2 (multi-cell + contract)** of cellforge, after L1 (single cell) and before L3 (multi-zone).
