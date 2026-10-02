# The 7-Port Conversion Chart — How to Quilt-port any program

**Date:** 2026-09-15 · **Status:** Reference template · **Use:** for every Quilt-port project after the Countroller

---

## The thesis

Every program can be Quilt-ported because Quilt is a **visualization and
intermediation layer for IO**. The Countroller's 32-cell substrate is the
smallest possible proof — once you have it, the template generalizes.

This chart is the recipe. Use it for the next port (paper trading, robotic
arm, DAW, browser game, prompt playground, anything). Same shape, every
time.

---

## The 7 ports — same cell-graph, every runtime

| # | Port | What replaces what | Same cells | Substrate |
|---|---|---|---|---|
| 1 | **Python simulator** | Reference port; runs in any interpreter | ✓ | Python 3.10+ |
| 2 | **C / firmware** | Real hardware; microcontroller SDK | ✓ | C / Pico SDK, ESP-IDF, etc. |
| 3 | **Rust / no_std** | Same hardware, type-safe | ✓ | Rust + embedded HAL |
| 4 | **TypeScript / browser** | Browser canvas + WebGPU | ✓ | TypeScript + WebGPU |
| 5 | **JSON-API** | REST over the cell-graph | ✓ | Python stdlib HTTP / Cloudflare Workers |
| 6 | **MIDI / DAW** | Music IO; cells become notes/CC | ✓ | MIDI 1.0 / OSC / Ableton |
| 7 | **Trading / paper** | Order book cells; trades as effects | ✓ | Alpaca / IBKR paper APIs |

The first 5 are documented for the Countroller. Ports 6 and 7 are the
near-future extensions.

---

## The 32-cell test

A program is **Quilt-portable** if it can be described as a 32-cell graph
with typed links. The test:

1. Can you list 32 cells (or fewer, or scaled up by powers of 2)?
2. Are the cells typed (LED / button / position / etc.)?
3. Are the typed links clear (sounds, displays, controls, renders)?
4. Can the cell-graph port to Pico, browser, server, JSON-API?
5. Can the witness chain replay any session?

The Countroller passes. Paper trading passes (32 cells: 4 portfolio
positions + 4 quantum + 4 display + 4 news + ... etc.). Robotic arm
passes (32 cells: 5 glove sensors + 4 joints + 4 status + ...).

**The far-future test:** every program, eventually, has a 32-cell view.
The view is the spreadsheet. The spreadsheet is the runtime.

---

## The porting workflow

### Step 1: Identify the 32 cells (or N cells, any N)

For any program, ask:

> What are the **inputs** that change state? (each is a cell)
> What are the **outputs** that render state? (each is a cell)
> What are the **intermediate computations** worth visualizing? (each is a cell)
> What are the **modes** or **states** worth tracking? (each is a cell)

For the Countroller: 25 LEDs + joystick + 2 buttons + joystick button + 2 buzzers + OLED = 32.
For paper trading: 4 positions + 4 quantum + 8 order book + 4 P&L + 8 display + 4 risk = 32.
For robotic arm: 5 glove sensors + 4 joint cells + 4 status + 4 trajectory + ... = 32.
For DAW: 16 step sequencer cells + 4 transport + 4 mixer + 4 quantize + 4 display = 32.

The 32 isn't a magic number — it's just **enough cells to be visualizable
on a spreadsheet**. Use 16, 64, 128 if it fits better. The substrate
scales.

### Step 2: Define the typed links

For each pair of related cells, define the edge type:

```
LINK("joystick", "cursor", edge_type="controls")
LINK("button_a", "buzzer_1", edge_type="sounds")
LINK("active_pattern", "led_2_2", edge_type="renders")
```

Edge types are nouns or verbs. They become searchable in the LINK graph:
"show me all cells that 'sounds' another cell."

### Step 3: Implement the 5+1 opcodes for the runtime

Each port implements the same 6 opcodes:

```python
# Universal
def BIND(cell): ...    # mount a cell at an address
def LINK(a, b, type): ...  # typed edge between cells
def EFFECT(cell, fn): ...  # mutate a cell, with inverse
def VIEW(cell): ...   # read a cell
def TICK(dt): ...     # advance clock
def FORGET(cell): ... # retire a cell
```

The implementation differs per port (C has `gpio_put`, Python has `self.value =`,
TypeScript has `document.getElementById`, etc.), but the **algebra is identical**.

### Step 4: Wire the input/output handlers

For each port, define how input cells get values and how output cells
render them.

