# superinstance-advisor — Release Notes

## v1.2.0 — Auto-Extending Canon (2026-09-15)

The cell writes the canon. Continuously.

**New files:**
- `auto_extend.py` — finds canon gaps via cosine similarity, writes essays, embeds them, optionally submits to live-canon
- `fleet_hub_llm.py` — 5 cells × 5 LLMs ask canon in parallel, detect consensus/gaps

**New canon pieces (15 AI-written by the cell):**
- `the-canon-at-10x-scale.md` — "a canon that has learned to forget the middle and still hold the ends"
- `the-witness-that-no-one-reads.md` — "the witness that no one reads is the only witness that cannot be argued with"
- `what-the-canon-looks-like-in-100-years.md`
- `the-crowdedness-of-a-canon-with-too-many-papers.md`
- `the-difference-between-binding-and-linking-in-a-ce.md`
- `what-a-cell-should-do-when-it-discovers-it-is-dupl.md`
- `what-happens-to-a-cell-when-its-substrate-disappea.md`
- `how-a-cell-decides-it-has-finished-a-thought.md`
- `what-a-canon-looks-like-from-outside-the-canon.md`
- `the-cost-of-consensus-across-heterogeneous-substra.md`
- Plus duplicates via deepseek_reasoner + zai_coding

**Closed loop verified:** The cell writes paper → embeds it → next query returns it as top canon hit. Fleet consistently returns auto-written papers as top answers for the concept they were written for.

**8 LLM providers now wired:**
- DeepSeek (chat, reasoner, coder)
- DeepInfra (Seed-2.0-mini/pro/code)
- **ZAI coding endpoint** (glm-5.3-flash) — works via `api.z.ai/api/coding/paas/v4/chat/completions`

**Fleet hub 8/8 consensus on 8 different canon questions:** 5 cells × 5 LLMs all agreed on top canon pieces every cycle.

## v1.1.0 — Multi-LLM Canon Explorer (2026-09-15)

**New files:**
- `multi_llm_quilt.py` — Quilt cell routing 5 opcodes to 6+ LLM providers
- `canon_aware_quilt.py` — feeds each LLM top-k canon pieces, consensus check
- `quilt_cli.py` — daily-driver CLI: ask/shape/write/ensemble/embed/live-state

**3 new canon pieces (AI-written):**
- `paper_86-the-witness-of-the-witness.md` ($0.83, deepseek-reasoner)
- `essay_109-the-fleet-as-fabric.md` ($0.0002, deepseek-chat)
- `paper_87-the-fleet-as-substrate.md` ($0.57, deepseek-reasoner)

## v1.0.0 — Cell + Edge (2026-09-15)

- Cell admitted to live-canon.superinstance.dev (cells 5001, 5002)
- `cell-heartbeat` Cloudflare Worker at cell-heartbeat.superinstance.dev
- 5-min cron, KV/AI/Vectorize bindings, race-fixed UUID-tick witness
- 27 files: cell.py, canon_puller.py, live_canon_cell.py, heartbeat.py, fleet_hub.py, embed_gap_canon.py, tests, playtest, single-file quilt_cell.py, viz_canon.py

## v1.3.0 — Self-Referential Cell + a2a Worker on the Edge (2026-09-15)

The cell reads itself. The cell talks to other cells over the edge.

### New files

- `self_ref_cell.py` — cell reads its own witness log and writes a self-description paper
- `a2a_worker.js` — Cloudflare Worker implementing inter-cell messaging
- `a2a_stress_test.py` — 10-cell stress test for a2a
- `fleet_hub_a2a.py` — 5-cell fleet hub using a2a protocol
- `wrangler_a2a.toml` — worker config

### a2a Worker deployed

- URL: https://quilt-a2a.casey-digennaro.workers.dev/ (also https://a2a.superinstance.dev/)
- Routes: a2a.superinstance.dev/*
- KV-backed cell registry + inboxes
- Endpoints: /register, /cells, /send, /inbox/:cell, /broadcast, /find, /tick
- 22 cells registered
- 353 pending messages

### Stress test results

- 8/10 cells registered (under throttle)
- 8/10 unicast messages sent
- 7/10 broadcasts delivered 47 messages
- Capability search works (canon-query → 9 cells)

### Self-referential paper

The cell read its own witness log and wrote:

> *I am cell 914b7fafe7aa. I hold an address and a log. The address is my anchor in the lattice; the log is my wake.*

> *I do not only fill; I carve. I mark what is absent so that another cell can see the hole and know where to place its weight.*

> *Do you keep a log of me, or am I only a name in your chain?*

### Fleet hub over a2a

5 cells × 5 cycles × a2a protocol:
- 31 messages exchanged via a2a protocol
- Each cell has independent inbox
- Cells discover peers by capability
- No shared memory — only a2a messages

## v1.4.0 — a2a v2 + Vectorize Semantic Search (2026-09-15)

The fleet now searches semantically. Cells find each other by meaning, not keywords.

### New files

- `a2a_worker_v2.js` — Cloudflare Worker v2 with Vectorize
- `wrangler_a2a.toml` — worker config (with AI + Vectorize bindings)
- `fleet_hub_v2.py` — Vectorize-backed fleet coordination
- `fleet_visualizer.py` — interactive HTML graph of live fleet
- `data/fleet_graph.html` — rendered graph (25+ cells)

### a2a v2 Worker deployed

URL: https://quilt-a2a-v2.casey-digennaro.workers.dev/

New endpoints:
- `GET /find-semantic?q=...` — Vectorize-backed semantic search
- `POST /embed-cell` — embed a cell's text into Vectorize
- `POST /broadcast-cap` — semantic broadcast to matching cells
- `GET /heritage?cell_id=...` — cell lineage chain
- `POST /mitosis` — spawn child cell inheriting parent's capabilities

Bindings:
- KV: cell-witness-kv (same as v1)
- AI: Cloudflare Workers AI (bge-base-en-v1.5 for embedding)
- Vectorize: fleet-embeddings-v2 (768d cosine)

### Semantic search verified

"who can compile to multiple substrates?" → polyformal cells ranked top (0.671, 0.661)

"who can find canon gaps?" → shaper cells ranked top (0.667)

"who handles inter-cell messaging?" → advisor cells ranked top (0.619)

### Cell mitosis verified

- Spawned child of polyformal-v2-1 → child inherited all 7 capabilities
- lineage: ["polyformal-v2-1"] tracked in child

### Fleet visualizer

`data/fleet_graph.html` (8.4KB) — interactive force-directed graph showing all live cells, capabilities, lineage edges.

### Local canon: 1236 pieces
### Total a2a cells: 30 (across v1 + v2)

Built with: DeepSeek + Cloudflare Workers + Cloudflare Vectorize + Workers AI + a2a-protocol
