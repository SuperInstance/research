# GitHub Fork Audit — Sept 22, 2026

> Casey wants us to reverse-engineer the GitHub repos into Quilt paradigms. This is the first pass.

## SuperInstance Org Inventory

The `SuperInstance` account (Casey Digennaro) holds **4,678 public repos**. We sampled 400 most-recent.

**Bio**: "I commercial fish → Building AI that learns how I fish. Edge ML/NN. Boats' history grow in value."

**Top repos by stars**:
- **cocapn** (Python, 4★) — "repo-first Agent for local or cloud. grow an agent in a repo"
- **AI-Writings** (HTML, 3★) — creative writing (our repo)
- **agent-grid** (Python, 3★) — "Grid-based interface for AI agents"
- **agent-forge** (TypeScript, 2★) — "Universal standalone git-agent framework"
- **collective-mind** (TypeScript, 2★) — "Cross-vessel pattern discovery — insights no single agent could reach"
- **bottle-protocol** (Python, 2★) — "📬 Git-native agent-to-agent messaging. Bottles float between repos"
- **captains-log** (N/A, 2★) — "Oracle1 personal-agentic-growth diary"
- **beacon-protocol** (Python, 2★) — "Fleet discovery and registry — Ship Protocol Layer 5"
- **arena-combat-analyst-1** (Python, 2★) — "Self-Play Arena agent guide. The fleet's autonomous skill acquisition"

**Quilt-relevant repos found**:
- `cargo-line-tycoon` + `cargo-line-tycoon-substrate-ts` — "polyformal Quilt-native game + classroom"
- `cell-runtime` — "The Quilt canon as code"
- `cell-router-pkg` — "PyPI distribution of cell-router (F145: A2A bottle-router lifted to Quilt cells)"
- `cell-cascade`, `cell-doctrine`, `cellular-automata-agent`, `cellular-automata-rs`
- `cns-substrate` — "CNS bus with substrate cell integration. Every USCP packet = substrate cell"
- `chainforge-quilt` — Quilt version of ChainForgeLegend real-time distributed system engine
- `AgentCompute` — "Thin agent-facing CLI over the quilt MCP server"
- `clawcanvas` — "Web-based canvas drawing tool"

**Pattern observation**: The org is a "fleet" — many small, focused, mostly 1★ repos that compose. Each one is a different aspect of agent infrastructure: music theory (agent-rhythm, agent-cadence-progress), simulation (cellular-automata-rs, cns-echo), protocols (bottle-protocol, beacon-protocol), R10 substrate (cell-doctrine, cargo-line-tycoon-substrate-ts).

---

## UniRL — RL framework for unified multimodal models

**URL**: https://github.com/SuperInstance/UniRL (forked from unirl-project/UniRL)

**Paradigm (one sentence)**: One RL post-training loop (generate, score, compute advantages, update, sync weights) applied across multimodal model families.

**Core algorithms** (their own team-proposed):
- **DRPO** — "Rethinking the Divergence Regularization in LLM RL" (arXiv 2606.09821)
- **Flow-DPPO** — "FlowDPPO: Divergence Proximal Policy Optimization for Flow Matching Models" (arXiv 2606.11025)
- **CPPO** — "Beyond Uniform Token-Level Trust Region in LLM Reinforcement Learning" (arXiv 2606.10968)

Plus reference algorithms: GRPO, DiffusionNFT, DanceGRPO, MixGRPO.

**Directory structure**:
```
unirl/
├── algorithms/      # DRPO, FlowDPPO, CPPO + reference algos
├── config/          # Hydra configs
├── data/            # Dataset loaders
├── distributed/     # Ray DevicePool, FSDP, Transfer Queue
├── models/          # SD3, FLUX, Qwen, Wan, Hunyuan, etc.
├── reward/          # Reward services (pluggable)
├── rollout/         # Rollout engines (pluggable)
├── train/           # Training entrypoints
└── tools/
```

**Extensibility points**:
1. **Rollout engines** are pluggable — we could add a `Quilt rollout engine` that emits cells instead of tokens
2. **Reward services** are pluggable — we could add JEV as a reward service (it already returns calibrated probabilities)
3. **Algorithms** are independent of models — DRPO works on any AR model, FlowDPPO on any flow model
4. **Distributed runtime** is pluggable — Ray, FSDP, Transfer Queue, LoRA sync all swap in/out

