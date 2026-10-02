# QUILT — flx-cuda as a cell-graph

`flx-cuda` is the GPU-accelerated sibling of MCPMempool. Both projects
implement the same priority-scheduler pattern, but on different
substrates. This document shows how flx-cuda's CUDA kernels project
onto the Quilt cell-graph.

Audience: GPU systems engineers who know CUDA but may not know Quilt.

## The cell-graph

```
                 ┌───────────────────────────────┐
                 │  cell:scheduler_substrate     │
                 │  name=flx-cuda                │
                 │  axis=role                    │
                 └────────────┬──────────────────┘
                              │ (typed: contains-queue × 256)
                              ▼

   ┌──────────────────────────────────────────────────────────┐
   │  256 PRIORITY QUEUE CELLS                                │
   │  ┌──────────┐  ┌──────────┐       ┌──────────┐           │
   │  │ q[-128]  │  │ q[-127]  │  ...  │ q[127]   │           │
   │  │ ring buf │  │ ring buf │       │ ring buf │           │
   │  │ (capacity│  │ (capacity│       │ (capacity│           │
   │  │  per_pri)│  │  per_pri)│       │  per_pri)│           │
   │  └──────────┘  └──────────┘       └──────────┘           │
   └──────────────────────────────────────────────────────────┘
                              │
                              │ (typed: holds-cells)
                              ▼

   ┌──────────────────────────────────────────────────────────┐
   │  N OP CELLS (per queue)                                 │
   │  ┌──────────┐  ┌──────────┐       ┌──────────┐           │
   │  │OpCell{id}│  │OpCell{id}│  ...  │OpCell{id}│           │
   │  │kind=...  │  │kind=...  │       │kind=...  │           │
   │  │prio=...  │  │prio=...  │       │prio=...  │           │
   │  │size=...  │  │size=...  │       │size=...  │           │
   │  │status=..│  │status=..│       │status=..│           │
   │  └──────────┘  └──────────┘       └──────────┘           │
   └──────────────────────────────────────────────────────────┘
```

**Total cells:** 1 substrate + 256 queues + N ops (variable).
**Total typed links:**
- `substrate → queue` (256× `contains-queue`)
- `queue → op` (N× `holds-cell`)

## The 5+1 opcodes — applied to flx-cuda

| Opcode | C/CUDA call | Quilt semantics |
|---|---|---|
| `BIND` | `flx_scheduler_init(sched, cap, min, max)` | Mount the scheduler substrate; reserve GPU memory for 256 queues |
| `LINK` | (Implicit: queue is contained by substrate, op is contained by queue) | Typed containment edges |
| `EFFECT` | `flx_submit(sched, op)` | Append op cell to its priority bucket |
| `EFFECT` | `flx_dispatch(sched, out)` | Pop the highest-priority op cell across all buckets |
| `EFFECT` | `flx_complete(sched, op_id)` | Mark op cell as done |
| `VIEW` | `flx_queue_counts(sched, out)` | Read per-bucket op counts |
| `TICK` | `flx_tick(sched, dt)` | Advance scheduler clock by `dt` ticks |
| `FORGET` | `flx_drain(sched, priority)` | Empty the priority bucket (remove all ops at that priority) |

## Why CUDA helps here

The CPU scheduler pattern (MCPMempool) scans 256 priority buckets
sequentially. On GPU, you can:

1. **Parallel enqueue** — one block per bucket submits independently.
2. **Parallel dispatch** — one block scans all buckets; the highest
   non-empty bucket wins (with atomic ops for the ring buffer).
3. **Parallel counts** — one thread per bucket, returns 256 counts in
   one kernel launch.

For 10K+ pending ops, this is the difference between "real-time" and
"the scheduler is the bottleneck."

## The polyformalism — same cell-graph, three substrates

| Substrate | Repo | Quilt semantics |
|---|---|---|
| TypeScript / Node | MCPMempool | CPU scheduler; same `OpCell` schema |
| C++ / CUDA | **flx-cuda** (this repo) | GPU scheduler; same `OpCell` schema |
| Rust (planned) | flx-cuda-rs | GPU scheduler; same `OpCell` schema; safe wrappers |

The Python port (`bindings/python/flx_cuda.py`) is a CPU fallback for
machines without CUDA. Same API, same semantics.

## The witness chain

Every CUDA kernel launch is recorded:

```
TICK 0   BIND scheduler (capacity=1024, prios=-128..127)
TICK 1   EFFECT submit op_id=1 priority=5 size=4096
TICK 1   EFFECT submit op_id=2 priority=9 ptr=0x1000
TICK 2   EFFECT submit op_id=3 priority=3 ptr=0x2000
TICK 3   VIEW queue_counts → [0,0,0,1,0,1,0,0,0,1,...]
TICK 4   EFFECT dispatch op_id=2 priority=9
TICK 5   EFFECT complete op_id=2
TICK 5   EFFECT dispatch op_id=1 priority=5
TICK 6   EFFECT complete op_id=1
TICK 6   EFFECT dispatch op_id=3 priority=3
TICK 7   EFFECT complete op_id=3
TICK 8   VIEW queue_counts → [0,0,0,0,0,0,0,0,0,0,...]
TICK 9   FORGET drain priority=5 (0 ops removed)
TICK 10  FORGET drain priority=9 (0 ops removed)
```

This is the audit trail. Every op's lifecycle is observable.

## Code example (Python / CPU fallback)

```python
from flx_cuda import PriorityScheduler, QuiltSchedulerView, OpCell

sched = PriorityScheduler(use_cuda=False)
view = QuiltSchedulerView(sched)

view.bind()
view.effect_submit(OpCell(kind=0, priority=5, size=4096))
view.effect_submit(OpCell(kind=1, priority=9, ptr=0x1000))
view.effect_submit(OpCell(kind=2, priority=3, ptr=0x2000))

print(f"Counts: {view.view_counts()}")
op = view.effect_dispatch()  # returns op with priority=9
view.effect_complete(op.id)
view.tick()
```

## Code example (C++ / CUDA)

```cpp
#include <flx_cuda.cuh>

flx_cuda::FlxScheduler sched;
flx_cuda::flx_scheduler_init(&sched, 1024, 0, 9);

flx_cuda::FlxOpCell op = {
    .id = 1, .kind = 0, .priority = 5, .status = 0,
    .size = 4096, .ptr = 0, .timestamp = 0
};
flx_cuda::flx_submit(&sched, &op);

flx_cuda::FlxOpCell out;
flx_cuda::flx_dispatch(&sched, &out);  // out.priority == 5

flx_cuda::flx_complete(&sched, out.id);
flx_cuda::flx_scheduler_free(&sched);
```

## Integration with the SuperInstance fleet

- **MCPMempool** — the TS scheduler; the upstream cell schema.
- **flux-cuda** — the bytecode VM that flx-cuda's kernel structure
  matches (32 threads/block).
- **cudaclaw** — the persistent kernel pattern; flx-cuda currently
  uses launch-per-call but is designed to migrate.
- **eisenstein-cuda** — the constraint-math kernel for fairness.
- **tile-cuda** — the stack-allocatable cell layout.

## See also

- `UPSTREAM.md` — design lineage
- `PLAIN_LANGUAGE.md` — captains/mechanics version
- `README.md` — landing page
- `tests/test_flx_cuda.cpp` — test suite with Quilt projection invariants
- `bindings/python/flx_cuda.py` — Python port + Quilt view layer
