# Research Summary — CUDA-Q as Quilt Cell Substrate

**Session: 2026-09-14, ~2 hours of scout**
**Doc: /workspace/research/cuda-q-quilt-substrate.md (20KB, 8 sections)**

## Big surprise

**Most of what you'd think you'd need to build already exists:**

| Need | Already exists |
|---|---|
| Plugin substrate | `quilt-cordis` — Cell/Plugin bridge with reversible effects, 33 tests |
| Model router for plugins | `quilt-casting` — Wilson + LinUCB, 48 tests |
| 5-opcode foundation | `quilt-foundation` — 10-round forged |
| GPU mapping of opcodes | `quilt-cuda` — 5+1 opcodes as CUDA ops, 193KB, cudaGraph = compiled cell graph |
| Hardware backend router | `flux-hardware` — CUDA/AVX-512/Fortran/FPGA/eBPF/WebGPU/Vulkan/Coq (CUDA-Q fits as backend #9) |
| Persistent agent kernel | `cudaclaw` — SPSC queue, SmartCRDT, CellAgent + MuscleFiber |
| Diffusion on graphs | `si-conservation-diffusion`, `sheaf-dynamics`, `plato-diffusion` |
| Polyformalism experiment | `polyformalism` — 13 languages, 2100 test vectors |

**What's MISSING:**

1. `EXTEND` opcode (mounting plugins via the VM, not via Python lifecycle)
2. `ENTANGLE` primitive (no quantum correlation between cells today)
3. `MEASURE` opcode (VIEW is pure; quantum needs collapse-on-read)
4. `GENERATE` opcode (cell-graph diffusion; classical denoiser, quantum sampler)
5. CUDA-Q / quantum-hybrid repo (no `quilt-quantum` yet — pure greenfield)
6. The 4 new laws as device-side prover kernel

## The 4-opcode plugin spec (drafted in §3 of the doc)

```python
EXTEND(name, substrate, semantics) -> Cell              # Reversible w/ FORGET
ENTANGLE(a, b, basis) -> Cell                             # bell/ghz/w/cluster
MEASURE(cell, basis) -> value                            # Z/X/Y/Bell
GENERATE(prompt, scope, steps) -> List[Cell]             # stable-diffusion-of-cells
```

Plus 4 new laws preserving the 5+1+1+1+1 algebraic structure:
- EXTEND-LAW (mount/unmount invertibility)
- ENTANGLE-NONCLONING (no-cloning as substrate safety)
- MEASURE-PROJECTION (idempotent collapse)
- GENERATE-CONSERVATION (Σ confidence children = parent pre-diffusion)

## JEPA per cell + stable-diffusion-of-cells

Each cell becomes a local JEPA predictor (predict embeddings not pixels).
LINK between cells is learned similarity, not a fixed type. CUDA-Q gives
**superposition over plausible predictions** — the cell holds
|pred_1, pred_2, ..., pred_N⟩ which collapses on MEASURE.

The pipeline: PROMPT cell → NOISE cells (uniform superposition over scope)
→ K classical denoise + quantum projection steps → K high-confidence
output cells. **Diffusion runs over the cell graph, not a pixel grid.**

## Production vs porting seam (§2.6 of doc)

You explicitly named both:
- **PRODUCTION layer**: user-facing — GENERATE, EXTEND(name, semantics)
- **PORTING layer**: substrate-facing — ENTANGLE, MEASURE, EXTEND(name, hw)

The `quilt-cordis` bridge is what holds them together: a CUDA-Q kernel
is just another Cordis plugin with `effect_quantum(fn, inverse)`.

## What I need from you (6 questions in §7 of doc)

1. **GENERATE output type** — classical cells (quantum sampler draws latent) or quantum cells (real superposition until MEASURE)? **My rec:** classical default, `keep_quantum=True` opt-in.
2. **4-opcode spec signoff** — or split EXTEND into EXTEND-MOUNT + EXTEND-FORK?
3. **4 new laws signoff** — esp. GENERATE-CONSERVATION: confidence sums to parent's pre-diffusion value, or to 1.0?
4. **CUDA-Q toolkit** — what hardware? CPU sim, GPU, real QPU?
5. **Repo naming** — `quilt-quantum` or `quilt-cuda-q`?
6. **Priority** — start `quilt-quantum` skeleton now (Phase 2 → Phase 3) or more scout first?

## Cost

~9-11 sessions for working slice:
- Spec ratification: 1 (this doc + your signoff)
- `quilt-quantum` skeleton: 2-3
- `quilt-cuda` substrate flag: 1
- `quilt-cordis` quantum adapter: 1
- First diffusion demo (8-cell scope, 4 steps): 2-3
- Hardware run: 1-2

## Open question I should ask now

**The user vision was:** *"CUDA-Q for not just in-cell widgets but for high-level production of novel quilt designs and low-level handling of porting and entangling."*

This maps cleanly onto the PRODUCTION/PORTING split I drafted. **But** — do you want CUDA-Q to be **the** substrate (every cell is quantum by default), or **a** substrate (a backend in `flux-hardware` you opt into per cell)? My rec: **a substrate**, opt-in. Quantum overhead is real; classical cells stay cheap.

**Next move I recommend:** answer the 6 questions in §7 of the doc, then I start `quilt-quantum` skeleton in the next session. If you want to move faster, answer even just #1 + #5 + #6 and I can start the header files today.

---

Full doc: `/workspace/research/cuda-q-quilt-substrate.md`
