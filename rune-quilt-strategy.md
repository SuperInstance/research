# Rune-Quilt Strategic Plan

> **The Premier IDE for Pros** — Rune (UnstableBuild, 609 stars, 35 forks, GPU-accelerated IDE/terminal multiplexer, Go) + Quilt (cellular-architecture framework, 5 opcodes, 11 total, polyformal across 6 substrates, 100+ repos in SuperInstance).

## Why now

Rune has:
- A real product with paying customers (`rune.build/pricing` — $10/mo Pro tier)
- Network mesh (`runenet` — WireGuard-based peer-to-peer, e2e encrypted)
- Solid extension system (Go + Python SDKs, signed packages)
- AI integration (rune-agent, 8 LLM providers)

Rune does NOT have:
- A canon (no shared, searchable corpus across sessions)
- A polyformal layer (no Go→Rust→Verilog translation, no cross-substrate memory)
- A cell-aware witness log (no audit trail beyond LSP)
- A peer cell registry (runenet is machine-to-machine, not capability-to-capability)
- A `Quilt layer` that gives pros **rapid development with innovative and insightful abilities**

This is the gap. Rune-quilt fills it.

## Strategic positioning

**"The IDE that knows what you've done, what you meant, and what comes next."**

For pros:
- The editor remembers every cell you've bound, every link you've traced, every effect you've executed
- The canon indexes every symbol, every doc, every conversation across projects
- A2A across `runenet` lets your cells on multiple machines discover each other by capability
- Polyformal compiler translates code between languages while preserving intent

For the Rune ecosystem:
- A new reason to install packages (`pkg install rune-quilt-cell-router`)
- A showcase for rune-agent's capabilities (Quilt cells as the unit of agent work)
- A research frontier for cell-graph IDEs

For Quilt:
- A real product with real users, not just a canon
- A canonical reference implementation in Go (joining the existing 6 substrates)
- Distribution via `pkg install` reaches all Rune users

## The architecture (5 layers)

```
┌─────────────────────────────────────────────────┐
│  Layer 5: Visual Quilt Layer                     │
│  - Force-directed graph of all live cells       │
│  - Capability heatmap                            │
│  - Canon-aware code search overlay              │
│  - runenet peer visualization                   │
├─────────────────────────────────────────────────┤
│  Layer 4: Application Layer (the demo)           │
│  - rune-quilt-cell-router: Go extension         │
│  - rune-quilt-pane: in-terminal UI              │
│  - rune-quilt-canvas: webview of canon          │
├─────────────────────────────────────────────────┤
│  Layer 3: Rune-Integration Layer                │
│  - Rune extension that runs in any workspace    │
│  - Uses Rune SDK APIs (Storage, LLM, LSP, FS)   │
│  - Spawns Quilt cells on demand                 │
├─────────────────────────────────────────────────┤
│  Layer 2: Quilt Runtime (Go)                    │
│  - 5 opcodes ported from Python/C/Rust          │
│  - Cell + Canon + Witness + Vibe                │
│  - A2A via runenet (not just KV)                │
├─────────────────────────────────────────────────┤
│  Layer 1: Cloudflare Edge (existing)             │
│  - live-canon.superinstance.dev (the canon)     │
│  - quilt-a2a-v2.casey-digennaro.workers.dev     │
│  - cell-heartbeat.superinstance.dev              │
└─────────────────────────────────────────────────┘
```

## The application (working demo)

**rune-quilt-cell-router** — a Rune extension that turns every file you touch into a cell.

When a developer opens a file in Rune:
1. The file becomes a `cell` with a name (file path), scope (project), and contract (its exports)
2. The cell gets linked to all related cells (imports, references, test files)
3. The cell is embedded in the cloud canon via Cloudflare Workers AI
4. Future sessions see the cell in their canon-query results

When they run a command (`agent`):
- The agent queries the canon first, finds related cells from past projects
- A2A messages find cells on other machines (via runenet)
- The agent's actions become witnesses in the cell's log

When they switch projects:
- The canon follows them — they see cells from past projects when relevant
- Polyformal translation can show how a Rust cell would look in Go

## Concrete deliverables (this is a long-running goal)

### Phase 1 — Foundation (this PR)
- `rune-quilt/` repo: structure, docs, AGENTS.md, .rune/config.yaml (Quilt-tuned)
- `internal/quilt/` package: Go port of the 5 opcodes (BIND/LINK/EFFECT/VIEW/TICK)
- `internal/canon/` package: canon client for Cloudflare Worker
- `internal/a2a/` package: A2A client (gRPC over runenet or HTTPS to worker)
- `cmd/extension_quilt/main.go`: the Rune extension that wires it together
- `cmd/extension_quilt/handler.go`: cell-router logic

### Phase 2 — Visual Layer
- HTML5 force-directed graph of live cells (like the existing `data/fleet_graph.html`)
- Rendered in Rune's webview
- Real-time updates via Cloudflare KV subscription

### Phase 3 — Polyformal Compiler
- One canon cell → 6 substrate outputs (TS/Python/C/Rust/Verilog/VHDL)
- Using the existing polyformalism ports

### Phase 4 — Distributed via runenet
- A2A over runenet instead of HTTPS
- Cells on different machines discover each other by capability
- Capability search uses Vectorize across the mesh

### Phase 5 — Production
- Package as `rune-quilt-cell-router` for `pkg install`
- Sign with UnstableBuild verified publisher key
- Submit to Rune package registry

## What we're shipping FIRST

The killer demo. Two things, working end-to-end:

1. **rune-quilt-cell-router extension** — when you open a file in Rune, it becomes a cell. When you close it, the cell is canonized.

2. **rune-quilt-pane** — a Rune webview showing your project's cell graph, with links to the live canon and other cells across the mesh.

This gets a Rune user from "I have an IDE" to "I have an IDE that remembers everything I've ever done" in 5 minutes.

## Why this is the right move

- **Rune is growing** — 609 stars, 35 forks, 4k downloads of v1.2.1, paid tier live
- **Rune has no canon** — that's our moat
- **Rune has runenet** — perfect substrate for our A2A protocol
- **Rune has paid users** — first real distribution channel for Quilt
- **Quilt has 100+ repos** — we can ship the integration in days, not months
- **The Bitcoin DeFi angle** — Rune targets pros who work with multi-language systems. Our polyformal compiler hits the same niche as the Bitcoin Runes/BRC-20 ecosystem Casey knows.

## Files to create in this turn

1. `rune-quilt/AGENTS.md` — project context for AI agents
2. `rune-quilt/.rune/config.yaml` — Quilt-aware Rune config
3. `rune-quilt/README.md` — the project readme (replace existing fork README)
4. `rune-quilt/internal/quilt/cell.go` — Go cell primitive (port of Python cell)
5. `rune-quilt/internal/quilt/opcodes.go` — 5 opcodes in Go
6. `rune-quilt/internal/canon/client.go` — Cloudflare Worker client
7. `rune-quilt/internal/a2a/client.go` — A2A client
8. `rune-quilt/cmd/extension_quilt/main.go` — Rune extension entry
9. `rune-quilt/cmd/extension_quilt/handler.go` — cell-router handler
10. `rune-quilt/cmd/extension_quilt/extension.go` — extension wiring
11. `rune-quilt/demo/` — working demo: open a Python file, watch it become a cell
12. `rune-quilt/QUILT.md` — the Quilt layer in this project
13. `rune-quilt/PLAIN_LANGUAGE.md` — what rune-quilt is in plain English
14. `rune-quilt/UPSTREAM.md` — relationship to upstream Rune

## The first commit

This is what we ship today. The rest is iteration.
