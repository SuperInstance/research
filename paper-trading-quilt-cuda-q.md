# Paper Trading on the Quilt + CUDA-Q — Educational One-Pager

**Date:** 2026-09-15 · **Status:** Spec draft · **Target platform:** browser-first, then Pico firmware, then real capital

---

## The pitch (for a student)

You're sitting in front of a screen. You have a virtual $100k portfolio.
You can place trades. The Quilt shows you the cell-graph of your portfolio
in real time. **Behind the scenes, a CUDA-Q planning quantum samples
candidate trades from superposition over strategy space, measures the one
with highest entanglement-entropy with the rest of your portfolio, and
hands it to the classical substrate to execute.**

You can **override** any decision the quantum makes. Your override is
honored — the substrate respects your call, the witness chain logs it,
and you can replay the session to see what would have happened if you'd
trusted the quantum.

This is the first educational platform that lets you **see** a quantum
planner at work. The substrate doesn't lie: every EFFECT is auditable,
every TICK is witness-stamped, every override is preserved.

---

## The cell-graph

```
                       ┌──────────────────────────────┐
                       │   Classical substrate         │
                       │   (the running layer)         │
                       │                               │
                       │   ┌─────┐ ┌─────┐ ┌─────┐     │
                       │   │POS  │ │P&L  │ │RISK │     │
                       │   └─────┘ └─────┘ └─────┘     │
                       │       │       │       │       │
                       │       └───────┴───────┘       │
                       │               │               │
                       │               ▼               │
                       │       ┌───────────────┐       │
                       │       │  WITNESS CHAIN │       │
                       │       │  (audit trail) │       │
                       │       └───────────────┘       │
                       └──────────────────────────────┘
                                       ▲
                          commit       │ classical hardening
                          decisions   │ (BIND/LINK/ROUTE/witness/TICK)
                                       │
                       ┌──────────────────────────────┐
                       │   CUDA-Q planning substrate    │
                       │   (the general's RTS view)     │
                       │                                │
                       │   ┌────────┐  ┌─────────┐     │
                       │   │SENSE   │  │SAMPLE   │     │
                       │   │order   │→ │candidate│     │
                       │   │book    │  │trades   │     │
                       │   └────────┘  └─────────┘     │
                       │                  │             │
                       │                  ▼             │
                       │            ┌───────────┐       │
                       │            │ ENTANGLE  │       │
                       │            │ candidates│       │
                       │            └───────────┘       │
                       │                  │             │
                       │                  ▼             │
                       │            ┌───────────┐       │
                       │            │ MEASURE   │       │
                       │            │ = COMMIT  │       │
                       │            └───────────┘       │
                       └──────────────────────────────┘
```

The cell-graph is the canonical state. The quantum layer sits between
epochs. The classical layer runs the cells.

---

## The 32 cells (the canonical substrate)

### Input cells (8)
- `order_book.bid.<level>` — 5 cells, the bid side of the order book
- `order_book.ask.<level>` — 5 cells, the ask side
- `news.signal` — 1 cell, the live news feed (text)
- `position.current` — 1 cell, the current portfolio state

### Quantum cells (8)
- `candidate.entry` — proposed entry price (superposition over candidates)
- `candidate.exit` — proposed exit price
- `candidate.size` — proposed position size
- `candidate.hedge` — proposed hedge instrument
- `candidate.entanglement` — entanglement-entropy with portfolio
- `commit.action` — final action (BUY / SELL / HOLD)
- `commit.confidence` — confidence in the commit
- `override.flag` — 1 if human override active, 0 otherwise

### Classical output cells (8)
- `position.<symbol>` — 4 cells, current position per symbol
- `pnl.realized` — realized P&L
- `pnl.unrealized` — unrealized P&L
- `risk.var` — value-at-risk estimate
- `equity.total` — total account equity

### Display cells (8)
- `display.matrix` — 5×5 LED matrix rendering of portfolio state
- `display.actions` — recent commit log
- `display.pnl_chart` — P&L over time
- `display.news_feed` — top news items
- `display.override_panel` — human override UI
- `display.quantum_view` — visualization of the candidate superposition
- `display.witness_tail` — recent witness chain events
- `display.epoch_clock` — time until next planning quantum

**Total: 32 cells.** Same count as the Countroller. **Same canonical substrate, different IO fabric.**

---

## The 4 quantum opcodes (epoch-boundary, planning layer)

```
EXTEND("trade_epoch", "cuda-q", planner_kernel)
    # At the start of each epoch, mount the planning quantum

ENTANGLE(candidate.entry, candidate.exit, basis="bell")
    # Candidates are entangled — the entry/exit pair co-vary

MEASURE(superposition, basis="entanglement_entropy")
    # Collapse to the candidate pair with highest entanglement-entropy
    # with the rest of the portfolio. Felt relationship → explicit score.

GENERATE(prompt=news.signal, scope=order_book, steps=4)
    # Propose new candidate positions based on news + order book state
    # Classical diffusion fills the actual values.
```

