# UPSTREAM — MCPMempool (preserved from upstream)

This document preserves the **original upstream project** — MCPMempool,
by fuad403273 — faithfully, with no Quilt framing imposed. If you want
the original, **read this first**. The Quilt layer (added by
SuperInstance) is documented separately in `QUILT.md`.

## Original description

> Auto-Scalable MCPMempool Manager that handles Priority Based
> Scheduling, built for everyday use. Aimed at developers who need a
> straightforward, dependable solution.

## What the upstream is

- A **TypeScript** module with a `MCPMempool` class
- An entry-point script (`src/index.ts`) using `minimist` for CLI args
- Configurable via command-line flags (`--verbose`, `--config <path>`,
  `--dry-run`)
- The class lives in `src/mcpmempool.ts`
- TypeScript config in `tsconfig.json`

## What the upstream does

The `MCPMempool` class is a **priority-based scheduler for memory-pool
operations** (the "MCP" stands for **Memory Control Panel** in the MCP
Protocol / Model Context Protocol sense — a queue of pending operations
ordered by priority). The class manages:

- A pool of pending operations (memory allocations, deallocations,
  reads, writes — the typical ops in a memory-pool context)
- Priority assignment per operation
- Auto-scaling of the pool size as load varies
- Configuration via env vars + CLI flags

This is the kind of thing a low-level systems developer uses to manage
shared memory resources across many concurrent processes.

## How the upstream works

```
src/
├── index.ts          — CLI entry, arg parsing, instantiates MCPMempool
└── mcpmempool.ts     — The MCPMempool class: pool management, priority scheduling
tsconfig.json        — TypeScript compilation config
package.json         — npm metadata + scripts
```

### CLI interface

```bash
node dist/index.js --verbose --config ./config.json --dry-run
```

## Quick start (original)

```bash
git clone https://github.com/SuperInstance/MCPMempool-quilt.git
cd MCPMempool-quilt
npm install              # install minimist + dependencies
npm run build            # tsc → dist/
npm start                # runs dist/index.js with default args
```

## Credits and license

- **Upstream author:** fuad403273
  ([fuad403273/MCPMempool](https://github.com/fuad403273/MCPMempool))
- **Upstream license:** preserved (see `LICENSE`)
- **Quilt elevation:** SuperInstance (added the cell-graph projection layer)
- **Quilt layer license:** MIT (added as `LICENSE-QUILT`)

## Notes on the fork

- **Date imported:** 2026-09-15
- **Preserved:** All upstream code (`src/index.ts`, `src/mcpmempool.ts`,
  `tsconfig.json`, `package.json`). Nothing upstream was modified.
- **Added:** `QUILT.md` (the cell-graph projection), `PLAIN_LANGUAGE.md`
  (captains-and-mechanics version), and an updated landing-page README.
- **Pre-Quilt quirks:** The original README mentions "python" as the
  technology stack, but the actual code is TypeScript (Maven-style test
  runner not present). We documented what the code actually does, not
  what the README claims.

---

For the **Quilt projection layer** that makes this program **visible as
a cell-graph**, see `QUILT.md`. For the **plain-language version** that
explains what this does for working people, see `PLAIN_LANGUAGE.md`.
