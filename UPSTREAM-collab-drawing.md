# UPSTREAM — Collaborative Real-Time Drawing System (preserved from upstream)

This document preserves the **original upstream project** — Collaborative
Real-Time Drawing System, by mominyar — faithfully, with no Quilt
framing imposed. If you want the original, **read this first**. The
Quilt layer (added by SuperInstance) is documented separately in
`QUILT.md`.

## Original description

> A real-time multi-user drawing application built with Java, JavaFX,
> and TCP Sockets. Multiple simultaneous users draw on a shared canvas
> in real time, with TCP-socket communication synchronizing strokes
> across all connected clients. Registration and authentication
> included.

## What the upstream is

- A **Java 25 + JavaFX 25** desktop application
- **TCP socket** multi-client server (`OpsMapServer`) accepting
  connections on port 5050 (customizable)
- **JavaFX client** (`OpsMapClientApp`) with login + collaborative
  workspace
- **Maven build** (`pom.xml`), `mvn clean package` produces the JAR
- Per-client handler thread on the server side; broadcast to all
  connected clients when a stroke arrives

## What the upstream does

Three reference screenshots in the original README:
1. **Client login screen** (per-client authentication UI)
2. **Second client** login screen (proving multi-user)
3. **Collaborative workspace** (shared canvas where users draw)

The user flow:
1. Operator starts the server (`OpsMapServer`)
2. Each user launches the JavaFX client
3. Each user registers / logs in with unique credentials
4. Each user draws on their client canvas
5. Strokes broadcast over TCP to all other clients in real time
6. All clients see synchronized drawings on the shared workspace

## How the upstream works

```
src/main/
├── server/
│   └── OpsMapServer.java      — Accepts TCP connections on port 5050
│                                Spawns a handler thread per client
│                                Broadcasts incoming strokes
├── client/
│   └── OpsMapClientApp.java   — JavaFX UI: login + workspace
│                                Sends strokes over TCP
│                                Receives strokes from server
├── login-1.png                — Screenshot
├── login-2.png                — Screenshot
└── collaborative-workspace.png — Screenshot

pom.xml                        — Maven build, Java 25 target
```

### Data flow

1. Client A draws a stroke on its JavaFX canvas
2. Stroke coordinates serialize into a TCP message
3. Message goes to server (`OpsMapServer`)
4. Server broadcasts to all connected clients (B, C, …)
5. Each receiving client deserializes and renders the stroke
6. All clients see the same canvas state (eventually-consistent sync)

## Quick start (original)

```bash
git clone https://github.com/SuperInstance/collaborative-realtime-drawing-system-quilt.git
cd collaborative-realtime-drawing-system-quilt

# Verify tooling
java --version                  # should be Java 25
mvn --version                   # Maven 3.6+

# Build
mvn clean package

# Start server (terminal 1)
java -cp target/... opsmap.server.OpsMapServer 5050

# Start client (terminal 2, 3, 4 for multi-user test)
mvn javafx:run
# JavaFX main class is opsmap.client.OpsMapClientApp
```

## Credits and license

- **Upstream author:** mominyar
  ([mominyar/collaborative-realtime-drawing-system](https://github.com/mominyar/collaborative-realtime-drawing-system))
- **Upstream license:** preserved (see `LICENSE`)
- **Quilt elevation:** SuperInstance (added the cell-graph projection layer)
- **Quilt layer license:** MIT (added as `LICENSE-QUILT`)

## Notes on the fork

- **Date imported:** 2026-09-15
- **Preserved:** All upstream code (server, client, screenshots, Maven
  config). Nothing upstream was modified.
- **Added:** `QUILT.md` (the cell-graph projection), `PLAIN_LANGUAGE.md`
  (captains-and-mechanics version), and an updated landing-page README.
- **Pre-Quilt quirks:** The README credits the project as "opsmap" in
  the Maven `groupId` / artifact paths, but the README title is
  "Collaborative Real-Time Drawing System." We preserved both. The
  artifact naming follows upstream conventions; the documentation name
  follows the upstream README.

---

For the **Quilt projection layer** that makes this program **visible as
a cell-graph**, see `QUILT.md`. For the **plain-language version** that
explains what this does for working people, see `PLAIN_LANGUAGE.md`.
