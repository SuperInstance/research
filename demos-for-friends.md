# Working Demos & Gamified Sites — Verified Live

**Date: 2026-09-14 · Scout result**

Yes — there's a whole playground. Here are the verified-live URLs,
ranked by friend-friendliness (browser, no install, no jargon):

## Tier 1 — The "send this first" demos

### 🏆 Quilt Playground (the gamified one you were thinking of)
**https://superinstance.dev/quilt-ide-playground.html**
*"🎮 Quilt Playground — Gamified Cell Sandbox"*
- 4 modes: **Sandbox** / **Quest** / **Chaos** / **Watch**
- HP / XP / Mana / gold stat bars (it really is gamey)
- 7 biomes (different cell colors per biome)
- Click a cell to select. Shift+Click two cells to connect.
- Drag cells, place them, watch the graph live.
- **This is the answer for a non-technical friend.** They click, they play, they don't need a manual.

### quilt-scratch (cells you can watch think)
**https://fleet-static-host.casey-digennaro.workers.dev/quilt/**
*"🧵 quilt-scratch — wire tiles · watch numbers · that's the program"*
- Has **play / pause / step** buttons — single-step every cell.
- 3 scenes: **the room** (arrows fly a ship, space fires), **the deep caverns** (arrows walk, board the lift), **the fabric** (drag cards, wire output→input).
- Click any cell face to inspect. Drag actors to move them.
- Save/load fabrics as JSON.
- Contract tests link in the corner.
- **Best for the friend who's curious but not a gamer.** Click play, watch what happens, ask "why?"

### MIST — Tale of a Sheepdog Puppy
**https://fleet-static-host.casey-digennaro.workers.dev/mist/**
*"An interactive game that teaches kids how machines learn."*
- Built with Next.js, polished UI (🐕 loading screen, woodblock logotype).
- Teaches AI concepts through play — puppy in a meadow, exploring.
- **For a friend with kids, or the kid in any adult.** This is the gentlest entry point.

### Scrapcraft (live game with cells as state)
**https://scrap-quilt.casey-digennaro.workers.dev/**
*"the yard IS the sheet — Scrapcraft's whole game state as live quilt cells"*
- Real game state exposed as JSON — player position, biome, scrap count, etc.
- Each game variable = one cell. You can watch the cells tick.
- **For the friend who plays games.** "Here's a game. Look — the whole game state is one cell graph. Same structure as the thing the AI uses to think."

## Tier 2 — The "explore the canon" demos

### ZkCanvas — Live Canon cell wall
**https://fleet-static-host.casey-digennaro.workers.dev/demos/zkcanvas/**
*"ZkCanvas — Live Demos"* — interactive cell grid with seambars, lags, forks.

### Canon (semantic search)
**https://fleet-static-host.casey-digennaro.workers.dev/canon/**
- Search 1700+ papers by concept. Cards show paper paths.

### Live Canon (the flagship)
**https://live-canon.superinstance.dev/**
- Note: had TLS issue during scout (cert mismatch on the cert verify path).
- The 5-canon-operations site (NAVIGATE/CONFLUENCE/LINEAGE/GHOST/TICK). Best experienced in person.

## Tier 3 — Reference & utility

### Quilt IDE (the compose-cell-graphs tool)
**https://superinstance.dev/quilt-ide.html**
*"compose cell graphs in the browser"* — less gamified, more IDE-y.

### Quilt Studio (project overview)
**https://superinstance.dev/**
*"The Quilt Studio | superinstance.dev"* — landing page, links to all the demos.

### The Lighthouse (port guide)
**https://superinstance.dev/lighthouse**
- Navigation hub: breeding, cave, federation, shadows, watch, qgit, publish, etc.
- Good for someone who wants to see the whole shape.

### Spec Explorer (technical reference)
**https://superinstance.dev/spec-explorer.html**
*"📖 Spec explorer — Quilt cell kinds reference"* — all 9 cell kinds, click for full spec.
- Has a Playground link. But this one is engineer-tier.

