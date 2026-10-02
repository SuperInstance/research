# QUILT — Collaborative Real-Time Drawing System as a cell-graph

This is the **Quilt projection layer** for the Collaborative Real-Time
Drawing System. The original Java/JavaFX/TCP app is preserved (see
`UPSTREAM.md`); this document shows how the same program becomes
**visible as a cell-graph** using the 5+1 opcodes.

Audience: applied engineers who know distributed systems / Java /
TCP socket programming but not necessarily Quilt.

## What the cell-graph looks like

The collaborative drawing system has **3 server-side cells** + **N×M
client-side cells** where N is the number of clients and M is the
number of canvas cells per client. A 1000-stroke canvas is **1000 cells**.

### Server substrate

```
                     ┌─────────────────────────────┐
                     │   cell:server_root          │  type=tcp_listener
                     │   value={port:5050,        │  axis=role
                     │          clients:[A,B,C]}   │  link: child_handlers
                     └──────────────┬──────────────┘
                                    │ (typed: "spawns")
                                    ▼
            ┌─────────────────────────────────────────────┐
            │                                             │
   ┌────────▼─────────┐      ┌──────────────────┐         │
   │ cell:handler_A   │      │  cell:handler_B  │  ...   │
   │ type=tcp_handler │      │  type=tcp_handler│        │
   │ value={socket,   │      │  value={...}     │        │
   │         user_id,  │      │                  │        │
   │         strokes}  │      │                  │        │
   │ axis=client       │      │                  │        │
   │ link: broadcast   │      │                  │        │
   └────────┬─────────┘      └────────┬─────────┘        │
            │ (typed: "broadcasts_to")                    │
            └─────────────────────┬───────────────────────┘
                                  ▼
                     ┌─────────────────────────────┐
                     │   cell:broadcast_hub         │  type=router
                     │   axis=role                  │  link: every_handler
                     └─────────────────────────────┘
```

### Client substrate

```
            ┌─────────────────────────┐
            │  cell:login             │  type=form
            │  axis=auth              │  link: workspace
            └────────────┬────────────┘
                         │ (typed: "authenticates")
                         ▼
            ┌─────────────────────────┐
            │  cell:workspace         │  type=component
            │  axis=role              │  link: canvas
            └────────────┬────────────┘
                         │ (typed: "renders")
                         ▼
            ┌─────────────────────────────────────────┐
            │  cell:canvas                              │  type=canvas
            │  axis=surface                            │  link: every_stroke
            │  value=[stroke_1, stroke_2, ..., stroke_k]│
            └────────────┬────────────────────────────┘
                         │ (typed: "contains")
                         ▼
            ┌─────────────────────────┐
            │  cell:stroke_n          │  type=stroke
            │  value={user, x1,y1,   │  link: tcp_send, tcp_recv
            │          x2,y2, color,  │
            │          timestamp}    │
            │  axis=position          │
            └─────────────────────────┘
```

## The 5+1 opcodes in action

Every upstream action maps to a Quilt opcode:

| Upstream action | Quilt opcode | Cell(s) affected |
|---|---|---|
| Server binds port | `BIND` | `cell:server_root` |
| Client connects | `BIND` | new `cell:handler_X` |
| Client disconnects | `FORGET` | `cell:handler_X` |
| User draws stroke | `EFFECT(cell:stroke_n, lambda _: stroke_data)` | new stroke cell, broadcast |
| Server receives stroke | `EFFECT(cell:canvas, lambda _: canvas + stroke)` | canvas cell updated |
| Stroke renders | `VIEW(cell:canvas)` | pure read for render |
| Tick (frame) | `TICK(dt)` | clock advances |

## The cell subtypes

| Cell | Type | Lifecycle |
|---|---|---|
| `cell:server_root` | TCP listener | `BIND` once at startup |
| `cell:handler_X` | Per-client TCP handler | `BIND` on connect, `FORGET` on disconnect |
| `cell:broadcast_hub` | Router | `BIND` once |
| `cell:login` | Auth form | `BIND` once per client session |
| `cell:workspace` | UI component | `BIND` once per client session |
| `cell:canvas` | State (list of strokes) | `BIND` once, `EFFECT` per stroke |
| `cell:stroke_n` | Single stroke (per drawing operation) | `BIND` per draw, persists in canvas cell |
| `cell:stroke_event` | Event (TCP send/recv) | `BIND` per broadcast |

## The witness chain

Every state change appends to a witness log:

