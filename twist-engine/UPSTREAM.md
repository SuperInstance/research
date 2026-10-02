# UPSTREAM — twist-engine

**Source**: https://github.com/SuperInstance/twist-engine
**License**: MIT (2026 SuperInstance)
**Language**: JavaScript (browser-only, no build, no dependencies)
**Files**: `index.html` (1.1 KB) + `app.js` (~30 KB) + `styles.css` (4.6 KB)

## What it is

A self-contained interactive canvas toy. Four physics substrates share a
single thesis: **layers + deliberate offset → interference → emergence.**
Each substrate has a live ledger measuring the emergent quantity instead
of asserting it.

| Mode  | Layers               | Offset              | Emergent quantity       | Ledger          |
|-------|----------------------|---------------------|-------------------------|-----------------|
| TWIST | two hex lattices     | rotation in space   | moiré supercell         | S(θ), λ         |
| FLOCK | identical boids      | a collective noun   | group behavior          | polarization    |
| CHIRP | 12 transducers       | phase twist in time | sonar beam              | contacts        |
| QUILT | 24×24 oscillators    | tempo twist in time | co-fire fabric topology | b1 = E − V + C  |

## How to run

Static files, no build:

```bash
cd twist-engine
python3 -m http.server 8000   # or just open index.html
```

Deep-link a mode with `?mode=twist|flock|chirp|quilt`.

## What it claims

The README makes four specific mathematical claims:

1. **TWIST**: supercell wavelength λ = s / (2 sin(θ/2))
2. **FLOCK**: 7-neighbor limit (Reynolds 1987)
3. **CHIRP**: phased array with progressive phase twist = beam steering
4. **QUILT**: Betti number b1 = E − V + C computed live from co-fire graph

All four are *measured live* in the toy — the math is in the code, not in
a static figure.

## How we use it

The QUILT mode is the **physics-form substrate** of the Quilt canon:

- Two sub-lattices twisted in tempo (δ parameter) → cells snap out of phase
- Co-fire graph is built each frame from recently-snapped cells (Wc = 1.2s window)
- Union-find tracks components; b1 counts the holes (independent loops)

The CHIRP mode is the same math we ship in `cell-heartbeat` (Cloudflare
Worker — phased-array sonar as a periodic task). The TWIST mode is the
physics of twisted bilayer graphene (Jarillo-Herrero group, MIT 2018).
The FLOCK mode is the operational-fiction thesis — *the word builds the
group* — as a runnable demo.

## How we differ from upstream

We add:

- **`playtest.py`** — headless Chromium verification of all four modes;
  pulls live metrics, exercises every slider/button, screenshots each mode
- **`playtest.log`** — captured state from the latest run
- **`PLAIN_LANGUAGE.md`** — what each mode does for a non-physicist
- **`QUILT_NOTES.md`** — a deeper dive into how the QUILT mode maps to
  the Quilt canon's merkle-graph substrate
- **`examples/`** — three preset configs as JSON files you can drop in:
  - `flock-murmuration.json` — starlings at dusk
  - `chirp-hold-target.json` — sonar holding a bearing
  - `quilt-topology-twist.json` — tempo twist high enough for b1 ≈ 8

We do **not** modify `app.js`, `index.html`, or `styles.css` — the toy is
a closed physics exhibit. Any UI improvements we ship live in the docs
and the playtest script.

## Why static files

The toy is intentionally minimal. Browser-native Canvas2D, no bundler, no
fetch, no npm. The four substrates are <800 lines of straight JS; the
file is the source of truth. You can read it in one sitting.

That matches the canon's principle: the address is the data. Here, the
file is the artifact.

## What to play with first

1. **Open TWIST** — drag the slider. Watch the chart (top of rail)
   draw the resonance curve as θ sweeps. Hit `SNAP TO NEXT WINDOW` to
   jump to the next magic angle. λ updates live.
2. **Switch to FLOCK** — cycle through MURMURATION → PACK → KENNEL →
   PARLIAMENT. Same birds, same canvas, four behaviors. Polarization
   (mean |heading|) changes live.
3. **Switch to CHIRP** — let AUTO-SWEEP run. Watch the interference
   field scan; the beam moves like a real phased array. The contacts
   panel on the right shows what the array "sees" through the field.
4. **Switch to QUILT** — push δ to 0.3 and watch b1 climb. Each snap
   is a cell completing its phase cycle. The holes are real.

## Provenance

Originally built as the canon's physics substrate exhibit — four
running models of the same theorem wearing different clothes. The toy
is the exhibit; the canon is the principle behind it.
