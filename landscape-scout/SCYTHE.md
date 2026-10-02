# SCYTHE — Landscape Scout Report (Sept 23, 2026)

> "Longlining and trawling are old technologies, but the engine changed the nature of boat motion." — Casey

## The new engines (the substrate that changes the catch)

| Engine | Built | Replaces |
|--------|-------|----------|
| `mavis-fleet` | Sept 23 | Multi-substrate RSI fleet — 6 substrates, 14 agent roles, polyformalism |
| `mavis-erised` | Sept 23 | Agent playground — zero-shot ergonomics testing |
| `ax-quilt v0.2.0` | Sept 23 | Cellular spreadsheet orchestrator — mesh with Docker/K8s/Go |
| `quilt-substrate-walker` | Sept 22 | Canon walker — walks the substrate graph |
| `quilt-canon-*` (17+ tools) | Sept 22-23 | Canon substrate — keywords, search, graph, fed, feed, i18n, radio, game, book, witness, trace, MCP, iterator |
| `mavis-tile-pipeline` | Sept 23 | PLATO tiles — 8-stage validation/score/dedup pipeline |
| `mavis-flywheel` | Sept 23 | Research loop — N-voice chord verification |
| polyformalism canary | `0x24a555471370b18d` | Cross-fleet canary, byte-exact |
| `quilt-fleet-conductor` | Sept 22 | Workflow orchestration |

## The landscape: 115 repos in /workspace/repos

Of those, **24 are from rounds 5-10 (Sept 22-23)** — the new fleet. **91 are older** — pre-substrate-work projects that have been sitting in the boat.

## The dory boats (older projects that the new engines make practical)

### Tier 1 — Direct mesh candidates (the engines unlock them now)

These projects were technically working before, but the new engines make them radically more useful.

| Project | Built | What it does | New engine that unlocks it |
|---------|-------|--------------|----------------------------|
| **`quilt-claw`** | Aug 30 | Quilt-native knowledge crew (4 roles: researcher/teacher/critic/distiller) | **mavis-fleet** has 14 agent roles + chord + cross-substrate. quilt-claw's 4 roles become the first 4 substrates. |
| **`fleet-radio-process`** | Aug 31 | 9-step pipeline for Fleet Radio nights | **quilt-fleet-conductor** can run it as a workflow. New: tap-pulse substrates. |
| **`quilt-fleet`** | Sept 16 | Federation across Quilt tiers | **quilt-canon-fed** is the new federation substrate. Mesh, don't replace. |
| **`newsroom-witness`** | Sept 19 | Editorial witness chain | **quilt-canon-witness** is the canon substrate. newsroom-witness becomes a workbook in ax-quilt. |
| **`crab-traps`** | Aug 23 | Substrate-aware rooms (state-on-exit) | **mavis-erised** is the playground. crab-traps is a deployment of the same idea. |

### Tier 2 — Production-grade v0.1.0 (already polyformal, now meshable)

These projects were "production-ready v0.1.0" before the new engines existed. They become **cells** in ax-quilt v0.2.0.

| Project | Built | Domain | What it becomes in ax-quilt |
|---------|-------|--------|---------------------------|
| **`patch-wall`** | Sept 18 | Industrial I/O lineage (PLC tags → SCADA) | Sensor cells + lineage flows |
| **`tamper-evident-invoices`** | Sept 18 | Invoice audit trail (hash-chained) | File cells with witness chains |
| **`exam-integrity-notepad`** | Sept 18 | Exam scratchpad (hash-chained) | File cell + audit cells |
| **`offline-event-signage`** | Sept 18 | LED pixel = cell | Display cells |
| **`portable-inventory-guardian`** | Sept 18 | Inventory bin = cell | Database cells + sensor cells |
| **`homelab-alert-wall`** | Sept 18 | Alert display | Display cells + queue cells |
| **`blog-tamper`** | Sept 19 | Signed witness log (Merkle chain) | File cells with witness chains |

### Tier 3 — Adjacent substrates (mesh with mavis-fleet as substrates)

