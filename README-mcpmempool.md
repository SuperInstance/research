# MCPMempool — Quilt Edition

An auto-scaling TypeScript memory-pool manager (upstream by fuad403273)
elevated with a Quilt projection layer so every mempool operation is a
**tappable cell**.

## The three doors — pick the one that fits you

- **📖 [UPSTREAM.md](docs/UPSTREAM.md)** — The original TypeScript
  sched-pool, faithfully documented. If you want the unmodified project,
  start here.
- **⚙️ [QUILT.md](docs/QUILT.md)** — The cell-graph projection layer.
  Engineering English. Shows how every mempool operation becomes a
  tappable cell.
- **🚢 [PLAIN_LANGUAGE.md](docs/PLAIN_LANGUAGE.md)** — For captains,
  mechanics, deckhands, working people. Two-minute read. Plain language.

## Status

| Area | State |
|---|---|
| Upstream code | ✅ Preserved, unmodified |
| Cell-graph projection | ✅ Documented (1 root cell + N op cells + 4 support cells) |
| "Tappable cell" UI | 🔮 Stub — data model ready, render is a separate task |
| Python reference port | ✅ Example in `QUILT.md` |
| C / production port | 🔮 Future |
| GPU scheduler (flx-cuda) | 🔮 Future |
| Vectorize cross-pollination | 🔮 Future — needs Cloudflare DNS clear |

## The big idea — every mempool op is a tappable cell

A memory pool is a **queue of cells**. Every allocation is a BIND. Every
deallocation is a FORGET. Every priority change is an EFFECT. Every
read is a VIEW. The auto-scaler is a TICK-bound policy.

The Quilt projection doesn't change the runtime — it makes the queue
**visible and tappable**. You can click any cell in the mempool, see its
address, its priority, its timestamp, and either let it run or manually
trigger its next state.

## Quick start (the original)

```bash
npm install
npm run build
npm start              # runs dist/index.js
node dist/index.js --verbose --config ./config.json --dry-run
```

## The cell-graph (canonical)

```
mempool_root ─┬─ op_1 (alloc, priority 5, queued)
              ├─ op_2 (free, priority 9, running)
              ├─ op_3 (write, priority 3, done)
              ├─ scheduler
              ├─ autoscaler
              └─ metrics
```

Every enqueued op becomes a new cell. Every state change updates the
cell. The witness chain IS the audit log.

## What we kept vs added

**Kept** (from upstream):
- All `src/` code (`src/index.ts`, `src/mcpmempool.ts`)
- `tsconfig.json`, `package.json`
- The original `LICENSE`

**Added** (the Quilt layer):
- `docs/UPSTREAM.md` — original-repo-faithful documentation
- `docs/QUILT.md` — the cell-graph projection
- `docs/PLAIN_LANGUAGE.md` — working-people version
- `LICENSE-QUILT` — MIT, for the Quilt layer
- This README (rewritten as a landing-page dispatcher)

**Nothing in the upstream was renamed or moved.**

## See also

- [SuperInstance/quilt-cordis](https://github.com/SuperInstance/quilt-cordis) —
  the cell-plugin bridge; mempool operations become Cordis plugins
- [SuperInstance/quilt-foundation](https://github.com/SuperInstance/quilt-foundation) —
  the 5+1 opcode algebra
- [SuperInstance/flx-cuda](https://github.com/SuperInstance/flx-cuda) —
  GPU-accelerated priority scheduling
- The original: [fuad403273/MCPMempool](https://github.com/fuad403273/MCPMempool)
