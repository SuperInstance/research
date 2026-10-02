# QUILT — MCPMempool as a tappable cell-graph

This is the **Quilt projection layer** for MCPMempool. The original
TypeScript auto-scaling memory-pool manager is preserved (see
`UPSTREAM.md`); this document shows how the same program becomes
**visible as a tappable cell-graph** using the 5+1 opcodes.

Audience: applied engineers who know memory-pool management / scheduling
/ TypeScript but not necessarily Quilt.

## The big idea — every mempool op is a cell

A memory pool is a **queue of cells**. Every allocation is a BIND. Every
deallocation is a FORGET. Every priority change is an EFFECT. Every
read is a VIEW. The auto-scaler is a TICK-bound policy.

The Quilt projection doesn't change the runtime — it makes the queue
**visible and tappable**. You can click any cell in the mempool, see its
address, its priority, its timestamp, and either let it run or manually
trigger its next state.

## What the cell-graph looks like

```
                  ┌────────────────────────────┐
                  │   cell:mempool_root        │  type=pool
                  │   value={                  │  axis=role
                  │     capacity: 100,         │
                  │     cells: [...],          │
                  │     policy: 'priority'     │
                  │   }                         │  link: cell (one per op)
                  └──────────────┬─────────────┘
                                 │ (typed: "contains")
                                 ▼
       ┌────────────────────────────────────────────────┐
       │                                                │
┌──────▼──────────────┐    ┌─────────────────┐    ┌─────▼─────────────┐
│  cell:op_1          │    │  cell:op_2      │    │  cell:op_3       │
│  type=operation     │    │  type=operation │    │  type=operation  │
│  value={            │    │  value={        │    │  value={         │
│    kind: 'alloc',   │    │    kind: 'free',│    │    kind: 'write', │
│    size: 4096,      │    │    ptr: 0x1000, │    │    ptr: 0x2000,  │
│    priority: 5,     │    │    priority: 9, │    │    priority: 3,  │
│    status: 'queued' │    │    status: 'run'│    │    status: 'done'│
│  }                   │    │    }            │    │    }             │
│  axis=lifecycle     │    │  axis=lifecycle │    │  axis=lifecycle  │
│  link: scheduler    │    │  link: scheduler│    │  link: scheduler │
└──────────────────────┘    └─────────────────┘    └──────────────────┘
```

## The 5+1 opcodes in action

Every mempool operation maps to a Quilt opcode:

| Mempool action | Quilt opcode | Effect |
|---|---|---|
| Enqueue operation | `BIND(cell:op_n)` | New cell added to pool |
| Update priority | `EFFECT(cell, lambda v: {**v, priority: new_p})` | Cell priority updates |
| Status change | `EFFECT(cell, lambda v: {**v, status: new_s})` | Cell status updates |
| Run operation | `EFFECT(cell, lambda v: execute(v))` | Side-effect happens, status → 'done' |
| Read operation | `VIEW(cell)` | Pure read |
| TICK (scheduler pulse) | `TICK(dt)` | Clock advances, scheduler picks next |
| Dequeue operation | `FORGET(cell)` | Cell removed from pool |

## The cell subtypes

| Cell | Type | Lifecycle |
|---|---|---|
| `cell:mempool_root` | Pool container | `BIND` once at startup |
| `cell:op_n` | One operation per enqueue | `BIND` on enqueue, `FORGET` on dequeue |
| `cell:scheduler` | Priority-aware router | `BIND` once |
| `cell:autoscaler` | Capacity adjuster | `BIND` once, `EFFECT` per scale event |
| `cell:metrics` | Pool statistics (utilization, throughput, latency) | `BIND` once, `EFFECT` per metric update |

## The witness chain

Every state change appends to a witness log:

```
BIND cell:mempool_root capacity=100 policy=priority @ tick=0
BIND cell:op_1 {kind:alloc, size:4096, priority:5, status:queued} @ tick=10
BIND cell:op_2 {kind:free, ptr:0x1000, priority:9, status:queued} @ tick=11
EFFECT cell:op_2 → status=run @ tick=15
EFFECT cell:op_2 → status=done @ tick=16
EFFECT cell:autoscaler → capacity=120 (load+20%) @ tick=42
EFFECT cell:op_3 → priority=8 (was 3, bumped) @ tick=58
BIND cell:op_3 {kind:write, ptr:0x2000, priority:3, status:queued} @ tick=63
EFFECT cell:op_3 → status=run @ tick=70
EFFECT cell:op_3 → status=done @ tick=71
FORGET cell:op_1 @ tick=72
```

The witness chain IS the mempool's audit trail. Replay it and you see
the exact order of operations. This is critical for memory-pool
debugging — figuring out why a specific allocation pattern caused an
issue.

