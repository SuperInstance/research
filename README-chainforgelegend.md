# ChainForgeLegend — Quilt Edition

A small React app (upstream by harutosati) elevated with a Quilt
projection layer so the same program is **visible as a cell-graph**.

## The three doors — pick the one that fits you

- **📖 [UPSTREAM.md](docs/UPSTREAM.md)** — The original ChainForgeLegend,
  faithfully documented. If you want the unmodified React app, start here.
- **⚙️ [QUILT.md](docs/QUILT.md)** — The cell-graph projection layer.
  Engineering English. Shows how the same React component tree becomes
  8 Quilt cells with typed links.
- **🚢 [PLAIN_LANGUAGE.md](docs/PLAIN_LANGUAGE.md)** — For captains,
  mechanics, deckhands, working people. Two-minute read. Plain language.

## Status

| Area | State |
|---|---|
| Upstream code | ✅ Preserved, unmodified |
| Cell-graph projection | ✅ Documented (8 cells, 9 typed links) |
| Python reference port | ✅ Example in `QUILT.md` |
| TypeScript port | 🔮 Stub — needs `tsc` setup |
| JSON-API | 🔮 Stub — needs REST server |
| Pico port | 🔮 Future — overkill for an 8-cell substrate |
| Vectorize cross-pollination | 🔮 Future — needs Cloudflare DNS clear |

## Quick start

```bash
npm install
npm start           # http://localhost:3000
npm test            # runs the upstream App.test.js
```

## The cell-graph (canonical, 8 cells)

```
title → header → app → container → input → list → item_n → remove_btn
```

Each cell maps to an upstream component or state slot. `EFFECT` mirrors
every `setState`. The witness chain mirrors every render. The
cell-graph IS the program — the React tree is one rendering of it.

## What we kept vs added

**Kept** (from upstream):
- All `src/` code (`App.jsx`, `components/ChainforgelegendContainer.jsx`,
  CSS, tests)
- `package.json`, `tsconfig.json`, `public/index.html`
- The original `LICENSE` (MIT)

**Added** (the Quilt layer):
- `docs/UPSTREAM.md` — original-repo-faithful documentation
- `docs/QUILT.md` — the cell-graph projection
- `docs/PLAIN_LANGUAGE.md` — working-people version
- `LICENSE-QUILT` — MIT, for the Quilt layer
- This README (rewritten as a landing-page dispatcher)

**Nothing in the upstream was renamed or moved.**

## See also

- [SuperInstance/quilt-cordis](https://github.com/SuperInstance/quilt-cordis) —
  the cell-plugin bridge that makes the React components addressable
- [SuperInstance/quilt-canon-cli](https://github.com/SuperInstance/quilt-canon-cli) —
  the unified CLI for Quilt canon operations
- [SuperInstance/quilt-foundation](https://github.com/SuperInstance/quilt-foundation) —
  the 5+1 opcode algebra
- The original: [harutosati/ChainForgeLegend](https://github.com/harutosati/ChainForgeLegend)
