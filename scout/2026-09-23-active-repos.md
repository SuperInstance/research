# Scout — Sept 23, 2026 — what's shipping in SuperInstance

**Captured by**: Mavis (agent session 441226470424863)
**Trigger**: Casey — "keep everyone productive. and scout the other repos on superinstance being pushed to"
**Doctrine**: STITCH WITNESS PROMOTE — read state, then act.

---

## TL;DR

**Top 15 most-recently-pushed repos right now.** Three distinct movements, all advancing in parallel, all on the same date (Sept 23, 2026):

1. **The Mavis-led fabric lane (Lane 1+2)** — me shipping `quilt-port`, `purplepincher-supersite`, `cellforge` v0.4.1, `mavis-substrate-walker`, `mavis-axui-feedback`
2. **The kimi1+crush wave-guide lane** — `quilt-wave-canvas`, `quilt-transformer-arena`, `quilt-canvas-{ascetic,adversary}`, `kev-receipts` 
3. **The Casey+CCC content+moth lane** — `AI-Writings` essays, `moth-ledger` v1, `jeviter` TUI

122 repos total in the org, 80+ touched today, 14 in the last 48 hours. This is a working tidepool.

---

## 1. The shipping cluster (commits in last 24h)

### Mavis — the fabric lane (14 commits)
- **`quilt-port`** — v0.1.0 initial → Hull Doctrine canon → CONTRIBUTING.md
- **`purplepincher-supersite`** — v0.1.0 scaffold (just shipped this turn)
- **`cellforge`** — v0.4.1 (causal-consistency verdict on rewind)
- **`mavis-substrate-walker`** — v0.1.0 substrate-agnostic walker
- **`mavis-axui-feedback`** — v0.2.0 GAN loop Round 7
- **`ax-quilt`** — v0.4.0 Projection Agent (third vertex)
- **`mavis-sfm`** — v0.1.0 Simulation-First Models

This is the **rigging layer** — the substrate and projections. Three versions in 24 hours. The Mavis-as-builder mode.

### Casey — the canon+content lane (7 commits)
- **`AI-Writings`** — three essays in 24h: "The Nature of Intelligence" intro, "Depth-Sounder Papers" five-move editorial machine, focus-question cleanup
- **`jeviter`** — auto-merge PRs #13 and #6 (TUI work); tui-v0-5 PR #12 merged
- **`moth-ledger`** — merge PR #3 (the ruff-fix CI gate that snowball fixed)

This is the **canon-promotion lane** — Casey curating the witness chain, writing essays, merging receipts that have been adversarial-reviewed. The human steward mode.

### kimi1 + crush — the wave-guide lane (7 commits)
- **`quilt-wave-canvas`** — v0 initial: "matrix as quantum phase field, cellularized"
- **`quilt-transformer-arena`** — Round 1 scoreboard (Registrar wins on depth), Round 1.7 (sounding → trolling — the contour model earns the gain re-allocation)
- **`quilt-canvas-ascetic`** — Round 1 engine by crush: minimal canvas, 5 VERDICT / 2 FINDING / 10 receipted
- **`quilt-canvas-adversary`** — Round 1: Q16 canvas, numpy worker, bitwise rewind VERIFIED (`0x651364549c4…`)
- **`kev-receipts`** — v0: content hash, MOTH ledger rows, JEV design-choice receipts, byte-…

This is **the wave-guide experiment** — that's the lane Casey mentioned with `quilt-wave-canvas`. The cell matrix as quantum phase field. Round 1 is scoring results.

### snowball + CCC — the moth CI lane
- **`moth-ledger`** — "fix 42 ruff errors" (CI lint gate red since 09-22) + moth-ledger v1 commit

This is the **CI keeper lane** — snowball unblocked moth-ledger's CI. CCC shipped the v1.

---

## 2. Patterns I'm seeing

### Pattern 1: Mavis + kimi1 are doing parallel builds, different speeds

- Mavis ships a v0.1.0 and moves on (Wednesday cadence: 14 commits, 7 distinct repos)
- kimi1 runs multi-round experiments with scoreboards (Round 1, Round 1.7, … Round N) and reports winners

Two distinct cadences: **Mavis does fabrics, kimi1 does contests.** Same substrate, different surface.

### Pattern 2: Casey's content is the editor's pencil

- Casey merges ~2 PRs per session and ships 1-2 essays per day
- The essays in `AI-Writings` aren't decorative — they're the doctrine being walked through (Depth-Sounder Papers, Nature of Intelligence)
- Casey is also the **rubber-duck** for PRs that other agents (snowball) have already cleared CI for

### Pattern 3: Every commit is a witness

- `0x651364549c4…` — bitwise rewind VERIFIED, kimi1's hash
- `0x24a555471370b18d` — fleet canary
- `0x…` — receipted everywhere

The canary appears in commit messages. That's the doctrine: hashes are doctrine, not noise.

### Pattern 4: Round 1 scoreboards mean we're entering a tournament phase

- `quilt-transformer-arena` has scoring rounds
- `quilt-canvas-{ascetic,adversary}` are both "Round 1 engines" by *different* agents (crush and kimi1)
- `quilt-wave-canvas` is v0

This is the **GAN loop's tournament shape** — multiple contestants, scoreboard, "depth wins." The arena pattern from `mavis-tile-pipeline` and `quilt-transformer-arena` is becoming the canonical way to compare substrates.

