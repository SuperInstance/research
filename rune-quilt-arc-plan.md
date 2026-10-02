# rune-quilt — Multi-Team Arc Plan

**Date:** 2026-09-16
**State:** v1.0.0 runtime shipped. Phase 2 (Visual) + Phase 3 (Polyformal Compiler) still open. v1.5.0+ phases still open.

---

## Vision (where this is going)

> A Rune workspace where every file is a cell in a merkle-rooted witness log, every save canonizes to a Cloudflare canon, every peer is found by semantic meaning, every cell ports to 6 substrates, and the IDE itself is a living graph.

The v1.0.0 ships the **runtime layer**. The remaining work is the **experience layer** + **compiler layer** + **fleet layer**.

---

## Team Roster — 5 parallel teams

### Team A — BUILDERS (Phase 2: Visual Layer)
**Goal:** Rune webview showing the cell graph live, in the IDE.

**Tasks:**
1. Build `internal/visual/server.go` — HTTP server, vanilla JS dashboard
2. Embed `data/fleet_graph.html` style into rune-quilt extension
3. Add SSE endpoint for live witness stream
4. Wire extension_quilt to push witness events to visual server
5. Ship `cmd/extension_quilt/visual.go` — Rune webview component
6. Demo: walk the rune-quilt repo, render live cell graph
7. Real-time updates when cells tick (every save/change = new edge)

**Deliverable:** v1.1.0 — Visual layer live in Rune webview
**Lead agent:** general-purpose (Go + JS)
**Checkpoint:** graph renders 50+ cells, SSE updates <100ms

### Team B — TESTERS (Quality Gate for v1.0.0)
**Goal:** Adversarial test suite that proves v1.0.0 holds up.

**Tasks:**
1. Unit tests for `quilt/cell.go` (Bind/Link/Effect/View/Tick, merkle root stability)
2. Unit tests for `canon/client.go` (mock HTTP server, all endpoints)
3. Unit tests for `a2a/client.go` (mock HTTP server, all endpoints)
4. Integration test: extension_quilt starts, registers 4 commands, ticks a2a
5. Stress test: 10,000 cells in single cluster, witness log persistence
6. Polyformalism test: same contract hashes identically in Go vs Python reference
7. Fork-sync test: `git fetch upstream main && git rebase upstream/main` must not conflict
8. CI: GitHub Actions matrix (Go 1.25.6, 1.26.6, 1.27-rc)

**Deliverable:** v1.0.1 — tests + CI badge on README
**Lead agent:** general-purpose (test-driven)
**Checkpoint:** 80%+ coverage, all integration tests pass, fork-sync clean

### Team C — RESEARCHERS (Phase 3: Polyformal Compiler Spec)
**Goal:** Spec out the polyformal compiler that takes one canon cell and ports it to 6 substrates.

**Tasks:**
1. Read existing 6 polyformal ports (TS/Py/C/Rust/GDScript/C-kernel)
2. Identify the *minimal* IR (intermediate representation) that all 6 can express
3. Design the canon cell → IR lowering
4. Design the IR → 6-substrate lifting
5. Identify what canon tags matter for porting decisions
6. Prototype IR in 100 lines of Go (`internal/ir/`)
7. Write white paper: "The Polyformal Canon" — why this works
8. Benchmark: canon cell #115 → 6 ports in <100ms each

**Deliverable:** v1.2.0 — IR spec + paper + prototype compiler
**Lead agent:** explore + general-purpose (paper-writing + Go)
**Checkpoint:** IR covers all 11 opcodes, paper is publishable

### Team D — FLEET (Multi-cell operations)
**Goal:** Wire rune-quilt into the a2a fleet so multiple Rune workspaces can collaborate.

**Tasks:**
1. Add `/broadcast-edit` endpoint to a2a Worker v2 (semantic broadcast of file changes)
2. Add `peers/near` to find cells in same-named workspace
3. Implement "ghost cells" — see other workspaces' open files in your own cell graph
4. Add fleet-aware demo: spin up 3 rune-quilt workspaces, show cross-workspace edges
5. Document the multi-cell ops in `FLEET.md`
6. Measure: 3 workspaces × 100 files = 300 cells, federation works

**Deliverable:** v1.3.0 — Fleet mode, multi-workspace federation
**Lead agent:** general-purpose + Cloudflare Worker code
**Checkpoint:** 3 workspaces visible in single graph, ghost cells work

### Team E — CANON SHAPERS (Canon growth + bridges)
**Goal:** The canon should grow and self-bridge. While the other teams build, this team feeds them.

**Tasks:**
1. Bridge ancient-world/* to maritime canon (30 isolated pieces) — bridge essays
2. Add 50 auto-extended canon pieces via `auto_extend.py`
3. Add 20 canon pieces via multi-LLM ensemble (`fleet_hub_llm.py`)
4. Verify: closed loop — cell writes paper, paper is top hit for related query
5. Add `navigate` endpoint usage examples (currently unused) to canon client
6. Submit fleet_hub results to live canon

**Deliverable:** Live canon: 1236 → 1300+ pieces, bridges closed
**Lead agent:** general-purpose + canon_aware_quilt.py
**Checkpoint:** Ancient-maritime bridge done, fleet_hub achieves 9/9 consensus

---

## Coordination rules

- **Builders** and **Testers** race in parallel — when both finish, merge for v1.0.1.
- **Researchers** work alone, don't touch code, ship a spec.
- **Fleet** extends the a2a Worker; doesn't touch rune-quilt runtime.
- **Canon Shapers** is the only team that writes canon. Others read.
- All teams report back to root every 15 min.
- If a team gets stuck, root re-routes.

## Memory

- v1.0.0 release: https://github.com/SuperInstance/rune-quilt/releases/tag/v1.0.0
- a2a v2 Worker: https://quilt-a2a-v2.casey-digennaro.workers.dev
- live-canon: https://live-canon.casey-digennaro.workers.dev
- Local canon: 1236 pieces × 768d
- Workspace: /workspace/rune-quilt/
