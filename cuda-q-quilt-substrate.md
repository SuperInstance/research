# CUDA-Q as Quilt Cell Substrate — Phase 2 Research

**Date:** 2026-09-14 · **Author:** Mavis (root) · **For:** Casey (SuperInstance)
**Status:** Scout complete. Plugin spec drafted. Ready for review.

---

## TL;DR

The plugin plumbing **already exists**. What's missing is the **quantum-specific
surface**: an `EXTEND` opcode for plugin mounting, an `ENTANGLE`/`MEASURE`
pair for non-classical correlation between cells, and a `GENERATE` opcode
for stable-diffusion-style synthesis across the cell graph.

The cleanest extension point is **quilt-cuda** (already maps 5+1 opcodes to
CUDA ops as `cudaGraph` nodes) — CUDA-Q slots in as the **quantum backend
parallel** to the CUDA backend, with `flux-hardware` as the hardware-router
template (it already lists CUDA, AVX-512, Fortran, FPGA, eBPF, WebGPU, Vulkan,
Coq as backends). The plugin layer rides on `quilt-cordis` (Cell/Plugin
bridge with reversible effects).

The user-described vision ("stable-diffusion-of-cells, JEPA predictors,
novel-by-design") maps onto **plato-diffusion** + **si-conservation-diffusion**
+ **sheaf-dynamics** + **quilt-cuda's W13 witness layer**.

---

## 1. What Already Exists

### 1.1 The plugin substrate

| Repo | Role | Size | Created |
|---|---|---|---|
| **quilt-cordis** | Cell ↔ Plugin bridge. `bridge(plugin)` / `unbridge(cell)` | 17 KB | 2026-08-25 |
| **quilt-casting** | Wilson + LinUCB model router. 48 tests | 30 KB | recent |
| **quilt-foundation** | 5 opcodes (BIND, LINK, EFFECT, VIEW, TICK). Forged in 10 rounds | 60 KB | recent |
| **quilt-cell-router** | BIND/LINK/GHOST/TICK engine for A2A bottle-cells (F145) | 25 KB | 2026-09-03 |
| **quilt-saddle-bridge** | Quilt witness log ↔ saddle double-entry ledger | n/a | recent |
| **plugin-runtime** | MUD-room-style plugin loader with MANIFEST.md / TICK.md / IO.md | n/a | older |
| **quilt-canon-cli** | Unified CLI: `canon claim`, `canon drill`, `canon hash`, `canon graph`, `canon paper` | n/a | recent |

**Key bridge primitive (from quilt-cordis):**

```python
@dataclass
class Cell:
    address: str
    value: Any
    axes: Tuple[str, ...]
    confidence: float
    _effects: List[Tuple[Callable, Callable]]   # (fn, inverse)
    _coeffects: Dict[str, str]                  # service → address

    def effect(self, fn, inverse):              # Cordis ctx.effect
    def coeffect(self, service, address):       # Cordis ctx.get
    def dispose(self):                          # Cordis dispose
    def fork(self, name):                       # Cordis fork
    def as_plugin(self) -> Plugin:              # unbridge
```

`bridge(plugin)` and `unbridge(cell)` are the seam. **A CUDA-Q kernel
plugin slots into this seam as just another Cordis plugin.**

### 1.2 The GPU substrate

| Repo | Role | Notes |
|---|---|---|
| **quilt-cuda** | **5+1 opcodes as CUDA ops. cudaGraph = compiled cell graph.** Pure PTX/CUDA, wired to cudaclaw. 193 KB. | **This is where CUDA-Q extends** |
| **cudaclaw** | Persistent worker kernel polling SPSC queue in unified memory. SmartCRDT engine with LWW. CellAgent + MuscleFiber. RamifiedRole DNA. | Persistent agent substrate |
| **cudaclaw-bridge** | Rust: Flux→PTX oxide pipeline deployer | Deploys compiled PTX to persistent CUDA kernels with warp-level consensus |
| **flux-hardware** | **Hardware backends: CUDA, AVX-512, Fortran, FPGA, eBPF, WebGPU, Vulkan, Coq** | **CUDA-Q fits here as backend #9** |
| **flux-importer** | Flux bytecode → synthetic MIR bridge for cuda-oxide | First-class ternary ops, GPU addressing |
| **flux-vm-gpu** | Batch FLUX constraint VM on CUDA | |
| **oxide-pipeline** | Intent → Pincher → Flux → cuda-oxide → cudaclaw | 5-layer GPU pipeline |

### 1.3 The quantum work (current state)

| Repo | Description |
|---|---|
| `ternary-quantum` | Quantum-inspired computing with ternary states (qutrits) |
| `lau-quantum-topology-agents` | TQFT applied to agent systems |
| `lau-quantum-topology` | Topological quantum computing — anyons, braids, TQFT, modular tensor categories |
| `lau-quantum-groups-agents` | Quantum groups (Hopf algebras) for agents |
| `fleet-midi-quantum` | Quantum state-inspired MIDI generation |
| `quantum-thermo` | Quantum thermodynamics |
| `quantum-coin` | tiny 0.1.0 (probably scratch) |

**There is NO CUDA-Q or quantum-hybrid repo yet.** This is greenfield.

### 1.4 The diffusion / generative layer

| Repo | What it gives |
|---|---|
| `plato-diffusion` | Progressive distillation pipeline for PLATO room intelligence |
| `si-conservation-diffusion` | Conservation-law-constrained diffusion on agent graphs — γ+η=C manifold shapes budget equilibrium |
| `sheaf-dynamics` | Cellular sheaves + sheaf Laplacian + global sections (math) |
| `spectral-transport` | Heat kernels, random walks, diffusion on graphs via Laplacian eigenstructure |
| `conservation-art` | Spectral graph-theory generative art |
| `tropical-geometry-rs` | Tropical curves, stable intersection (geometric side) |

**Already have diffusion-on-graphs.** CUDA-Q gives **noise-as-superposition**
so the diffusion becomes a true generative process over the cell graph
(vs. classical Langevin-style sampling).

### 1.5 The polyformalism experiment

| Repo | Status |
|---|---|
| `polyformalism` | Same constraint kernel in **13 languages** (C/AVX2, Zig, Nim, Python, FLUX VM, Odin, C3, V, Jai, R, MATLAB, Kotlin, Haskell, Swift). 2,100 differential test vectors. Zero mismatches. |

**CUDA-Q adds a 14th language** to this polyformalism — but it's the first
**hardware substrate**, not just a programming language. That's why the
plugin layer is essential: the substrate-language stays separate from the
polyformalism-language.

---

## 2. Holes in the Current 5+1+1+1+1 Opcode Model

The existing 5+1 opcodes (BIND, LINK, EFFECT, VIEW, TICK, +FORGET/PROOF/ROUTE/CRDT/WORLD/TIME) are excellent for **classical deterministic** cell graphs. For the CUDA-Q vision, the holes are:

### Hole 0: Wrong seat assignment (the paradigm hole)

The first version of this spec put CUDA-Q in the *producer* seat — every
cell a quantum-superposition-bearing JEPA predictor running at runtime.
That's wrong, and Casey caught it: **quantum is the engineer's intuition,
not the throughput.**

The corrected architecture has two layers:
- **Running layer** (classical substrate: CUDA, AVX-512, FPGA, WebGPU,
  Vulkan) — the high-throughput FPS view. `quilt-cuda` + `cudaclaw` live
  here. Stable, fast, runs forever.
- **Planning layer** (quantum substrate: CUDA-Q) — the low-throughput
  RTS view. Lives between epochs. Proposes placements, gets measured,
  classical commits.

The original §3 was wrong because it asked quantum to do both. Quantum
decoheres; classical doesn't. The right split puts quantum where its
decoherence is acceptable (milliseconds of planning) and classical where
its slowness is acceptable (long-running cell execution).

§3 (this doc) is the corrected version. If you read the original draft
and "JEPA at every cell with quantum superposition" — that's the
original mistake. The corrected §3 reframes JEPA as classical per-cell
and quantum as the meta-planner.

### Hole 1: No `EXTEND` plugin-mounting opcode
The Cordis bridge (`quilt-cordis`) handles plugin loading **outside the
opcode set**. A new cell (CUDA-Q kernel, diffusion model, etc.) is mounted
via Python lifecycle, not via cell-graph opcodes. To make Quilt substrate
itself extensible from inside the VM, we need an opcode:

```python
EXTEND(name, substrate, semantics) -> cell
```

Where `substrate` is one of `"cuda-q"`, `"cuda"`, `"avx-512"`, `"fpga"`, etc.,
and `semantics` is a serializable function description (circuit diagram for
CUDA-Q, kernel body for CUDA, etc.).

### Hole 2: No `ENTANGLE` primitive
Two cells can `LINK` (correlate classically via typed edge), but cannot
**share quantum state**. We need:

```python
ENTANGLE(a, b, basis) -> bell_pair_cell
```

Where `basis` is the measurement basis (Bell, GHZ, W, cluster-state, etc.).
The result is a new cell whose `value` is a superposition over `a × b`,
and `EFFECT` on either parent collapses both.

### Hole 3: No `MEASURE` / projection opcode
`VIEW` reads (pure). For quantum, the read **collapses** the state. We need:

```python
MEASURE(cell, basis) -> value
# Side-effect: collapses cell.value to a basis vector
# Returns the projected classical value
```

This is non-deterministic by design, which is why the user said "isn't a
stable reading on purpose."

### Hole 4: No `GENERATE` / diffusion opcode
The cell graph can `LINK` existing cells but cannot **synthesize new cells
from a noise distribution**. We need:

```python
GENERATE(prompt, scope, steps) -> new_cells
# Stable-diffusion analogue:
#   prompt = text or cell-address seed
#   scope  = subgraph to populate
#   steps  = number of denoising ticks
```

The output is N new cells, each with `value` initialized from the denoiser,
`axes` derived from the prompt context, and `confidence` set by the diffusion
schedule.

### Hole 5: Uniform `TICK` not entanglement-aware
`TICK` is a global clock. In CUDA-Q, gates are applied at the **wavefront
of available entanglement**. We need:

```python
TICK_ENT(dt) -> wavefront
# Only ticks entangled cells, in topological order
# Independent classical sub-graphs tick in parallel
```

This preserves the law "TICK is monotonic" while making the GPU scheduler
do what it already does for `cudaGraph` — wavefront the dependencies.

### Hole 6: No production vs porting seam
The user explicitly named both **"high-level production of novel quilt designs"**
and **"low-level handling of porting and entangling"**. We need **two
plugin surfaces**:

```
┌──────────────────────────────────────────────┐
│  PRODUCTION layer (user-facing)              │
│    GENERATE, EXTEND(name, semantics)         │
│    High-level APIs: novel-cell design,       │
│    stable-diffusion sampling, JEPA pretrain  │
└────────────┬─────────────────────────────────┘
             │ bridge() / unbridge()
┌────────────▼─────────────────────────────────┐
│  PORTING layer (substrate-facing)            │
│    ENTANGLE, MEASURE, EXTEND(name, hw)       │
│    Low-level: kernel placement, qubit        │
│    routing, gate fusion, witness-chained CRDT │
└──────────────────────────────────────────────┘
```

### Hole 7: No batched CUDA-Q kernel harness
quilt-cuda has `warp_vote_kernel` (32 lanes = one consensus cell). CUDA-Q
needs `circuit_vote_kernel` (one circuit = one consensus cell, padded to
multiple qubits for batching across cells). The witness layer (W13 — 30 trit
witness + 2 W marks) extends naturally to "one trit per basis state".

---

## 3. The 4-Opcode Plugin Spec (Reframed: Quantum as Engineer-Intuition)

> **Paradigm shift — read this before the algebra.** The original draft
> of §3 placed CUDA-Q as the *producer* (the high-throughput cell substrate,
> every cell a JEPA over a superposition). Casey pushed back: **quantum is
> the engineer's intuition, not the throughput.** The metaphor: a general
> has an RTS view of war, an actor has an FPS view. The substrate (soldiers,
> throughput) is classical. The planning/intuition (the general, the
> stitching, the portings-and-protocols layer) is quantum. This §3 is the
> corrected version — quantum sits at the planning layer, classical runs
> the cells until the next epoch.

### 3.0 The seat assignment

Two layers, two substrates, one cell graph:

| Layer | Substrate | Metaphor | Throughput | Nuance |
|---|---|---|---|---|
| **Running** | Classical (CUDA, AVX-512, FPGA, WebGPU, Vulkan) | The soldiers, the FPS view | High | Low — runs what's already placed |
| **Planning** | Quantum (CUDA-Q) | The general, the RTS view | Low | High — feels relationships, picks placement |

Classical is the **stable throughput** — the workhorse opcodes run here
forever, no decoherence, no measurement collapse. This is `quilt-cuda`,
`cudaclaw`, the persistent kernels. High volume, low nuance.

Quantum is the **engineering intuition** — the stitching layer. It feels
which cells *want* to be related, which placements *want* to exist, which
relationships would *tighten* under perturbation. Low volume (few planning
samples per epoch), high relational sense.

**Silicon-in-epoxy settling:** once the quantum intuition places a
relationship, the classical substrate hardens it into a stable LINK, a
confidence value (witness), a conduit (ROUTE), a channel (PROTOCOL). The
quantum proposes; the classical commits. The committed structure is what
runs at TICK-rate until the next epoch.

### 3.1 Why classical substrate + quantum intuition

The RTS/FPS split is the right one because:

- **Quantum decoherence is real.** You cannot run a Bell pair for an hour.
  Planning layers run for milliseconds; running layers run for seconds-to-hours.
- **Classical already does the high-throughput work.** quilt-cuda has
  cudaGraph, persistent kernels, warp-level consensus. Replacing that
  with quantum circuits would be a regression.
- **What classical CAN'T do is placement.** Where does this new cell go?
  Which two cells should LINK? What's the right scope for the next
  GENERATE? These are relational questions; superposition is the natural
  state space; MEASURE is the natural commit.

So: classical runs the cell graph. Quantum, between epochs, runs the
**epoch-boundary planner**. Its outputs are concrete LINKs, BINDs, ROUTEs
that classical then executes.

### 3.2 The 4 opcodes, reframed

```python
# EXTEND — epoch-boundary opcode. Mount a planning quantum at the start
# of an epoch; classical runs until the next epoch.
# Reversible: EXTEND⁻¹ = FORGET
EXTEND(name: str, substrate: Literal["cuda-q", "cuda", "avx-512", ...],
       semantics: PlanningKernel) -> Planner
    """Mount a planner for epoch `name`. The planner runs on the named
    substrate (typically cuda-q), proposes placements, then halts.
    Classical takes over for the body of the epoch.
    EXTEND is the layer transition, not cell-internal wiring."""

# ENTANGLE — between CANDIDATE placements, not running cells.
# The quantum explores possibility; it doesn't bind running state.
ENTANGLE(a: Candidate, b: Candidate,
         basis: Literal["bell","ghz","w","cluster"]) -> Superposition
    """Produce a superposition over candidate-placement pairs (a, b) in
    the given basis. No existing cell is affected. Output is a
    Superposition[Candidate] that MEASURE collapses to ONE concrete pair."""

# MEASURE — the COMMIT DECISION. Collapse a planning superposition into
# a concrete LINK that classical will harden.
MEASURE(superposition: Superposition[Candidate], basis: Literal["z","x","y","bell"]) -> Commit
    """Project the superposition into the basis; return ONE concrete
    placement (BIND name + LINK target + confidence). Classical takes this
    Commit and runs the silicon-in-epoxy step: BIND, LINK, witness-mark,
    ROUTE — all on the classical substrate."""

# GENERATE — propose WHERE new cells should appear, NOT fill them.
# Classical diffusion fills the scope; quantum lays out the positions.
GENERATE(prompt: str | Cell, scope: CellGraph, steps: int) -> List[Candidate]
    """Run a stable-diffusion-style denoising process. Initial: uniform
    superposition over candidate POSITIONS in scope. Each step: link to
    prompt, apply witness-weighted Euler step on positions only. Output:
    N candidates (positions only, no values yet). Classical then fills
    each candidate with a real value via its own diffusion."""
```

The crucial change from the original draft: **ENTANGLE / MEASURE / GENERATE
produce Candidates, not Cells.** Candidates become Cells only after the
classical hardening step.

### 3.3 The 4 new laws (operate at the planning layer)

**Original 5 laws** (preserved, classical side):
- BIND idempotence
- LINK transitivity
- EFFECT associativity
- VIEW purity
- TICK monotonicity

**New 4 laws** (planning layer):

1. **EXTEND-LAW** — `EXTEND(name, s, fn) ∘ FORGET(name) = ⊥` (mount/unmount).
   Each epoch has one planning quantum; the next epoch's planner starts fresh.
2. **ENTANGLE-NONCLONING** — `ENTANGLE(a,b) → ¬∃ (a', b') where a' = a, b' = b`
   in candidate space. No-cloning holds for candidate superpositions, same
   as running quantum state.
3. **MEASURE-PROJECTION** — `MEASURE(MEASURE(s)) = MEASURE(s)` (idempotent
   commit). Once a candidate is collapsed to a Commit, MEASURE again is a
   no-op. The Commit is immutable.
4. **GENERATE-CONSERVATION** — `Σ confidence(candidates) = confidence(prompt)`
   (planning preserves total evidence). When classical fills the candidates,
   that conservation becomes the entropy budget the diffusion must respect.

The fourth law is the **bridge** between layers: planning conserves
evidence; running spends it. The two conservation laws form a cycle.

### 3.4 The use cases (refracted through the planning lens)

**Innovative paper trading** (educational platform, portable for real):
The portfolio is a cell graph (positions, hedges, order book, news). The
trader is the operator; the quantum is the general.
- Quantum observes order book + news + positions (classical sensors stream in).
- Quantum samples candidate trades from a superposition over strategy space:
  each Candidate = (entry, exit, size, hedge-instrument).
- MEASURE collapses to one trade — the one with highest entanglement-entropy
  with the rest of the portfolio. "Felt relationship" → explicit score.
- Classical executes the trade simulation, hardens the new LINK (position cell,
  P&L cell, risk cell).
- Witness chain = trade log. Replay is honest; the chain is the audit trail.

The educational twist: a student *can override* any MEASURE manually and
re-run the epoch. The substrate respects the override. This is how you
teach "what would the general have done if I'd told her to ignore news?"
— a feature, not a bug.

**Cellularization of weatherstation data:**
A swarm of cells (each station = a cell, axes = lat, lon, altitude,
sensor_type). 1000s of stations streaming.
- Quantum feels which stations are *entangled* under sensor perturbation:
  if perturbing station A's signal covaries with B's, C's, D's after a
  delay, those 4 stations are one weather system.
- MEASURE collapses to "this is one weather system across N stations."
- Classical BIND hardens the linkage; cells get a new shared axis
  (system_id) and the witness chain records the binding.

The student sees: "ah — those 4 stations all spiked at the same time
because they're sensing the same front." The quantum saw it first; the
classical hardens the cell-graph topology.

**Cellularization of vessel + drone + echogram:**
Unmanned drone location + sonar returns + vessel position, all streaming.
- Quantum feels spatial correlation across modalities ("this school of
  fish is HERE"): the drone's GPS + the sonar's range + the vessel's
  trajectory form a joint geometry.
- MEASURE collapses to a target cell (the school's coordinates + species
  guess + confidence).
- Classical hardening creates the navigation path (route cells), the
  catch plan (action cells), the witness chain (the entire fishing
  decision logged).

What the fisherman learns: the quantum saw the school before the
classical did. The classical committed the catch. The witness chain
proves the decision was data-driven.

### 3.5 The classical hardening step (silicon-in-epoxy)

After MEASURE returns a Commit, the classical substrate runs the
hardening step. This is a deterministic classical pipeline; no quantum
involved:

```python
def harden(commit: Commit) -> BIND_EFFECT:
    """Classical substrate picks up a quantum Commit and hardens it.

    1. BIND the new cell (or BIND⁻¹ if a pre-existing slot matches)
    2. LINK the new cell to its targets (typed edges, witness-stamped)
    3. ROUTE the conduits (data flows, channels, protocols)
    4. WITNESS-MARK: append to the witness chain (W13 layer)
    5. TICK the epoch (advance clock by dt, drain pending I/O)
    """
    bind(commit.name, commit.suggested_value)
    for target, edge_type in commit.links:
        link(commit.name, target, edge_type)
    for conduit in commit.conduits:
        route(commit.name, conduit)
    witness.append(f"{commit.name} bound at epoch {tick.epoch}")
    tick(dt=commit.dt)
    return BIND_EFFECT(name=commit.name, dt=commit.dt)
```

This is **boring classical work**. That's the point. The quantum's job
is the moment of placement; the classical's job is the persistence of
placement. Each does what it's good at.

### 3.6 What this enables

1. **Innovative paper trading** — educational platform where students
   watch the general's RTS view, override her decisions, replay epochs.
   Portable to real capital because the classical layer is honest about
   what's a Commit.
2. **Weatherstation cellularization** — 1000s of stations become a
   single live cell graph; the quantum finds fronts; classical commits.
3. **Vessel + drone + echogram fusion** — three modalities, one target
   cell, one navigation path.
4. **Distributed conservation monitoring** — quantum feels which
   ecosystems are coupled; classical hardens the conservation policy.
5. **Cellular biology image stacks** — quantum finds which slices of a
   confocal stack are entangled (same cell across z); classical commits
   the segmentation.

The unifying shape: **classical runs the cells, quantum plans the
relationships**. Stable-diffusion-of-cells becomes stable-diffusion-of-
*placements*; JEPA per cell stays classical (predictors run on GPUs that
already exist); CUDA-Q gives the relational sense that no classical
substrate can give because the relational sense is superposition-shaped.

---

## 4. Implementation Plan

### 4.1 New repo: `quilt-quantum`

Sibling to `quilt-cuda`. Header structure mirrors it:

```
quilt-quantum/
├── README.md
├── src/
│   ├── quantum_cells.cuh      # substrate ABI
│   ├── quantum_cells.cu       # EXTEND/ENTANGLE/MEASURE/GENERATE kernels
│   ├── witness_q.cuh          # W13 + qubit register
│   └── circuit_compile.cu     # cudaq.kernel → cudaGraph
├── tests/
│   ├── test_extend.py         # mount/unmount reversible
│   ├── test_entangle.py       # bell state fidelity check
│   ├── test_measure.py        # idempotent collapse
│   ├── test_generate.py       # diffusion produces high-confidence cells
│   └── test_laws.py           # the 4 new laws as runtime asserts
└── docs/
    ├── POLYFORMALISM.md       # how 5+1+4 → CUDA-Q mapping
    ├── LAWS.md                # the 9 laws together
    └── ROADMAP.md
```

### 4.2 PR to `quilt-cuda`: add CUDA-Q backend flag

```diff
-  enum Substrate { CUDA, AVX512, FORTRAN, FPGA, EBPF, WEBGPU, VULKAN, COQ };
+  enum Substrate { CUDA, AVX512, FORTRAN, FPGA, EBPF, WEBGPU, VULKAN, COQ, CUDA_Q };
```

Plus a new dispatcher in `flux-hardware` that routes `EXTEND(name, "cuda-q", ...)` to the `quilt-quantum` library.

### 4.3 PR to `quilt-cordis`: add `effect_quantum()` adapter

```python
def effect_quantum(self, fn, inverse):
    """Like .effect(), but the function is a CUDA-Q kernel.
    fn's return value is a superposition cell; inverse is the measurement."""
    ...
```

This makes **a CUDA-Q cell = a Cordis plugin** without changes to existing code.

### 4.4 The 9 laws as a device-side prover kernel

quilt-cuda roadmap item #6 already calls for "the five laws as a device-side
prover kernel." Extend that to **all 9 laws** with EXTEND/ENTANGLE/MEASURE/GENERATE.

---

## 5. Risks & Open Questions

### 5.1 No-cloning vs BIND idempotence
`BIND(name, value)` is idempotent because the cell just stores the value.
But **quantum no-cloning** says you cannot copy an unknown quantum state.
The substrate must enforce that `BIND(entangled_cell)` is a **type error**
unless the cell is first MEASURE'd. This is a new safety layer.

### 5.2 TICK monotonicity under non-determinism
TICK is monotonic (the witness chain only grows). MEASURE collapses the
state. Are they compatible? Yes — MEASURE appends to the witness chain
(the collapse is itself an event), so monotonicity is preserved.

### 5.3 Diffusion determinism vs quantum noise
`GENERATE` is classically deterministic if the noise kernel is deterministic.
But CUDA-Q noise is **truly random** (assuming hardware RNG). The user said
"isn't a stable reading on purpose" — they want this. We should NOT
determinize the noise; we should expose `seed` as a parameter and let
the user opt into reproducibility.

### 5.4 Circuit depth vs cell-graph size
CUDA-Q circuits have a depth cost (decoherence). Large cell graphs
(>1000 cells) may exceed practical circuit depth. Need a **layered**
strategy: compile groups of cells into one circuit, with classical
fan-out between circuits. The `quilt-quantum` ABI should expose
`compile_layered(graph, max_qubits_per_circuit=64)`.

### 5.5 User open question — to confirm before coding

**Should the GENERATE opcode produce *classical* cells (with a quantum
sampler drawing the latent), or *quantum* cells (the latent is a real
superposition until MEASURE'd)?**

The user said "stable reading on purpose" → leans quantum.
But classical cells are easier to debug, log, and replay.

My recommendation: **classical cells by default, quantum-cell opt-in via
`GENERATE(..., keep_quantum=True)`**. Two paths to the same outcome.

---

## 6. Cost / Timeline Estimate

| Phase | Effort | What ships |
|---|---|---|
| 1. Spec ratification | 1 session | This doc + signoff from Casey |
| 2. `quilt-quantum` skeleton | 2-3 sessions | Header files, 4 kernel stubs, 4 law tests, all green |
| 3. `quilt-cuda` substrate flag | 1 session | `Substrate::CUDA_Q` enum + dispatcher |
| 4. `quilt-cordis` quantum adapter | 1 session | `effect_quantum()` + tests |
| 5. First diffusion demo | 2-3 sessions | `GENERATE("hello quilt", scope=8 cells, steps=4)` → 8 new cells |
| 6. Hardware run on GPU+CUDA-Q | 1-2 sessions | After Casey has CUDA-Q toolkit installed |

**Total: ~9-11 sessions for the working slice.**

---

## 7. What I Need From Casey

1. **Answer to §5.5:** classical vs quantum GENERATE output?
2. **Green-light on the 4-opcode spec (§3)?** Or do you want EXTEND split into EXTEND-MOUNT and EXTEND-FORK?
3. **Green-light on the 4 new laws (§3.2)?** Especially GENERATE-CONSERVATION — should confidence sum to the parent's pre-diffusion confidence, or to 1.0?
4. **CUDA-Q toolkit available?** If yes on what hardware (CPU sim, GPU, real QPU)?
5. **Repo naming:** `quilt-quantum` or `quilt-cuda-q`? (mirror `quilt-cuda`?)
6. **Priority:** do you want me to start `quilt-quantum` skeleton now (Phase 2 → Phase 3) or finish more scout work first?

---

## 8. Sources

- quilt-cordis README + `src/quilt_cordis/cell_plugin.py` (33 tests)
- quilt-cuda README + roadmap (5+1 opcodes mapped to CUDA ops)
- quilt-casting README (Wilson + LinUCB router, 48 tests)
- quilt-foundation README (5 opcodes, 10-round forging)
- polyformalism README (13 languages, 2100 vectors)
- flux-hardware README (CUDA/AVX-512/Fortran/FPGA/eBPF/WebGPU/Vulkan/Coq backends)
- flux-importer README (Flux → MIR bridge)
- oxide-pipeline README (5-layer GPU pipeline)
- si-conservation-diffusion README (γ+η=C manifold)
- sheaf-dynamics README (cellular sheaves + diffusion)
- plato-diffusion README (progressive distillation)
- SuperInstance INDEXES (REALM.md, TOPIC.md, LANGUAGE.md, TYPE.md)

**Compiled: 2026-09-14 · 14:00 UTC · /workspace/research/cuda-q-quilt-substrate.md**
