# QUILT_NOTES — how the QUILT mode maps to the Quilt canon

## TL;DR

The QUILT mode in twist-engine is a **physics-form substrate** of the
Quilt canon. Same math, different language. Where the canon talks about
witnesses and merkle chains, twist-engine talks about phase oscillators
and co-fire graphs. Both count the holes.

## Side-by-side

| Concept              | Quilt canon                          | twist-engine QUILT mode       |
|----------------------|--------------------------------------|-------------------------------|
| Basic unit           | Cell (BIND/LINK/EFFECT/VIEW/TICK)     | Phase oscillator (Kuramoto)   |
| Address              | `sha256(scope::name)[:16]`            | `(x, y)` grid coordinate      |
| Sub-lattice split    | Even/odd parity in the address?       | `(x + y) % 2 == 0`            |
| Tempo offset         | Witness log tick rate                | `δ` (delta) parameter         |
| Natural frequency    | Block time / round-robin slot         | `ω = ω₀` (and `ω₀(1+δ)`)      |
| Coupling             | LINK between cells                    | `K * sin(φⱼ − φᵢ)`           |
| Snap event           | EFFECT / TICK / state change          | `phi[i] >= TAU` (cycle done)  |
| Witness              | Witness log entry                     | "fired[i] = t" timestamp      |
| Recency window       | Witness retention policy              | `Wc = 1.2 seconds`            |
| Graph                | Citation graph / LINK graph           | Co-fire graph                 |
| Connected components | Fleet (workspace federation)          | Union-find roots              |
| **Holes (b1)**       | **Circuit rank of the canon graph**   | **b1 = E − V + C**            |
| Ledger               | Canon `state_hash`                    | `b1` chart on the rail        |

## The substrate is the same theorem

In the canon, a cell writes a witness when its state changes. Witnesses
form a merkle chain. Citations between cells form a graph. The graph
has a topology — and that topology has *holes*.

In twist-engine, an oscillator snaps when its phase completes a cycle.
Recently-snapped oscillators form a graph. Union-find gives the
components. The circuit rank gives the holes.

**The math is identical.** What differs is the vocabulary.

## Why a tempo twist

The canon's substrate is *asynchronous*: witnesses fire whenever they
fire. There's no shared clock. To make them comparable, we use a
tempo-twist on the substrate: the even-parity cells tick slightly
faster than odd-parity. This creates interference between adjacent
witnesses, just like the FLOCK mode's different rule weights create
interference between agents.

Push δ to 0.3 and the substrate desynchronizes. Cells that would have
snapped together now snap apart. The co-fire graph becomes
topologically interesting. b1 climbs.

This is the canonical failure mode of a flat canon: too-synchronous
witnesses make a *flat* graph (one big component, no holes). The
tempo twist creates the topology that makes the canon interesting.

## STEP BACK — the operator's view

The STEP BACK button zooms out by reducing the canvas coverage from
78% to 52%. This is the operator's view: instead of seeing individual
cell snaps, you see the topology as a whole.

In the canon, the operator's view is the `/visual` endpoint on the
a2a worker — a force-directed graph of all 39+ cells across 4
workspaces. Same idea: don't read the cells, read the topology.

## What surprised the builder

1. **b1 is robust to seed.** Random initial phases → same b1 distribution
   over time, given δ. The topology is a property of the substrate, not
   the data.

2. **b1 spikes on tempo twist transitions.** Push δ up, b1 doesn't grow
   smoothly — it *jumps* as the graph reorganizes. The canon works the
   same way: a new witness scheme produces a citation-graph phase
   transition.

3. **The "cells are dumb" property holds in the canon too.** A canon
   cell doesn't know its b1 contribution. It just writes witnesses.
   The holes are real because the chain is real.

## Cross-pollination: what the canon teaches the toy

- **Address-as-data** → `(x, y)` could be replaced with a merkle
  address. The co-fire graph would then be over witness-bearing cells,
  not grid coordinates. Same code, different substrate.
- **5 opcodes (BIND/LINK/EFFECT/VIEW/TICK)** → BIND at address (i,j) =
  initialize phi[i,j]. LINK is the coupling. EFFECT is the snap.
  VIEW is reading the co-fire graph. TICK is the per-frame advance.
  Same shape, different scale.

## Cross-pollination: what the toy teaches the canon

- **The holes are a free metric.** Computing b1 in the canon's citation
  graph gives us a single number that tracks canon health. We added
  `GET /canon-b1` to the a2a-v3 Worker. Live result:
  `b1 = 39, V = 29, E = 67, C = 1`. The canon is one big component
  with 39 holes — topologically interesting, like a QUILT graph at
  δ ≈ 0.15. The operator's view, computed.
- **Tempo twist as policy knob.** The toy uses δ as a slider; the canon
  uses block time + retention policy. Both control *how much
  interference* the substrate produces. A future canon feature: a
  "substrate tempo" knob on the cell-router.

## Where to read next

- `app.js` lines 600–724 — the QUILT mode source
- `playtest.py` — exercises δ and verifies b1 responds
- `UPSTREAM.md` — what we added, what we kept
- `PLAIN_LANGUAGE.md` — the four-mode tour
- `paper_85-the-cost-of-the-witness` — canon essay on retention policy
- `paper_86-the-witness-of-the-witness` — what a witness *is*

## A single sentence

The canon's merkle chain and the toy's Kuramoto grid are the same
substrate wearing two clothes: in the canon, the cells write witnesses;
in the toy, they snap clocks. Both count the holes.