| Port | Input source | Output sink |
|---|---|---|
| Pico | GPIO read, ADC sample, I2C read | GPIO write, PWM, NeoPixel serial, I2C write |
| Python | `sim.press_button_a()` | `print(sim.render_led_matrix())` |
| Browser | Mouse / keyboard / gamepad events | Canvas pixels, DOM updates |
| JSON-API | HTTP POST to `/cells/<addr>/effect` | HTTP response body |
| MIDI | MIDI input message | MIDI output message |
| Trading | Order book stream, news feed | Order submission |

### Step 5: Run the witness chain

Every effect appends to a witness log. The log is replayable. **The log
is the audit trail.** It's the same format across all 7 ports.

### Step 6: Write the educational one-pager

For each port, a 1-page document explains:
- The 32 cells (or N cells)
- The 5+1 opcodes in action
- How to override any decision (the educational hook)
- How to replay a session (the audit trail)
- Why this port exists (the use case)

The Countroller's `docs/extends-to-anything.html` is the template.

### Step 7: Add to the 7-port chart

Once a port ships, add a row to the chart. The chart is the **menu** of
what's possible. Future ports see the precedent and follow the pattern.

---

## The 5+1 opcodes (the universal algebra)

| Opcode | Algebra | Physics | Polytime |
|---|---|---|---|
| `BIND(cell)` | idempotent: BIND(BIND(c)) = BIND(c) | mount the cell | O(1) |
| `LINK(a, b, type)` | associative: LINK(LINK(a,b), c) = LINK(a, LINK(b,c)) | create typed edge | O(1) |
| `EFFECT(cell, fn)` | has inverse: EFFECT(EFFECT(c, f), f⁻¹) ≈ c | mutate with rollback | O(\|fn\|) |
| `VIEW(cell)` | pure: no side effects | read projection | O(1) |
| `TICK(dt)` | monotonic: t₂ > t₁ | advance clock | O(1) |
| `FORGET(cell)` | terminal: FORGET(c) → ⊥ | retire cell | O(k) for k effects |

These are **the same algebra in every runtime**. The Countroller's
implementation is in `quilt/cells.py`. A Pico implementation would be in
`quilt-cells.c`. A TypeScript implementation would be in `quilt-cells.ts`.
All three are byte-identical on the witness chain.

---

## The cell-graph invariants

A Quilt-ported program satisfies:

1. **Cell addressability** — every cell has a unique string address
2. **Cell typing** — every cell has a type (LED, button, sensor, display, ...)
3. **Link typing** — every LINK has a type (controls, sounds, renders, ...)
4. **Witness append-only** — the witness chain only grows
5. **TICK monotonicity** — the clock only advances
6. **EFFECT inverses** — every effect has an inverse (for FORGET)
7. **VIEW purity** — VIEW never mutates

If a port violates any invariant, it's not Quilt-portable. Fix it or
use a different abstraction.

---

## The roadmap (in priority order)

| # | Program | Why this port next |
|---|---|---|
| 1 | **Paper trading** | First CUDA-Q use case; visible quantum; educational |
| 2 | **DAW step sequencer** | Music cells; MIDI is universal; visible + audible |
| 3 | **Robotic arm (Quilt-Robotic-Arm)** | Existing port plan; physical demo |
| 4 | **LLM prompt playground** | Token cells; visible AI work; educational |
| 5 | **Spreadsheet macro recorder** | The spreadsheet is the runtime; record actions as cells |
| 6 | **Game state debugger** | Cells for every game entity; witness = replay; undo |
| 7 | **Weather station cellularization** | From CUDA-Q §3.4; quantum finds fronts |

Each follows the same template. **Once you have the recipe, every program is one of these.**

---

## The far-future first

Working backwards from the year 2032:

> Every program in 2032 is a cell-graph. The substrate is universal. The
> cell-graph is visible — you watch it work like a spreadsheet. The
> witness chain is the audit trail. The quantum planning layer proposes;
> the classical substrate commits. CUDA-Q is the planner. The Quilt is
> the substrate. Polyformalism is the deployment vector. Every program
> ports to every runtime. **The Quilt is the spreadsheet of intelligence.**

That's the destination. The Countroller is the smallest possible proof.
This chart is the recipe for getting there.

---

**Files in this template:**

- `quilt-countroller-quilt-port/` — the reference port (Python simulator)
- `quilt-countroller-quilt-port/quilt/api.py` — the JSON-API surface
- `quilt-countroller-quilt-port/docs/extends-to-anything.html` — the visualization
- This file — the recipe for every next port

**Next ports to ship (priority order):**

1. Paper trading (CUDA-Q use case 1)
2. DAW step sequencer (MIDI port)
3. Robotic arm (existing port plan, continue from sensor wrap)
4. LLM prompt playground (token cells)
