# flx-cuda — GPU-accelerated priority scheduler for cell-graph queues

> **flx-cuda** runs the same priority-scheduler pattern as
> [MCPMempool](https://github.com/SuperInstance/MCPMempool-quilt) on the
> GPU. The use case: thousands of pending cell-graph operations where
> the CPU scheduler is the bottleneck.

```c
#include <flx_cuda.cuh>

flx_cuda::FlxScheduler sched;
flx_cuda::flx_scheduler_init(&sched, /*capacity*/ 1024, /*min*/ 0, /*max*/ 9);

flx_cuda::FlxOpCell op = { .id = 1, .priority = 9, .kind = 0, .size = 4096 };
flx_cuda::flx_submit(&sched, &op);

flx_cuda::FlxOpCell out;
flx_cuda::flx_dispatch(&sched, &out);  // returns op with priority=9 (highest)
```

## What it is

A **256-priority-bucket ring buffer scheduler** running on CUDA. Each
priority bucket is a queue on the GPU. Submit appends to a bucket;
dispatch dequeues the highest-priority op across all buckets;
complete marks an op done; drain empties a bucket; tick advances
clock.

| | |
|---|---|
| **Tech** | C++ + CUDA |
| **Build** | CMake 3.13+ + nvcc |
| **License** | MIT |
| **Polyformal ports** | Python (CPU fallback), Rust (in `bindings/rust/`) |
| **Quilt projection** | 5+1 opcodes (BIND/LINK/EFFECT/VIEW/TICK/FORGET) |

## When to use flx-cuda

If you have:
- 1000+ pending ops/sec (MCPMempool, drawing strokes, sensor reads)
- A scheduler that's becoming your bottleneck
- CUDA-capable hardware (Volta or newer recommended)

Then `flx-cuda` is the answer. It runs the same algorithm as the CPU
scheduler but parallelizes the priority scan across GPU warps.

If you don't have CUDA hardware, use the Python CPU fallback. Same
API, same semantics, ~1000x slower but still correct.

## The 5+1 Quilt opcodes — applied to the scheduler

The Quilt projection maps scheduler operations to the canonical opcodes:

| Opcode | Scheduler meaning |
|---|---|
| `BIND` | `flx_scheduler_init` — mount the substrate |
| `LINK` | Typed dependency between priority buckets (e.g., drain-priority-9 ⇒ pause-priority-5) |
| `EFFECT` | submit / dispatch / complete |
| `VIEW` | `flx_queue_counts` — read per-bucket op counts |
| `TICK` | `flx_tick` — advance the clock |
| `FORGET` | `flx_drain` — empty a bucket |

The Python wrapper (`bindings/python/flx_cuda.py`) exposes these as
named methods: `bind()`, `effect_submit()`, `effect_dispatch()`,
`view_counts()`, `tick()`, `forget()`. Each emits a witness event.

## Build

```bash
mkdir build && cd build
cmake ..
make
ctest --output-on-failure
```

Requirements: CUDA toolkit (`nvcc`), CMake 3.13+.

## Polyformal ports

| Port | Status | Path | Tests |
|---|---|---|---|
| **C++ / CUDA** | ✅ reference | `src/flx_cuda.cu` | `tests/test_flx_cuda.cpp` |
| **C++ / CPU** | ✅ reference | `src/flx_cuda_cpu.hpp` | `tests/test_flx_cuda_cpu.cpp` (5/5 ✓) |
| **Python (CPU fallback)** | ✅ reference | `bindings/python/flx_cuda.py` | `bindings/python/tests/test_flx_cuda.py` (4/4 ✓) |
| **Rust** | ✅ reference | `bindings/rust/src/lib.rs` | `bindings/rust/tests/test_flx_cuda.rs` (7/7 ✓) |

Same Quilt semantics across all ports. The cell-graph projection
(`OpCell`, priority buckets, 5+1 opcodes) is invariant.

## Integration with the SuperInstance fleet

- **[MCPMempool](https://github.com/SuperInstance/MCPMempool-quilt)** —
  the upstream TS scheduler this ports from. flx-cuda is the
  GPU-accelerated sibling.
- **[flux-cuda](https://github.com/SuperInstance/flux-cuda)** — the
  bytecode VM (1000 parallel agents). flx-cuda slots into flux-cuda's
  scheduler layer.
- **[cudaclaw](https://github.com/SuperInstance/cudaclaw)** — the
  persistent kernel substrate. flx-cuda kernels follow the same
  warp/block convention (32 threads/block).
- **[eisenstein-cuda](https://github.com/SuperInstance/eisenstein-cuda)** —
  the constraint math kernel. flx-cuda uses Eisenstein priority
  assignments for fairness in mixed-workload schedulers.

## The honest scope

This is a **first-cut production repo**. What works:
- Init / free / submit / dispatch / complete / drain / counts / tick
- Priority buckets from -128 to 127
- Linear-capacity allocation across buckets
- Polyformal C++/CPU, C++/CUDA, Python, and Rust ports
- 16 tests passing across all ports
- Witness chain in every port
- Benchmark suite (see `BENCHMARKS.md`)

What's not here yet:
- Async submit/complete (currently synchronous)
- Multi-GPU dispatch
- Persistent kernel mode (uses launch-per-call currently)
- WASM/WebGPU port for browser

These are tracked in the issue tracker.

See `BENCHMARKS.md` for cross-language performance numbers.

## License

MIT. See [LICENSE](LICENSE).
