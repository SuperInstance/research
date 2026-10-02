# Comparison: cellforge vs quilt-ai vs substrate-gan vs substrate-llm-client

**Date**: Sept 23, 2026
**Context**: Scouted all `quilt-*`, `substrate-*`, and ML-adjacent repos to see what the other agent is building before I designed cellforge. Result: the "town and laborers" inversion Casey described isn't in any existing repo. cellforge is genuinely novel.

---

## TL;DR

| Repo | Substrate role | Solves | Cell kinds | Async? | Hot-swappable runtime? |
|---|---|---|---|---|---|
| **`quilt-ai`** | AI *inference* as reactive cells | "Call LLMs from Quilt sheets" | 8 (ai.llm, ai.embed, ai.image, ai.translate, ai.sentiment, ai.summarize, ai.code, ai.vision) | yes (per-cell async) | **No** — provider is fixed per cell |
| **`substrate-llm-client`** | LLM client lib with JEV gating | "Wrap multi-provider LLMs with confidence scores" | N/A (library, not cells) | yes | No |
| **`substrate-gan`** | GAN harness with JEV judge | "Generator→Judge loop, train on the kept" | N/A | yes | No |
| **`substrate-videogame-ml`** | ML for games (OpponentAI, NPCBehavior, ProceduralGen, ReplayLearner) | "ML primitives for game engines" | 4 (ad-hoc) | yes | No |
| **`substrate-embedding`** | Hash + mock-semantic embedders | "1024-dim BGE-compatible vectors without PyTorch" | N/A | no | No |
| **`cellforge`** (proposed) | ML *training* with cell matrix as permanent substrate, hot-swappable workers | "Train PyTorch/JAX/SSM/diffusion on a workbook that outlives the math" | 8 (WEIGHT, ACTIVATION, GRADIENT, TOKEN, INFLUENCE, WITNESS, DISPATCH, ZONE_BOUNDARY) | yes | **YES** — dispatcher cell hot-swaps PyTorch↔JAX↔CUDA↔custom |

**None of the existing tools do what Casey described: a permanent substrate that outlives any one ML training engine.**

---

## What `quilt-ai` does (the closest existing work)

`/workspace/repos/quilt-ai/` is a TypeScript package `@quilt/ai` with:

**4 built-in providers** (zai, kimi, deepseek, cloudflare) — all 4 are also in my Quilt toolchain.

**8 cell kinds**: ai.llm, ai.embed, ai.image, ai.translate, ai.sentiment, ai.summarize, ai.code, ai.vision.

**Engine features** (read from `engine.ts`):
- Caching by config hash (cache hit count tracked)
- Cost tracking per call (input/output tokens × $/1K)
- Fallback chain: zai → kimi → deepseek → cloudflare
- 6 worked YAML examples: basic LLM, fanout-3-models, RAG, agent-loop, cost-control, image-pipeline

**The killer insight of quilt-ai**: AI is a first-class cell kind, evaluated reactively with the rest of the sheet. When `question` changes, `answer` re-evaluates automatically. Same for `docs` → `matches` (vectorize.search) → `answer` (LLM with context).

**What it does NOT do**: train anything. It calls trained models. The training process is a black box that lives at the provider.

**What it does NOT have**:
- A persistent state matrix that survives model swap
- A grid where weights, activations, and gradients are first-class cells
- Hot-swappable execution backends
- A dispatcher that decides when a worker comes
- A witness chain that records every parameter update
- An INFLUENCE_CELL with TTL for human/agent nudges

---

## What `substrate-llm-client` does

Multi-provider LLM wrapper with **JEV confidence gating** (default 0.7) and **Pincher cache** (only caches responses above threshold).

```typescript
const result = await client.chat('deepinfra', messages);
// result.jev_conf in [0.65, 0.95], cached if high enough
```

**Strengths**: Provider-agnostic, confidence-gated, fallback-aware.
**Weakness**: Stateless, no notion of training or persistent state.

---

## What `substrate-gan` does

GAN harness where generator proposes → JEV (judge) scores → best kept → training_data grows.

```typescript
const gan = new Gan({ generator: new SubstrateGenerator(), judge: new SubstrateJudge() });
await gan.train(10, 'topic');
// metrics: { round, generated, kept, rejected, best_score, mean_score }
```

**Strengths**: This is actually the closest to "training" — there's a training_data list, history of metrics, threshold-based selection.
**Weakness**: All in TypeScript memory, no GPU dispatch, no worker swap, no substrate persistence.

---

## What `substrate-videogame-ml` does

- **OpponentAI**: learns player tendency, plays opposite. JEV confidence grows with observations.
- **NPCBehavior**: trait-driven actions, witness-log per NPC
- **ProceduralGen**: JEV-curated dice rolls for room generation
- **ReplayLearner**: learns from replay data, predicts wins/losses

**Strengths**: Game-domain ML with witness logs.
**Weakness**: Game-specific, not a general training substrate.

---

## What `cellforge` will do (and why it's different)

The inversion Casey articulated:

> **To build a training system that feels as permanent and recognizable as a university town while the underlying infrastructure shifts beneath it, you must invert the relationship between state and execution. The Quilt cell matrix must be the permanent destination, and the low-level mathematical engines must be treated as disposable, hot-swappable utility workers.**

This means:

