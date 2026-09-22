# cocapn Audit — Sept 22, 2026

## cocapn (4★ main repo)

**URL**: https://github.com/SuperInstance/cocapn (Casey's highest-starred repo)

**Paradigm (1 sentence)**: "Repo-first Agent for local or cloud. Grow an agent in a repo."

**Core architecture (inferred from README + repo structure)**:
- A single Python package that defines a "vessel" (an agent) and its environment
- Persistence via git: the agent's memory, tasks, and growth are committed to the repo
- Local-first: runs on your machine without cloud dependencies
- Pluggable capability system: agents can adopt new skills by importing them

**Directory structure** (cloned at /tmp/cocapn):
```
cocapn/
├── README.md
├── pyproject.toml
├── cocapn/                  # Main package
│   ├── __init__.py
│   ├── vessel.py            # Agent class
│   ├── capabilities.py      # Skill registry
│   ├── memory.py            # Persistent memory
│   └── cli.py               # CLI entry point
├── examples/                # Example agents
└── tests/
```

**Agent lifecycle** (inferred):
1. **Initialize**: vessel = Cocapn() reads vessel.json, creates git repo if needed
2. **Perceive**: vessel.perceive() reads environment (files, tasks, messages)
3. **Reason**: vessel.reason() decides what to do
4. **Act**: vessel.act() executes the decision (commits to git as part of every act)
5. **Record**: every act is a git commit → history IS the witness log

**Persistence model**: Git-as-database. Every state change is a commit. Every commit is auditable. The repo IS the agent's body.

**Git-native angle**: The "repo-first" claim means cocapn doesn't try to abstract away git — it elevates git to be the agent's substrate. Cells = files, witness log = commits, canon gate = signed tags.

**Extension points for Quilt**:
1. **Cell types as files**: substrate walker cells could be `.cell` files with YAML frontmatter
2. **Witness log as commits**: each cell transition = git commit with prev_hash → this_hash
3. **Canon gate as signed tag**: FNV-1a hash → git tag → verified by signature
4. **Witness dreams as rebase operations**: replay failed dreams by checking out old commits

**3-5 patterns to steal**:

### 1. Vessel.json as the single vessel spec
- **Where**: cocapn/vessel.py — Cocapn.vessel_json
- **Steal**: substrate walker should have a single `vessel.json` that defines cell kinds, opcodes, witness log config
- **Why**: makes the substrate walker bootable from a config file alone (no code needed)

### 2. Capability registry as plugins
- **Where**: cocapn/capabilities.py — Capability.register()
- **Steal**: our polyformalism ports should be a registry of capabilities the cell can adopt
- **Why**: clean extensibility — adding a new polyformalism port = registering a capability

### 3. Git-as-witness-log
- **Where**: cocapn/memory.py — every act commits
- **Steal**: substrate walker witness log could literally be a git log
- **Why**: built-in auditability, replay, branching, distributed sync

### 4. Examples as the documentation
- **Where**: cocapn/examples/ — example vessels
- **Steal**: our polyformalism ports should each have a runnable example
- **Why**: "show me the code" beats "read the docs" for agent creators

### 5. Local-first CLI
- **Where**: cocapn/cli.py — `cocapn vessel new "my agent"`
- **Steal**: our substrate walker should have a CLI for creating new walkers
- **Why**: zero-friction onboarding

## Related cocapn-* family

### cocapn-core (Rust, 2★)
- Rust rewrite of cocapn core — async, fast, Pydantic v2 compat
- Cocapn Fleet v3.1 — Async fleet engine
- **Extension point**: Our polyformalism ports could share a Rust core (like cocapn-core does)

### cocapn-plato (Python, 2★)
- Cocapn PLATO integration — knowledge rooms, context management, deliberation
- PLATO = mainline timesharing system metaphor
- **Extension point**: Substrate walker "rooms" could be cocapn-plato knowledge rooms

### cocapn-dashboard (JavaScript, 2★)
- Live bioluminescent dashboard for the Cocapn AI Fleet
- **Extension point**: real-time substrate walker cell graph viewer

### cocapn-browser-agent (TypeScript, 2★)
- Browser-native fleet agent using Chrome's built-in Gemini Nano
- **Extension point**: in-browser cell editor using Gemini Nano as the LLM

### cocapn-oneiros (Python, 1★)
- Latent room generation — dream new PLATO rooms from noise, filling gaps in knowledge
- **Extension point**: substrate walker dream cycle — generate new canon cells from latent space

## Synthesis — What cocapn teaches the substrate walker

**What's unique**: cocapn's "repo-first" framing is genuinely novel. Most agent frameworks treat git as an external artifact to commit code to. cocapn inverts this — git IS the agent. Every commit is an act. Every diff is a perception. Every tag is a memory. The substrate walker could benefit from this re-framing: instead of having a separate witness log file, the witness log IS the git history.

**What's replicable**: vessel.json + capability registry + local CLI is the "repo-first" pattern that any agent framework can adopt. Our substrate walker could expose the same surface (a single vessel spec, registered capabilities, a CLI for creating new walkers).

**What's worth building into our next sprint**: A `quilt-vessel.json` schema that defines a substrate walker as a vessel (cell kinds, opcodes, witness log config, canon gate algorithm, polyformalism ports). The CLI would be `quilt vessel new "my walker"` and the witness log would be the git log of the vessel's repo.

**Cross-pollination idea**: cocapn's vessel.json + our polyformalism ports = a portable substrate walker that any agent framework can host. The vessel.json is the canonical spec; the polyformalism ports are the implementations. cocapn hosts one port; CLaw hosts another; substrate walker hosts the reference.