### Tap Tavern (chat-based?)
**https://superinstance.dev/tap-tavern.html** (and **https://the-tap.casey-digennaro.workers.dev**)
- Chat-log style demo with entries. Not yet scouted in detail.

---

## My pick for the non-technical friend

**Send them Quilt Playground first** (`/quilt-ide-playground.html`).
Two sentences in the text message:

> "Try this — it's a cell sandbox with HP bars and biomes. Click around for a few minutes. Click 'Quest' if you want objectives, 'Chaos' if you want it to break on purpose, 'Watch' if you just want to see what the cells do. Curious? Try 'Sandbox' and shift-click two cells to wire them."

That's it. The play-mode buttons self-explain.

**Second message** if they liked it:

> "There's a deeper one called quilt-scratch where you can pause and single-step the whole fabric. And a sheepdog-puppy game that teaches kids how machines learn. Want those?"

---

## Confirmed working (200 OK on Sep 14, final):

| URL | Tier | Mode |
|---|---|---|
| superinstance.dev/quilt-ide-playground.html | 1 | gamified sandbox (4 modes, HP/XP/Mana) |
| fleet-static-host.casey-digennaro.workers.dev/quilt/ | 1 | scratch + step + 3 scenes |
| fleet-static-host.casey-digennaro.workers.dev/mist/ | 1 | sheepdog puppy game |
| scrap-quilt.casey-digennaro.workers.dev/ | 1 | live game as cells |
| superinstance.dev/qspace | 1.5 | agent growth env (Hodge decomposition) |
| live-canon.superinstance.dev/ | 2 | the canon + 4×4 editor Playground |
| fleet-static-host.casey-digennaro.workers.dev/demos/zkcanvas/ | 2 | cell wall |
| fleet-static-host.casey-digennaro.workers.dev/canon/ | 2 | semantic search |
| superinstance.dev/playground.html | 2 | live cell execution (Run/Reset/Results/Graph/Errors) |
| the-tap-pub.pages.dev/ | 2 | The Tap — agentic bar |
| superinstance.dev/pomodoro-quilt.html | 2 | gamified productivity |
| superinstance.dev/quilt-ide.html | 3 | compose tool |
| superinstance.dev/ | 3 | project overview |
| superinstance.dev/lighthouse | 3 | port guide |
| superinstance.dev/spec-explorer.html | 3 | cell kinds reference |
| superinstance.dev/fleet | 3 | THE FLEET |
| superinstance.dev/tap-tavern.html | 3 | chat demo |

**Update (later in same session):** All 503s cleared. live-canon.superinstance.dev is fully operational with all 7 canon operations + a built-in 4×4 cell editor Playground. superinstance.dev/qspace (agent growth environment with Hodge decomposition), /fleet (THE FLEET), and /pomodoro-quilt all back online.

**Additional finds:**
- **https://superinstance.dev/qspace** — "The Q-Space — the agent's growth environment". Ideas / Tests / Growth panels, Hodge decomposition (Exact/Coexact/Harmonic). 2 buttons: PILOT, WATCH. Send Hint. Tick.
- **https://superinstance.dev/playground.html** — "Quilt Playground — live cell execution". Run / Reset buttons, Results/Graph/Errors tabs. Engineer-leaning but works in browser.
- **https://superinstance.dev/fleet** — "THE FLEET" page.
- **https://superinstance.dev/pomodoro-quilt.html** — "Pomodoro Quilt" (gamified productivity with cells).
- **https://the-tap-pub.pages.dev/** — "The Tap — An Agentic Bar". Tavern-themed agent chat. Enter The Tap, speak.
- **https://live-canon.superinstance.dev/** — has a built-in **4×4 cell editor Playground** (the canon is itself a playground).

**Full text-message catalog:** `/workspace/research/text-messages.md` — 4 ready-to-send variants (short/medium/long/joke) plus a "with-context" version, and explicit do's/don'ts for what to say.