| Concern | Traditional (PyTorch Lightning, Ray Train) | cellforge |
|---|---|---|
| Where does state live? | GPU memory + checkpoints on disk | **Cell matrix (workbook) — always** |
| Who decides training step timing? | External scheduler (`Trainer.fit()`) | **DISPATCHER_CELL — first-class cell** |
| How do you change ML backend? | Rewrite training script | **Hot-swap via dispatcher contract** |
| How do you revert to a prior state? | Restore checkpoint from disk | **Truncate ledger to `witness_cell[N]`** |
| How do you inject human guidance? | External callback, often bypassed | **INFLUENCE_CELL with TTL** |
| How do you prove correctness across backends? | Cross-framework numerical test | **Multi-worker polyformality (Jaccard on N-rings)** |

**This is a different problem space from anything `quilt-ai` solves.**

`quilt-ai` answers: "How do I call an LLM from a Quilt sheet?"
`cellforge` answers: "How do I train an ML model on a Quilt sheet that outlives any one training framework?"

They share the cellular substrate, but solve orthogonal problems.

---

## 3 places cellforge can do BETTER than the other agent's work

### 1. State outlives engine (vs quilt-ai's transient calls)

**quilt-ai** evaluates an `ai.llm` cell — result lives in that cell until the next input change. The state IS the engine output. Swap zai → kimi and the cell's prior value is lost.

**cellforge** keeps a full_ledger of every WEIGHT_CELL value across time. Swap PyTorch → JAX and the weights are still in the grid. The dispatcher just changes which worker reads/writes them.

**Why this matters**: Model checkpoints are state. The dispatcher is a worker manager. State and worker are different concerns and should be different kinds of cells.

### 2. Dispatcher is a cell (vs substrate-gan's external `train()` loop)

**substrate-gan** has `gan.train(iterations, prompt)` — an external method on a class. The training loop is in code.

**cellforge** has a `DISPATCH_CELL` that owns worker lifecycle. The dispatcher IS a cell with its own orientation, and it can be reasoned about, witness-logged, even swapped out.

**Why this matters**: You can write a cell that watches the dispatcher, audits it, replaces it. You can write a cell that the dispatcher delegates to. The whole training system is a sheet of cells. There is no training script.

### 3. INFLUENCE_CELL with TTL (vs nothing comparable)

**None of the existing tools** have a first-class cell kind for "this human/agent guidance applies from tick T1 to tick T2."

In PyTorch Lightning you'd hack it with callbacks. In Ray Train you'd add a sidecar queue. In substrate-gan there's no notion.

**cellforge** has `INFLUENCE_CELL { tick, valid_until_tick, source, payload, strength }`. The dispatcher checks `valid_until_tick` at every tick. Expired nudges are silently ignored.

**Why this matters**: RLHF, curriculum learning, teacher-student distillation, human steering — all become `INFLUENCE_CELL` writes. The dispatcher sees them the same way it sees weights. Same machinery.

---

## What cellforge can learn from quilt-ai

Don't reinvent:
- **Caching by config hash** — apply to dispatcher decisions (same op manifest → same worker)
- **Cost tracking** — every worker step has cost (GPU-hours, $); log to a WITNESS_CELL variant
- **Fallback chain** — dispatcher has primary/secondary/tertiary workers; on witness violation, try next
- **Fan-out examples** — `02-fanout-3models.yaml` is the pattern for `multi_worker_polyformality()`; 3 workers on same cell block, take agreement

What cellforge ADDS that quilt-ai can't:
- **State persistence across worker swap**
- **Dispatcher as a cell (first-class)**
- **Witness chain on every parameter update**
- **INFLUENCE_CELL with TTL**
- **REWARD_CELL (planned) for RL training**
- **ZONE topology (Fast Reflex / Slow Critic / Nudge Foundry)**

---

## Naming note (Casey's doctrine)

- **`quilt-ai`** is correctly named — `quilt` family + `ai` purpose → zero-shot intuitive.
- **`substrate-gan`**, **`substrate-llm-client`**, **`substrate-videogame-ml`** are also correctly named — `substrate` family + `purpose`.
- **`cellforge`** follows the same convention: `cell` (substrate) + `forge` (training happens here) → zero-shot intuitive.
- `mavis-cellforge` would be wrong — the `mavis-` prefix is for persona artifacts only (mavis-fleet, mavis-tfm).

Production repo naming: **`cellforge`** at `https://github.com/SuperInstance/cellforge` (when built).

---

## Next: Cellforge L1 build (when Casey gives go-ahead)

**L1 scope** (the smallest cellforge that does anything useful):
- 1 cell block (single WEIGHT_CELL + ACTIVATION_CELL pair)
- 1 DISPATCH_CELL that owns worker lifecycle
- 1 PyTorch worker (mock: linear regression on synthetic data)
- 1 contract: `WorkerContract { name, dtype_policy, capabilities, hot_swap_cost }`
- 1 INFLUENCE_CELL with TTL (write a nudge, see it applied)
- 1 WITNESS_CELL (every parameter update is witnessed)
- 1 REWIND: truncate ledger to witness_cell[N]
- CLI: `cellforge init`, `cellforge step`, `cellforge rewind N`, `cellforge swap worker`
- Tests: ~15 (worker spawn, swap, rewind, TTL, witness chain, polyformality)

That's enough to PROVE the inversion: the workbook survives even if I rip out the PyTorch worker and replace it with a JAX worker. The state is in the grid, not the worker.

---

## Files

- `/workspace/research/cellforge-ideation/CELLFORGE_ZONES_SPATIAL.md` — spatial design
- `/workspace/research/cellforge-ideation/CELLFORGE_CONTRACT_PROTOCOL.md` — contract schema
- `/workspace/research/cellforge-ideation/COMPARISON_QUILT_AI.md` — this file

**Status**: Ideation complete. L1 build waiting on Casey go-ahead.