## Polyformal port plan

The same cell-graph ports to:

| Port | What it adds |
|---|---|
| **TypeScript (upstream)** | Already running. The tappable UI just makes the cells visible. |
| **Python simulator** | Reference port for testing; `asyncio` for the scheduler |
| **C / production** | Real memory-pool management; cells map to actual heap slots |
| **JSON-API** | REST over the cell-graph; deployable to a Cloudflare Worker |
| **Pico firmware** | The "mempool" becomes a sensor-buffer pool; cells map to ring buffer slots |

## Integration with the broader Quilt ecosystem

- **`quilt-cordis`** — the cell-plugin bridge. The mempool becomes a
  Cordis plugin with reversible effects.
- **`quilt-casting`** — model router. If you add a "predict next op"
  AI suggestion, the casting plugin picks which model predicts.
- **`flx-cuda`** — GPU-accelerated priority scheduling. Thousands of
  ops queued in the cell-graph, scheduler runs as a GPU kernel.
- **`flux-hardware`** — the hardware backend picker. CUDA for batch,
  FPGA for latency-critical scheduling.
- **`conservation-art`** — the conservation law applies to mempool:
  *every allocation is paired with a deallocation* (the conservation of
  memory).

## Code example (Python, reference port — tappable cells)

```python
from quilt import Cell, Substrate

class MCPMempoolCell:
    """One mempool operation as a tappable Quilt cell."""

    def __init__(self, substrate, kind, size=None, ptr=None, priority=5):
        self.cell = substrate.bind(Cell(
            address=f"op_{substrate.next_id()}",
            value={
                "kind": kind,
                "size": size,
                "ptr": ptr,
                "priority": priority,
                "status": "queued",
                "timestamp": substrate.tick_count,
            },
        ))

    def bump_priority(self, new_priority):
        """EFFECT — manually raise or lower the cell's priority."""
        self.cell.effect(lambda v: {**v, "priority": new_priority})

    def run(self):
        """EFFECT — execute the operation."""
        self.cell.effect(lambda v: {**v, "status": "running"})
        # ... do the work ...
        self.cell.effect(lambda v: {**v, "status": "done"})

    def dequeue(self):
        """FORGET — remove from the pool."""
        self.cell.dispose()


class MCPMempool:
    def __init__(self, capacity=100):
        self.substrate = Substrate(name="mcpmempool")
        self.root = self.substrate.bind(Cell(
            address="mempool_root",
            value={"capacity": capacity, "policy": "priority", "cells": []},
        ))
        self.scheduler = self.substrate.bind(Cell(address="scheduler"))
        self.autoscaler = self.substrate.bind(Cell(address="autoscaler"))
        self.metrics = self.substrate.bind(Cell(address="metrics"))
        self._next = 0

    def next_id(self):
        self._next += 1
        return self._next

    def enqueue_alloc(self, size, priority=5):
        return MCPMempoolCell(self.substrate, "alloc", size=size, priority=priority)

    def enqueue_free(self, ptr, priority=5):
        return MCPMempoolCell(self.substrate, "free", ptr=ptr, priority=priority)

    def tap_cell(self, addr):
        """Tappable — return the current state of a cell for human inspection."""
        return self.substrate.view(addr)


# Demo
pool = MCPMempool()
op_a = pool.enqueue_alloc(size=4096, priority=5)
op_b = pool.enqueue_free(ptr=0x1000, priority=9)  # higher priority

# Tap a cell
print(pool.tap_cell(op_a.cell.address))
# {'kind': 'alloc', 'size': 4096, 'priority': 5, 'status': 'queued', 'timestamp': 0}

# Bump priority manually
op_a.bump_priority(8)
print(pool.tap_cell(op_a.cell.address))
# {'kind': 'alloc', 'size': 4096, 'priority': 8, 'status': 'queued', 'timestamp': 0}

# Witness chain
print(f"Witness events: {len(pool.substrate.witness)}")
```

## The honest scope

- **What was ported:** The pool, the priority scheduler, the autoscaler,
  the metrics, the CLI
- **What was preserved:** All upstream code (`src/index.ts`,
  `src/mcpmempool.ts`, `tsconfig.json`, `package.json`)
- **What was added:** The cell-graph projection (this document) + the
  "tappable cell" UI concept
- **What's stubbed:** The tappable UI itself — the data model and
  cells are here; rendering the UI is a separate task
- **What's deferred:** GPU scheduling, Pico port, vectorize
  cross-pollination

## See also

- `UPSTREAM.md` — original repo, faithfully documented
- `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands
- `README.md` (landing page) — dispatches you to the right doc