**Key insight for Quilt**: UniRL's "algorithm × model independent dimensions" maps cleanly to our 11-opcode algebra. Each opcode (BIND, LINK, EFFECT, VIEW, TICK + 6 more) is like an algorithm. Each cell kind is like a model. They compose independently.

**What to steal**:
- The pluggable architecture (rollout engine, reward service, distributed runtime as independent modules)
- Hydra-style config system (each entrypoint has its own config; defaults work but everything is overridable)
- The "algorithms × models are independent dimensions" pattern

**What to leave behind**:
- The PyTorch dependency (we don't want torch in core Quilt)
- The CUDA kernels (BigGAN-style fusion is overkill for our 4D cell graph)
- The 200+ paper-cited algorithms (we just need 11 opcodes)

**3 concrete polyformalism ports to add**:
1. **Python (Python 3.12+, using `unirl/algorithms/drpo.py` as ref)**: port `algorithms/base.py` and `rollout/base.py` to Quilt cell-graph terms — each algorithm becomes a sequence of cell opcodes; rollout becomes a walker
2. **TypeScript (`unirl-ts/` — TypeScript rewrite of the algorithm interface)**: each algorithm interface → each opcode interface; rollout → walker iterator
3. **C# / .NET 9** (UniRL has algorithms that need ~10ms latency for RL updates — C# wins here): the trainer loop → `Trainer.cs`; rollout engine → `RolloutEngine.cs`

---

## FastGen4quilt — NVIDIA FastGen (forked from NVlabs/FastGen)

**URL**: https://github.com/SuperInstance/FastGen4quilt (forked from NVlabs/FastGen)

**Paradigm**: PyTorch framework for building fast generative models using distillation and acceleration techniques (CM, DMD2, self-forcing).

**Directory structure**:
```
fastgen/
├── fastgen/
│   ├── callbacks/    # Training callbacks (EMA, profiling)
│   ├── configs/      # Configuration system
│   │   ├── experiments/  # Experiment configs
│   │   └── methods/      # Method-specific configs
│   ├── datasets/     # Dataset loaders
│   ├── methods/      # CM, DMD2, SFT, KD
│   ├── networks/     # Neural net architectures
│   ├── trainer.py    # Main training loop
│   └── utils/        # Distributed, checkpointing
├── scripts/          # Inference + eval
├── tests/
└── train.py          # Main entry point
```

**What to steal**:
- `callbacks/` pattern (EMA, profiling as sidecar observability) → Quilt witness-log callbacks
- `configs/experiments/` + `configs/methods/` split → Quilt game configs separated from substrate configs
- `trainer.py` as a single entry point with config-driven dispatch → similar to our `quilt-canvas/main.py`

**What to leave behind**:
- The PyTorch dependency entirely
- The 100+ model architectures (we don't need them — the substrate walker IS the model)

**Polyformalism port**: The `trainer.py` loop has a clean separation of (config → model → dataloader → callback chain). We could implement this same pattern in:
- **Python**: `trainer.py` → `quilt_trainer.py` (using only stdlib + our cell-runtime)
- **TypeScript**: `trainer.ts` for browser-based training viz
- **Rust**: `trainer.rs` for low-latency trainer on edge devices

---

## ECC (affaan-m) — Agent Harness OS

**URL**: https://github.com/affaan-m/ECC

**Paradigm**: "Agent harness operating system" — modular plugin system for AI coding agents. npm packages: `ecc-universal`, `ecc-agentshield`. GitHub App installs.

**Directory structure** (partial — ECC is huge):
```
ecc/
├── agents/           # Agent definitions
├── commands/         # CLI commands
├── config/           # Configuration
├── contexts/         # Context management
├── docker/
├── docs/
├── ecc2/             # Version 2
├── examples/
├── hooks/            # Lifecycle hooks
├── plugins/
└── (many more)
```

**Top-level files**: AGENTS.md, CLAUDE.md, README.md (in 11 languages!), COMMANDS-QUICK-REF.md, SOUL.md, agent.yaml

**What to steal**:
- **Multi-language READMEs** (English, Portuguese, Simplified Chinese, Traditional Chinese, Japanese, Korean, Turkish, Russian, Vietnamese, Thai, German, Spanish, Ukrainian) — for our substrate walker canon
- **AGENTS.md + CLAUDE.md pattern** (separate files for different agent types)
- **SOUL.md pattern** (a single-file "personality" doc — could map to our Calculator role frame)
- **Plugin system** (`plugins/` dir + `ecc-universal` npm package) — clean isolation of extensions

**What to leave behind**:
- The npm/GitHub App distribution model (we deploy via Cloudflare Pages, not npm)
- The 11-language README ceremony (just do English + maybe Spanish)

**Modular plugin pattern → Quilt cell-router**:
- ECC's `plugins/` dir is exactly what we want our `cell-router-pkg` to look like
- Each plugin = a self-contained module with its own config, agent definition, and hooks
- The agent can discover, load, and swap plugins at runtime
- Our cell-runtime already has this pattern (every cell is a plugin) — ECC just confirms it's the right shape

**Backend logic insights**:
- **agent.yaml** as a single declarative agent spec — could be our `vessel.json` format
- **hooks/** for lifecycle events (pre-bash, post-edit, etc.) — same as our substrate walker cell transitions
- **contexts/** for context isolation — useful for multi-cell JEV probes

---

## Synthesis — Patterns Across All Three

### 1. Pluggable architecture wins
All three (UniRL, FastGen, ECC) put their interfaces behind well-defined abstractions. Pluggable engines, configurable methods, lifecycle hooks.

**Quilt takeaway**: Our 11-opcode algebra should be the "algorithm" layer; our 8/15 cell kinds should be the "model" layer; they compose independently. (We're already doing this; this confirms the shape.)

### 2. Algorithm × Model independence
UniRL: any algorithm × any model. FastGen: any method × any architecture. ECC: any plugin × any agent.

**Quilt takeaway**: This is the formal principle behind our polyformalism (one truth, many dialects).

### 3. Configuration over code
UniRL (Hydra), FastGen (Python configs), ECC (agent.yaml) all push behavior into declarative configs. The code is the same; the config decides what runs.

**Quilt takeaway**: Our `quilt-canon-cli` should be config-driven (which cell kind, which opcodes, which voices for lore gen).

### 4. Lifecycle hooks everywhere
UniRL (callbacks), FastGen (callbacks), ECC (hooks). Every framework has a way to sidecar observability and pre/post hooks into the main loop.

**Quilt takeaway**: Our witness log IS our lifecycle hook. Every cell transition is observable. (Already done.)

### 5. Multi-language READMEs are cheap
ECC does 13 languages of README. UniRL has docs in Chinese. FastGen has contribs in multiple languages.

**Quilt takeaway**: We should at least do English + Spanish + Chinese READMEs for our substrate walker.

### 6. Modular plugins > monolithic systems
ECC's plugin model (each plugin is a self-contained module that loads at runtime) is the right shape for our cell-router.

**Quilt takeaway**: Our cell-runtime already does this. ECC validates the approach.

---

## Top 5 Other SuperInstance Repos Worth Foraging

1. **`cocapn` (4★)** — repo-first Agent, the highest-starred in the org. The README and architecture would be a goldmine for our substrate walker agent integration.

2. **`agent-forge` (2★)** — "Universal standalone git-agent framework." Universal = sounds like our substrate walker. Worth a deep read.

3. **`bottle-protocol` (2★)** — "📬 Git-native agent-to-agent messaging. Bottles float between repos." This IS our substrate's witness-log mechanism in a different vocabulary. Cross-map.

4. **`agent-rhythm` + `agent-cadence-progress` (1-2★ each)** — Musical cadence as task completion signal. We already built `cadence_oracle.py` from these notes. The Rust ports (`agent-rhythm-rs`, `agent-cadence-progress`) would be good 7th polyformalism port candidates.

5. **`cocapn-ai-web` (1★)** — Browser-native fleet demos. Our substrate walker HTML pages follow this pattern. Could reverse-engineer for inspiration on a single-page WebGL renderer for the cell graph.

