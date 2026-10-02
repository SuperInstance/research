# Collaborative Real-Time Drawing System — Quilt Edition

A Java/JavaFX/TCP multi-user drawing app (upstream by mominyar) elevated
with a Quilt projection layer so the same program is **visible as a
cell-graph**.

## The three doors — pick the one that fits you

- **📖 [UPSTREAM.md](docs/UPSTREAM.md)** — The original Java desktop
  app, faithfully documented. If you want the unmodified project, start
  here.
- **⚙️ [QUILT.md](docs/QUILT.md)** — The cell-graph projection layer.
  Engineering English. Shows how the TCP server + JavaFX client become
  cells with typed links.
- **🚢 [PLAIN_LANGUAGE.md](docs/PLAIN_LANGUAGE.md)** — For captains,
  mechanics, deckhands, working people. Two-minute read. Plain language.

## Status

| Area | State |
|---|---|
| Upstream code | ✅ Preserved, unmodified |
| Cell-graph projection | ✅ Documented (3 server cells + N client cells) |
| Python reference port | ✅ Example in `QUILT.md` |
| WebSocket / Cloudflare Worker port | 🔮 Future |
| WebRTC (peer-to-peer) port | 🔮 Future |
| Vectorize cross-pollination | 🔮 Future — needs Cloudflare DNS clear |

## Quick start (the original server + client)

```bash
# Verify Java 25 and Maven
java --version
mvn --version

# Build
mvn clean package

# Terminal 1: server
java -cp target/classes opsmap.server.OpsMapServer 5050

# Terminal 2, 3, 4: clients (one per user)
mvn javafx:run
# JavaFX main class: opsmap.client.OpsMapClientApp
```

Open multiple client windows, register/login with different names,
draw on one — see strokes appear on all.

## The cell-graph (canonical)

**Server (3 cells):** `server_root → broadcast_hub → handler_X` (one per client)

**Client (4 cells):** `login → workspace → canvas → stroke_n`

Every TCP connection is a `BIND`. Every stroke is an `EFFECT` on the
canvas cell, broadcast to every handler. Every render is a `VIEW`.
The witness chain IS the canvas event log.

## What we kept vs added

**Kept** (from upstream):
- All `src/` code (`opsmap.server.OpsMapServer`, `opsmap.client.OpsMapClientApp`,
  screenshots)
- `pom.xml`, Maven config
- The original `LICENSE`

**Added** (the Quilt layer):
- `docs/UPSTREAM.md` — original-repo-faithful documentation
- `docs/QUILT.md` — the cell-graph projection
- `docs/PLAIN_LANGUAGE.md` — working-people version
- `LICENSE-QUILT` — MIT, for the Quilt layer
- This README (rewritten as a landing-page dispatcher)

**Nothing in the upstream was renamed or moved.**

## See also

- [SuperInstance/quilt-cell-router](https://github.com/SuperInstance/quilt-cell-router) —
  A2A bottle-cell routing; the broadcast hub IS a router
- [SuperInstance/quilt-cordis](https://github.com/SuperInstance/quilt-cordis) —
  the cell-plugin bridge that makes the Java components addressable
- [SuperInstance/conservation-law-rs](https://github.com/SuperInstance/conservation-law-rs) —
  conservation laws for draw events (every stroke is conserved)
- The original: [mominyar/collaborative-realtime-drawing-system](https://github.com/mominyar/collaborative-realtime-drawing-system)