```
BIND cell:server_root port=5050 @ tick=0
BIND cell:handler_A user_id=alice @ tick=10
BIND cell:handler_B user_id=bob @ tick=15
BIND cell:handler_C user_id=charlie @ tick=20
EFFECT cell:canvas → [stroke_1] @ tick=23   # alice drew
BIND cell:stroke_1 {alice, (10,20)→(50,60), red} @ tick=24
EFFECT cell:canvas → [stroke_1, stroke_2] @ tick=28   # bob drew
BIND cell:stroke_2 {bob, (30,40)→(80,90), blue} @ tick=29
EFFECT cell:canvas → [stroke_1, stroke_2, stroke_3] @ tick=35
BIND cell:stroke_3 {charlie, (15,15)→(45,45), green} @ tick=36
FORGET cell:handler_B @ tick=42   # bob disconnected
```

This is the **eventually-consistent log**. Replay it and you reconstruct
the exact drawing session. This is exactly how `quilt-cell-router` does
A2A bottle-cell routing — same pattern, different protocol.

## Polyformal port plan

The same cell-graph ports to:

| Port | What it adds |
|---|---|
| **Java/JavaFX/TCP (upstream)** | Already running. Cell-graph projection reveals the implicit substrate. |
| **Python simulator** | Reference port for testing; `asyncio` for TCP simulation |
| **TypeScript / browser** | Canvas + WebSocket; the server becomes a Cloudflare Worker |
| **WebRTC port** | Lower-latency than TCP; cells become peer-to-peer |
| **Pico firmware port** | The "drawing" can be **muscle movements**; collaborative robotic arm drawing |

## Integration with the broader Quilt ecosystem

- **`quilt-cell-router`** — A2A bottle-cell routing. The broadcast hub
  IS a router. TCP sockets → bottle-cells.
- **`quilt-cordis`** — cell-plugin bridge. The Java server becomes a
  Cordis plugin; the JavaFX client becomes a Cordis effect.
- **`quilt-canon-cli`** — the witness chain can be canonized
  (`canon hash` → state hash → reproducible canvas state across replays).
- **`flx-cuda`** — GPU-accelerated canvas rendering; thousands of strokes
  composited at frame rate.
- **`conservation-law-rs`** — the conservation laws apply to draw events:
  *every stroke is conserved* (no stroke vanishes without an inverse).

## Code example (Python, reference port)

```python
from quilt import Cell, Substrate
import asyncio
import json

class DrawingServer:
    def __init__(self, port=5050):
        self.substrate = Substrate(name="collab_drawing")
        self.server_root = self.substrate.bind(Cell(
            address="server_root", value={"port": port, "clients": {}}
        ))
        self.broadcast_hub = self.substrate.bind(Cell(
            address="broadcast_hub"
        ))
        self.substrate.link("server_root", "broadcast_hub", edge_type="broadcasts_to")

    async def on_client_connect(self, user_id):
        handler = self.substrate.bind(Cell(
            address=f"handler_{user_id}",
            value={"user_id": user_id, "canvas": []},
        ))
        self.substrate.effect("server_root", lambda v: {**v, "clients": {**v["clients"], user_id: True}})
        self.substrate.link(f"handler_{user_id}", "broadcast_hub", edge_type="broadcasts")
        return handler

    async def on_stroke(self, user_id, stroke_data):
        # BIND the stroke cell
        stroke_cell = self.substrate.bind(Cell(
            address=f"stroke_{user_id}_{stroke_data['timestamp']}",
            value=stroke_data,
        ))
        # EFFECT: append to all clients' canvases
        for client in self.substrate.view("server_root")["clients"]:
            handler = self.substrate.cells[f"handler_{client}"]
            self.substrate.effect(f"handler_{client}",
                lambda v: {**v, "canvas": v["canvas"] + [stroke_data]})

        # Broadcast to all clients (mock)
        print(f"BROADCAST: {user_id} drew {stroke_data}")
        print(f"Witness events: {len(self.substrate.witness)}")

# Demo
server = DrawingServer()
asyncio.run(server.on_client_connect("alice"))
asyncio.run(server.on_client_connect("bob"))
asyncio.run(server.on_stroke("alice", {"x1":10,"y1":20,"x2":50,"y2":60,
                                        "color":"red","timestamp":"2026-09-15T01:00Z"}))
```

## The honest scope

- **What was ported:** The server/client TCP architecture, the canvas
  data model, the broadcast pattern
- **What was preserved:** All upstream code (server, client, screenshots,
  Maven config)
- **What was added:** The cell-graph projection (this document)
- **What's stubbed:** Per-client canvas cell state — the upstream has it
  implicit; the cell-graph makes it explicit
- **What's deferred:** WebRTC port, GPU canvas rendering, vectorize
  cross-pollination

## See also

- `UPSTREAM.md` — original repo, faithfully documented
- `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands
- `README.md` (landing page) — dispatches you to the right doc
