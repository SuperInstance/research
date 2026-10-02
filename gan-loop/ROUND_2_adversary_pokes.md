# GAN Round 2 — Adversary Pokes Deeper

## The Generator's 4 candidates, scored

| Candidate | Generator align | Adversary align | Adversary's verdict |
|-----------|----------------|-----------------|---------------------|
| TIME_cell_as_tick | +0.995 | +0.950 | Likely true, but trivial |
| COST_cell_as_resource | +0.995 | +0.943 | A spreadsheet with a column |
| FAILURE_cell_as_mortal | +0.972 | +0.977 | Conventional |
| PLURALITY_cell_as_swarm | +0.962 | +0.991 | **MOST ORTHOGONAL — REVEALS NEW AXIS** |

## Adversary's deep critique

### TIME_cell_as_tick
*Looks like:* add a `tick_rate` to Cell.
*Hidden assumption:* time is global and monotonic.
*The hole:* What if two cells have *different* times? The workbook can't model that. TFMClock has private cell time; we never wired it into Workbook.
*The real challenge:* **DISTRIBUTED TIME** — each cell has its own clock with skew, and the workbook's "global tick" is the witness-log average. This is `quilt-spreadsheet` already showed distributed clocks with skew. We didn't port it.

### COST_cell_as_resource
*Looks like:* add `cost_usd` to Cell.
*Hidden assumption:* cost is scalar and computable.
*The hole:* What's the cost of *uncertainty*? What's the cost of *waiting*? What's the cost of *being wrong*? These are not scalars; they're functions of time and probability.
*The real challenge:* **PROBABILISTIC COST** — the cell's cost is a *distribution* over future states. The Designer budgets expected cost; the Adversary budgets worst-case.

### FAILURE_cell_as_mortal
*Looks like:* add `lifecycle` field to Cell.
*Hidden assumption:* failure is binary (alive/dead).
*The hole:* A cell can fail *silently* — emit wrong values, get stuck in a loop, hallucinate. The witness log shows the cell is *active*, but the cell is *lying*.
*The real challenge:* **HONESTY DETECTION** — the workbook can detect when a cell's outputs contradict the cell's own witness log. The cross-substrate chord already does this for canon; cells should too.

### PLURALITY_cell_as_swarm
*Looks like:* allow a Cell to contain other Cells.
*Hidden assumption:* the inside is smaller than the outside.
*The hole:* A cell containing cells is a *fractal*. The Designer, Porter, and Projection are themselves cells. The projection of a projection is a projection. Where does the recursion stop?
*The real challenge:* **RECURSIVE PROJECTION** — the Projection Agent projects a workbook. What does it mean to project a Projection? The boat-as-Quilt example *is* this — the LED matrix is a projection, but the LED matrix's state could itself be a workbook with its own Designer/Porter/Projection. **The Quilt is fractally self-similar.**

## Adversary's synthesis

The 4 candidates are not equal. Three of them (TIME, COST, FAILURE) are **extensions** — they add a column to the existing schema. The fourth (PLURALITY) is a **revolution** — it changes the *type* of the cell from `Cell` to `Cell = Union[Atomic, Compound]`.

The Adversary votes: build PLURALITY first. The other three will fall out naturally once cells can contain cells (because then time/cost/failure all become *aggregate* properties).

## Generator's counter-critique

But PLURALITY is the HARDEST one. It needs:
- A new IO type (`EMBEDDED_QUILT` already exists in ax-quilt — perfect!)
- A new cell kind (`Swarm`, `Federation`, `Quorum`)
- Recursive projection (the boat LED matrix has its own workbook)
- Termination (a swarm of swarms of swarms → must bottom out in atomic cells)

This is a **30-day project**, not a 30-minute project. The Adversary is right that PLURALITY is the deepest, but the Generator should NOT do it first. The Generator should:
1. Build TIME (1 hour) — the simplest, addresses the workbook's biggest gap
2. Build HONESTY (1 day) — turns witness logs into detectors
3. Build PLURALITY (1 week) — the deep one, after TIME and HONESTY are stable

## New adversarial finding

When the Generator says "the boat LED matrix has its own workbook", the Adversary hears: **the LED matrix's workbook is a *projection* of the boat's workbook**. But the LED matrix has *its own* sensors (buttons, dials, the panel-mount rotary encoder for heading). Those sensors feed INTO the LED matrix's workbook. The LED matrix's workbook projects BACK to the boat's workbook.

**This is a feedback loop, not a projection.** The Adversary has found a new verb:

### Bidirectional Projection

The current Projection Agent is *one-way*: workbook → LED. The Adversary demands *two-way*: workbook → LED → button press → workbook. The LED matrix is now a *cell* that contains *cells*. The workbook is no longer top-down; it is **a ring**.

## Round 3 challenge

Build a single demonstration of **bidirectional projection** — a workbook cell that projects to a runtime, AND the runtime feeds back into the workbook. Use the boat: the LED dashboard projects heading/SOG, AND a panel-mount rotary encoder feeds back into the target_heading cell.

This is one build, not four. It contains TIME (clocks), HONESTY (the rotary encoder value must match what the cell said), and PLURALITY (the LED dashboard cell contains a sub-workbook).

## Updated verdict

Single GAN outcome: **`bidirectional_projection_demo`** — boat autopilot workbook where the LED dashboard cell has a sub-workbook that projects back to the main workbook.

This is the build that the GAN loops have earned.
