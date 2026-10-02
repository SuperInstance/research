# UPSTREAM — flx-cuda's design lineage

`flx-cuda` is built from scratch; there is no upstream fork. This
document instead traces **the design lineage** — which existing repos
inspired flx-cuda's architecture, and why.

## Design lineage

| Ancestor | What it gave flx-cuda |
|---|---|
| **[MCPMempool](https://github.com/SuperInstance/MCPMempool-quilt)** | The cell schema (`OpCell` with kind/priority/status/timestamp). The 256-priority bucket concept. The submit/dispatch/complete/drain semantics. The polyformal projection idea. |
| **[flux-cuda](https://github.com/SuperInstance/flux-cuda)** | The 32-thread warp / 1-block convention. The `cudaMalloc` / `cudaMemcpy` patterns. The CUDA toolkit setup. |
| **[cudaclaw](https://github.com/SuperInstance/cudaclaw)** | The persistent-kernel substrate pattern. The witness-event log shape. |
| **[eisenstein-cuda](https://github.com/SuperInstance/eisenstein-cuda)** | The constraint-math approach to priority assignment for fairness. |
| **[tile-cuda](https://github.com/SuperInstance/tile-cuda)** | The stack-allocatable cell layout pattern (`alignas(16)` on `FlxOpCell`). |

## What flx-cuda is NOT a fork of

It is a **greenfield GPU scheduler** for the cell-graph pattern. There
is no upstream "flx-cuda" repository anywhere. The repo name was
invented as a sibling to flux-cuda, with the prefix `flx-` chosen to
match the existing SuperInstance naming convention for short project
names.

## What flx-cuda is FORKED from (nothing)

`flx-cuda` does not import, fork, or copy code from any other
repository. Every line in `src/flx_cuda.cu`, `src/flx_cuda.cuh`, and
`tests/test_flx_cuda.cpp` was written fresh for this project, drawing
on the architectural patterns of the repos listed above.

## What you can do with this lineage

- Use MCPMempool's cell schema documentation as a reference for
  `OpCell` semantics.
- Use flux-cuda's build system (CMake + nvcc) as a template.
- Use cudaclaw's witness log format for tracing.
- Use eisenstein-cuda's constraint math for fairness.

These are all **MIT licensed**. flx-cuda is **also MIT licensed**,
matching the convention.

## Notes on the commit history

The initial commit contains:
- `src/flx_cuda.cuh` (the C++ header)
- `src/flx_cuda.cu` (the CUDA implementation)
- `tests/test_flx_cuda.cpp` (the test suite)
- `bindings/python/flx_cuda.py` (Python CPU fallback + Quilt projection)
- `CMakeLists.txt` (build configuration)
- `README.md`, `LICENSE`, `docs/UPSTREAM.md`, `docs/QUILT.md`, `docs/PLAIN_LANGUAGE.md`

## License

MIT, matching the SuperInstance convention.
