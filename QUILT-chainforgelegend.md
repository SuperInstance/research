# QUILT — ChainForgeLegend as a cell-graph

This is the **Quilt projection layer** for ChainForgeLegend. The original
React app is preserved (see `UPSTREAM.md`); this document shows how the
same program becomes **visible as a cell-graph** using the 5+1 opcodes.

Audience: applied engineers who know distributed systems / state
management / React but not necessarily Quilt.

## What the cell-graph looks like

ChainForgeLegend has **8 canonical cells**. Every cell has a typed
address, a typed value, and typed links to neighbors.

```
                ┌──────────────────┐
                │   cell:title     │  type=string, value="ChainForgeLegend"
                │   axis=name      │  link: header_h1
                └────────┬─────────┘
                         │ (typed: "labels")
                         ▼
                ┌──────────────────┐
                │   cell:header    │  type=component, value=<header>
                │   axis=role      │  link: app_root
                └────────┬─────────┘
                         │ (typed: "renders")
                         ▼
                ┌──────────────────┐
                │   cell:app       │  type=component, value=<App>
                │   axis=tree      │  link: container
                └────────┬─────────┘
                         │ (typed: "mounts")
                         ▼
            ┌────────────────────────────┐
            │  cell:container            │  type=state, value={items, inputValue}
            │  axis=role                 │  links: input, list
            └────────┬───────────┬───────┘
                     │           │
        (typed:       │           │  typed:
         "binds")     │           │  "renders")
                     ▼           ▼
        ┌─────────────────┐  ┌─────────────────┐
        │  cell:input     │  │  cell:list      │
        │  type=string    │  │  type=array     │
        │  axis=control   │  │  axis=role      │
        │  link=add       │  │  link=item      │
        └────────┬────────┘  └────────┬────────┘
                 │ (typed: "submits")  │ (typed: "contains")
                 ▼                     ▼
        ┌─────────────────┐  ┌─────────────────┐
        │  cell:add_btn   │  │  cell:item_n    │
        │  type=event     │  │  type=object    │
        │  axis=action    │  │  axis=position  │
        └─────────────────┘  │  link=remove    │
                             └────────┬────────┘
                                      │ (typed: "selects")
                                      ▼
                             ┌─────────────────┐
                             │  cell:remove_btn│
                             │  type=event     │
                             └─────────────────┘
```

## The 5+1 opcodes in action

Every upstream action maps to a Quilt opcode:

| Upstream action | Quilt opcode | Cell(s) affected |
|---|---|---|
| Component mounts | `BIND` | New cell added to substrate |
| `useState(initial)` | `BIND` | Cell value = initial |
| `setState(newValue)` | `EFFECT(cell, lambda v: newValue)` | Cell value updates |
| Re-render | `VIEW(cell)` | Pure read for render |
| Component unmounts | `FORGET(cell)` | Cell removed |
| Tick (frame) | `TICK(dt)` | Clock advances |
| Initial fetch | `EXTEND(name, "react", effect_fn)` | Mount fetch cell |

## The cell subtypes (in this program)

| Cell | Type | Lifecycle |
|---|---|---|
| `cell:title` | Static string | `BIND` once, no effects |
| `cell:header` | Static component | `BIND` once |
| `cell:app` | Static component | `BIND` once |
| `cell:container` | Stateful component | `BIND` + `EFFECT` per state change |
| `cell:input` | Stateful value | `BIND` + `EFFECT` per keystroke |
| `cell:add_btn` | Event emitter | `BIND` + `EFFECT` on click |
| `cell:list` | Collection | `BIND` + `EFFECT` on add/remove |
| `cell:item_n` | Item (one per row) | `BIND` per add, `FORGET` per remove |
| `cell:remove_btn` | Event emitter per item | `BIND` per item, `FORGET` per item removed |

## The witness chain (the audit trail)

Every state change appends to a witness log:

```
BIND cell:title value="ChainForgeLegend" @ tick=0
BIND cell:header @ tick=1
BIND cell:app @ tick=2
BIND cell:container @ tick=3
EXTEND fetch-cell @ tick=4
EFFECT fetch-cell → {title, description} @ tick=5
FORGET fetch-cell @ tick=6
EFFECT cell:input → "" @ tick=7
EFFECT cell:add_btn → submit(inputValue) @ tick=8
EFFECT cell:list → [..., {id, text, timestamp}] @ tick=9
EFFECT cell:input → "" @ tick=10
EFFECT cell:remove_btn → filter(id) @ tick=11
FORGET cell:item_1 @ tick=12
```

The witness chain is **replayable**: you can reconstruct any session from
the log. This is how the Quilt substrate makes the React app auditable.

## Polyformal port plan

The same 8-cell substrate ports to:

| Port | What it adds |
|---|---|
| **React (upstream)** | The original — already Quilt-shaped, just unstated |
| **TypeScript port** | Same 8 cells, typed; extends `tsconfig.json` |
| **Python simulator** | Reference port for testing; 8 dataclasses |
| **JSON-API** | The 8 cells exposed as REST; deployable to Workers |
| **Pico firmware** | The 8 cells on a microcontroller; small enough to fit |

## Integration with the broader Quilt ecosystem

- **`quilt-cordis`** — the cell-plugin bridge; each upstream component
  maps to a Cordis plugin via `bridge()` / `unbridge()`
- **`quilt-casting`** — model router; if you add AI suggestions for items,
  the casting plugin picks which model suggests
- **`flx-cuda`** — the GPU substrate; the witness chain can be GPU-encoded
  for high-throughput replay
- **`flux-hardware`** — the hardware backend picker; a React app's cells
  could be EFFECTED on a CUDA backend for batch state diffs

## Code example (Python, reference port)

```python
from quilt_cordis import Cell, Substrate

sub = Substrate(name="chainforgelegend")

# BIND the 8 cells (mirrors the upstream component tree)
title = sub.bind(Cell(address="title", value="ChainForgeLegend"))
header = sub.bind(Cell(address="header"))
app = sub.bind(Cell(address="app"))
container = sub.bind(Cell(address="container", value={"items": [], "inputValue": ""}))
inp = sub.bind(Cell(address="input", value=""))
list_ = sub.bind(Cell(address="list", value=[]))

# TYPED LINKS
sub.link("title", "header", edge_type="labels")
sub.link("header", "app", edge_type="renders")
sub.link("app", "container", edge_type="mounts")
sub.link("container", "input", edge_type="binds")
sub.link("container", "list", edge_type="renders")
sub.link("input", "list", edge_type="submits")

# EFFECT — type into the input
sub.effect("input", lambda v: "Hello Quilt")

# EFFECT — click Add → adds to list
sub.effect("list", lambda items: items + [{
    "id": 12345, "text": sub.view("input"), "timestamp": "2026-09-15T00:54:50Z"
}])
sub.effect("input", lambda v: "")

# VIEW — read the list
print(sub.view("list"))
# [{'id': 12345, 'text': 'Hello Quilt', 'timestamp': '2026-09-15T00:54:50Z'}]

# WITNESS chain — every state change is logged
print(f"Witness events: {len(sub.witness)}")
```

## The honest scope

- **What was ported:** The component tree, the state shape, the event flow
- **What was preserved:** All upstream code, all upstream tests
- **What was added:** The cell-graph projection (this document)
- **What's stubbed:** None — the upstream is genuinely just a React skeleton
- **What's deferred:** GPU backend, Pico port, vectorization

## See also

- `UPSTREAM.md` — original repo, faithfully documented
- `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands
- `README.md` (landing page) — dispatches you to the right doc