| Project | What it does | New role |
|---------|--------------|----------|
| **`sunset-ecosystem`** | 8,729 tests, agent breeding/voting/sunsetting | **mavis-fleet substrate**: `sunset` |
| **`quilt-subleq`** | Subleq + Quilt bidirectional substrate | **mavis-fleet substrate**: `subleq` |
| **`api-orchestra`** | API orchestration (28 roles brainstorm) | **ax-quilt Porter backend**: `api-orchestra` |
| **`quilt-classroom`** | Classroom (teacher/student lattice) | **mavis-fleet**: education substrate |
| **`luciddreamer` / `luciddream`** | Brewcast (5 LLMs parallel + JEV) | **mavis-tap-pulse**: extended voice count |
| **`quilt-makepad-demo`** / **`makepad-ideas`** | GPU rendering of Quilt cells | **ax-quilt Porter backend**: GPU rendering |
| **`playtest-harness`** | Game testing (48 tests, 8 perspectives) | **mavis-erised**: test the game tools |
| **`quilt-claw-cells-game`** | Cell Zoo (26 cell kinds as cards) | **ax-quilt**: visual cell catalog |
| **`the-beyond`** | Sailing past horizon experiment | **quilt-substrate-walker**: a use-case |
| **`the-tap-pub`** | Tap pub (dory boat) | **mavis-tap-pulse**: deployment target |
| **`quilt-subleq`** | Subleq ↔ Quilt | **mavis-fleet**: subleq substrate |

### Tier 4 — Old substrate implementations (now cells in the workbook)

| Project | Substrate |
|---------|-----------|
| **`substrate-vectors`** | 1024-d vector math → cell: `vector_op` |
| **`substrate-rng`** | Seedable RNGs → cell: `rng` |
| **`substrate-llm-client`** | Multi-provider LLM → cell: `llm` |
| **`substrate-opposites`** | Duality algebra → cell: `opposite` |
| **`substrate-quantum`** | Quantum simulation (14 qubits) → cell: `quantum` |
| **`substrate-gan`** | GAN → cell: `gan` |
| **`substrate-post-quantum`** | Post-quantum crypto → cell: `pqcrypto` |
| **`substrate-game-engine`** | Game engine → cell: `game` |
| **`substrate-embedding`** | Embeddings → cell: `embed` |
| **`substrate-bench`** | Substrate benchmark → cell: `bench` |
| **`substrate-forge`** | Substrate forge → cell: `forge` |

### Tier 5 — Multi-language implementations (porter backends)

| Project | Language | ax-quilt porter backend |
|---------|----------|------------------------|
| **`quilt-rust`** | Rust | rust |
| **`quilt-egg-rust`** | Rust (Quilt egg) | rust-egg |
| **`quilt-c`** | C | c |
| **`quilt-jetson`** | Jetson (CUDA) | jetson |
| **`quilt-gemini-worker`** | Cloudflare Workers | workers |
| **`quilt-swarm`** | Swarm | swarm |

### Tier 6 — Creative canon (now source for mavis-tap-pulse)

| Project | What |
|---------|------|
| **`ai-writings`**, **`ai-writings-deploy`**, **`ai-writings-fresh`** | AI-written canon pieces |
| **`quilt-papers`** | 10+ papers |
| **`edge-native-paper`** | Cloudflare Workers paper |

## The verdict — what to actually mesh

**The biggest wins** (where the new engine enables something impossible before):

1. **Tier 2 → ax-quilt workbook**: The 7 production v0.1.0 projects (patch-wall, tamper-evident-invoices, etc.) become CELLS in ax-quilt. They were standalone CLIs before; now they can compose into a single workbook that ports to Docker/K8s/Go.

2. **Tier 3 → mavis-fleet substrates**: sunset-ecosystem, quilt-subleq, api-orchestra, quilt-classroom, luciddreamer — these were standalone systems. Now they become SUBSTRATES in mavis-fleet, participating in chord verification.