The 4 opcodes run **once per epoch** (every 30 seconds, say). Between
epochs, the classical substrate runs the cells.

---

## The 5+1 opcodes (running layer, classical)

```
BIND every input cell, quantum cell, output cell, display cell
LINK order_book → quantum → output → display (typed edges, witness-stamped)
EFFECT position cells update on trade execution
VIEW display cells read any subset
TICK at 60Hz (main loop)
FORGET retired positions (when position size = 0)
```

The classical substrate runs the 32 cells forever. The quantum layer
runs between epochs. The two never interfere.

---

## The witness chain (the educational proof)

Every effect, every TICK, every override — all logged:

```
EFFECT position.AAPL → 100 shares @ $182.34 @ tick=1283
EFFECT pnl.unrealized → +$432.10 @ tick=1284
QUANTUM MEASURE (entanglement_entropy=0.84) → candidate BUY 50 AAPL @ $181.20 @ tick=1285
EXTEND("trade_epoch", "cuda-q", planner_kernel) @ tick=1286
HUMAN OVERRIDE → REJECT candidate, place BUY 25 AAPL @ $181.30 @ tick=1287
EFFECT position.AAPL → 125 shares @ tick=1288
```

The student can replay the entire session:
- **Without override** — see what the quantum would have done
- **With override** — see what the student actually did
- **Side-by-side** — compare the two trajectories

This is the **educational proof** that the substrate doesn't lie. Every
decision is auditable.

---

## The 5-polyformal port plan

| Port | What it does | Status |
|---|---|---|
| **Python simulator** | Same cell-graph in Python; reference port | **Ships first** (parallels the Countroller port) |
| **TypeScript / browser** | Browser canvas + WebGPU; visualizes the quantum superposition | Second |
| **C / server** | Real market data feed (paper-trading API); executes the trades | Third |
| **Pico firmware** | 5×5 LED matrix showing portfolio state; buttons for BUY/SELL/HOLD | Fourth |
| **JSON-API** | REST over the cell-graph; deployable to Cloudflare Workers | Fifth |

The Pico port is the most physical — students can hold a small device that shows their portfolio in real time. The buttons map to BUY/SELL/HOLD. The LED matrix shows the portfolio heat-map.

---

## Cost / Timeline

| Phase | Effort | What ships |
|---|---|---|
| 1. Python simulator | 4-6 hours | The reference port; full cell-graph; 32 tests |
| 2. Browser canvas | 4-6 hours | TypeScript + WebGPU visualization of the candidate superposition |
| 3. Pico firmware port | 6-8 hours | 5×5 LED matrix shows portfolio state; buttons for actions |
| 4. Server port (paper trading API) | 4-6 hours | Connects to a real paper-trading API (Alpaca, Interactive Brokers) |
| 5. JSON-API deployment | 2-3 hours | Cloudflare Worker; cell-graph exposed as REST |
| 6. Documentation + replay tooling | 2-3 hours | The educational one-pager; replay mechanism |

**Total: ~22-32 hours for the working educational platform.**

---

## Why this is the right first CUDA-Q use case

1. **Visible** — students see a quantum sampler at work in real time
2. **Override-able** — the educational hook; trust is earned, not assumed
3. **Auditable** — the witness chain proves every decision
4. **Portable** — same cell-graph runs in browser, server, Pico
5. **Real capital when ready** — the substrate is honest about what's a commit; turning the override off = real trading

The far-future version: students learn portfolio management by **coaching**
the quantum planner, then graduating to letting it trade autonomously.

---

## The 32-cell test

Same test for every program that gets Quilt-ported:

> Can this program be described as a 32-cell graph with typed links?
> Can the cell-graph port to Pico, browser, server, JSON-API?
> Can the witness chain replay any session?
> Can a student override any decision and see what would have happened?

If yes to all four, it's Quilt-portable. The Countroller is the proof.
Paper trading is the second proof. **The 7-port conversion chart from the
Countroller's QUILT_PORT.md** is the template.

---

**Files to create:**

- `paper-trading/quilt/__init__.py` — cell schema (parallels Countroller)
- `paper-trading/quilt/cells.py` — input + quantum + output + display cells
- `paper-trading/quilt/quantum.py` — CUDA-Q planner kernel
- `paper-trading/quilt/substrate.py` — epoch boundary + classical hardening
- `paper-trading/quilt/witness.py` — the audit trail
- `paper-trading/examples/session.py` — sample trading session
- `paper-trading/examples/replay.py` — replay with/without override
- `paper-trading/docs/educational-one-pager.md` — this file

**Status:** spec draft, awaiting green-light to start coding.