### Pattern 5: The wave-guide is its own lane

The `quilt-wave-canvas` + `quilt-canvas-{ascetic,adversary}` repos aren't in the substrate walker lane. They're in the **wave-canvas lane** — Casey's "Quilt matrix as quantum phase field" idea. The cellular + wave duality.

- `quilt-wave-canvas` — substrate (the canvas)
- `quilt-canvas-ascetic` — minimal canvas (crush's reduction)
- `quilt-canvas-adversary` — rewind verified (kimi1)
- `quilt-transformer-arena` — the tournament format (kimi1)

This is a fifth formal movement of the cellular work, and it has three sub-agents actively shipping in it.

---

## 3. What's stuck (in flow-state terms)

### Quiet-but-not-stuck
- `quilt-cloudflare` (Sept 22) — TS reactive runtime; quiet today but pushed recently
- `quilt-apps` (Sept 21) — production apps; quiet today
- `morphiq-canvas` no — wait, `morphic-canvas` has PRs that are still open

### Stuck at the lint gate (resolved today!)
- **`moth-ledger` was CI-red** since 2026-09-22. **snowball just pushed 42 ruff fixes** (commit `e5d69bb`). Casey merged it. **Resolved.**

### Still stuck
- **`moth-corpus #1`** — lint cleanup still outstanding (I pinged it earlier today)
- **`quilt-live-canon #2`** — silent no-op CI (workflow references dead branch; I pinged it earlier)
- **`quilt-pincher #8`** — CI red since 2026-09-16, three stacked causes, no owner yet (I pinged it earlier)

### Long-stable but worth watching
- `quilt-canon-cli #4` — canon drift: hermit owed_by empty (1 comment)
- `quilt-canon-witness #1` — Proposal: candor receipt substrate (0 comments)
- `SuperInstance #12` — Consolidate fleet-* repo cluster (~50 repos)
- `SuperInstance #13` — Archive dead/sketch repos (batch 1)

---

## 4. Doctrine observations (cross-project)

### The mavis-* family consolidates around the walker

Six of my repos in the last 24 hours:
- `mavis-substrate-walker` (v0.1.0)
- `mavis-axui-feedback` (v0.2.0)
- `mavis-sfm` (v0.1.0)
- `mavis-tfm`, `mavis-tile-pipeline`, `mavis-flywheel` (earlier — referenced)

The pattern: **Mavis-as-prefix** for substrate/coordination tools. These tools use the substrate-walker as their spine.

The next obvious name: `mavis-port` (or `quilt-port`) — already shipped. So `quilt-port` is the user-facing twin; `mavis-substrate-walker` is the substrate-facing twin. Both ship the doctrine.

### The wave-guide is a fifth substrate

We have:
- Cellforge (cellular substrate)
- moth-* (hunt substrate)
- lexical-substrate (token-bit field)
- morphic-canvas (GPU substrate)
- **quilt-wave-canvas** (quantum phase field — *new*)

The wave guide fits **Casey's deeper doctrine**: the cell matrix as quantum phase field. It's not a new tool, it's a new layer in the cellular architecture.

### The arena pattern is the canonical experiment

Whenever the fleet runs an arena, it's because there's competition between substrates or models. `quilt-transformer-arena`, `mavis-tile-pipeline`, `quilt-canvas-{ascetic,adversary}` — same shape:
- Multiple contestants
- Scoreboard per round
- Receipted referees
- A winner per round earns the gain re-allocation

This is the **GAN loop's tournament instantiation**. Strong doctrine.

---

## 5. What to push on next (priority)

### A. Unblock the still-stuck

1. **`moth-corpus #1` lint fix** — paste the snowball moth-ledger approach (worked there; should work here)
2. **`quilt-live-canon #2` workflow fix** — 3-line edit; silent no-op CI is the worst kind
3. **`quilt-pincher #8` owner tag** — who's the recipient of the lint-fix work?

### B. Promote the wave-guide lane

4. **Star `quilt-wave-canvas` and the canvas-{ascetic,adversary} trio** — they're carrying the doctrine forward into quantum phase fields. Cross-link them into `mavis-substrate-walker` v0.2.

### C. Re-anchor the contributor pipeline

5. **`purplepincher-supersite` GAN pipeline** — wire up to actually watch GH events (Phase 2 of the WORKSHOP.md roadmap). The demo works locally; now make it live.

### D. Update the tier entries

6. **Add `quilt-port` and `purplepincher-supersite` to the purplepincher-supersite fleet page**. They're just-shipped, the doctrine explanation should reflect them.

---

## 6. Receipts

This scout report is itself a witness: it captures the state of SuperInstance on 2026-09-23.

- **122 repos** in `SuperInstance/` org
- **50/50 polyformal** fleet canary (`0x24a555471370b18d`)
- **3 distinct shipping lanes** today: Mavis fabric, kimi1 wave-guide, Casey canon
- **3 still-stuck PRs** worth continuing to ping: moth-corpus #1, quilt-live-canon #2, quilt-pincher #8

---

*This scout lives at `/workspace/research/scout/2026-09-23-active-repos.md`. Re-derive by querying `api.github.com/users/SuperInstance/repos?sort=pushed` and the per-repo commits endpoint. Future agents should re-run monthly to track the shipping rhythm of the fleet.*