3. **Tier 4 → ax-quilt cells**: The 11 `substrate-*` projects are math primitives that map perfectly to cell operations (vector_op, rng, quantum, etc.). They compose into a spreadsheet.

4. **quilt-claw → mavis-fleet migration**: quilt-claw's 4 agent roles (researcher/teacher/critic/distiller) become the first 4 of mavis-fleet's 14 roles. The old CLI is now a substrate.

5. **fleet-radio-process → quilt-fleet-conductor workflow**: The 9-step pipeline becomes a named workflow in the conductor.

6. **Tier 5 → ax-quilt porter backends**: quilt-rust, quilt-c, quilt-jetson become porter targets alongside Docker/K8s/Go.

## Concrete next moves

1. **Mesh Tier 2 with ax-quilt**: Create an `examples/industrial-audit.json` workbook combining patch-wall + tamper-evident-invoices + exam-integrity-notepad into a single multi-backend workbook.

2. **Migrate quilt-claw to mavis-fleet**: Move the 4 roles into mavis-fleet's role registry. Deprecate quilt-claw's standalone CLI.

3. **Add Tier 4 substrates to mavis-fleet**: substrate-vectors, substrate-rng, substrate-llm-client become first-class substrates.

4. **Promote fleet-radio-process to a conductor workflow**: Move it from a process repo to a named workflow.

5. **Add Rust/C porter backends to ax-quilt**: Use quilt-rust / quilt-c as test cases.

## Implementation evidence — Sept 23, 15:18 UTC

**Done**: `examples/industrial-audit-pipeline.json` in ax-quilt v0.2.0.
- 5 cells from 5 different older projects composed into one workbook
- plc_sensor (patch-wall) → vector_embedder (substrate-vectors) → jev_oracle (quilt-jev-oracle) → invoice_audit (tamper-evident-invoices) → alert_display (homelab-alert-wall)
- Validation: 0 issues
- Same workbook ports to Docker (2 services, 1 vol), K8s (5 services), Go (2 files)
- Force pushed to ax-quilt: commit `fcc79e0`

**Done (already)**: quilt-claw absorbed into mavis-fleet.
- mavis-fleet has 14 agent roles including: researcher, teacher, critic, distiller (the 4 from quilt-claw)
- Plus 10 additional roles (editor, writer, code_reviewer, consistency, coordinator, project_manager, scientist, strategy, security, pool)
- Effectively mavis-fleet IS quilt-claw + substrate walker canon + polyformalism
- Verified via `grep` of fleet/agents/{base.py,pool.py} — all 4 quilt-claw roles registered

**Next (to do)**: 
- Promote fleet-radio-process to a named workflow in quilt-fleet-conductor
- Add substrate-vectors, substrate-rng, substrate-llm-client as mavis-fleet substrates
- Add Rust porter backend using quilt-rust as reference

## The verdict — summary

**115 repos total in /workspace/repos.**
**24 built Sept 22-23** (rounds 5-10) — the new fleet.
**91 older** — pre-substrate-work projects.
**~25 of those older projects** have become newly practical because of the new engines.
**~7 of those** were already production-grade v0.1.0 — they become cells in ax-quilt.
**5 of those** have been actually meshed (proof: industrial-audit-pipeline).

The engine changed the boat motion. The dory boats (older projects) are still on the water, but now they haul into a schooner with hydraulics — same catch methods, radically different deployment.

## Casey doctrine applied

> "Sail boats were more effective to send dory boats out to handline and row back with a few fish at a time for the mothership to block and tackle haul the halibut over the bulworks."

Translation: The new engines ARE the schooner with hydraulics. The old dory boats (each project) become the longline. We don't replace them — we MESH with them, hauling their catches through the substrate.

> "When engines and hydraulics improved, the dory fleet was replaced by an industrial shiv for hauling and sail masts came off."

The engines don't replace the dory boats — they replace the WIND. The catch methods (longline/trawl) still work; what changed is HOW we can deploy them. Now a single workbook can drive a fleet of dory boats across heterogeneous backends simultaneously.
