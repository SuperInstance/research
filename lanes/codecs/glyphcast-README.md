# glyphcast

**Next-frame prediction and frame-rate synthesis for glyph-domain video streams.**

glyphcast treats a character-rendered video feed (as produced by
[chiaroscuro](https://github.com/SuperInstance/chiaroscuro)) as what it
already is: a stream of discrete tokens on a fixed lattice. That makes the
hard parts of classical video prediction — the blur of continuous targets,
the cost of full-frame transport — dissolve, and turns a tiny model into a
frame-projector a low-power device can afford.

The doctrine and the receipts behind this repo are written in the fleet
canon:

- *Four Things the Pixels Don't Have* — why a glyph stream carries shape,
  time, trainability, and space that a pixel stream surrendered.
- *Tiny Models of Motion, Written in Characters* — the annotated
  literature study this architecture is built from.
- The chiaroscuro **feed-lab** receipts (exp001 spatial / exp002 temporal /
  exp003 generation, in `labs/chiaroscuro`) — measured facts about how
  well scenes actually cross into a language model through this format,
  and what the format must fix (event sidecars, ruler gutters, legible
  engine presets).

## Why this exists

Pixel-space next-frame prediction is cursed by continuous targets: MSE
hedges across plausible futures and the hedge compounds into fog. A glyph
frame is a categorical lattice — a closed palette, cross-entropy that
bites, correspondence between frames that is *visible*. The pixel world
had to be laboriously tokenized before transformer machinery could touch
it. The glyph world is born quantized. glyphcast is the small model that
lives natively there.

## The three jobs

1. **Project** the next grid from recent grids + the event sidecar
   (`predict`). Coarse-to-fine: semantics first (what, where, moving how),
   texture second, detail third — resolution flows to wherever the
   bandwidth moment needs it.
2. **Interpolate** between grids on the cell lattice (`interpolate`) —
   RIFE-style: estimate per-cell flow, synthesize in-betweens by
   flow-guided palette sampling, reserve imagination for occlusion edges.
3. **Certify** predictions (`score`) — a scene/question harness that
   measures how much of the projected scene actually crosses to a reader,
   so improvements are receipts, not vibes.

## Status — honest label

**Proposal stage.** No model weights exist yet. What exists: the ported,
line-faithful numpy engine from chiaroscuro (feed-lab), the mock scene
with ground truth, measured legibility baselines per engine preset, and
the full architecture/roadmap in `docs/`. The first code this repo should
hold is the dataset builder (Phase 0) — see `docs/ROADMAP.md`.

Everything in this repo that describes *results* is labeled as measured,
simulated, or wagered. The fleet doctrine applies: **the crossing is
always a rate** — claims carry their numbers, or they are rumors.

## Module map (planned)

```
glyphcast/
  glyphcast/
    lattice.py      # grid model: palette registry, cell coords, engine pins
    sidecar.py      # discrete event stream (JEV-shaped): births, deaths,
                    # crossings, parity flips — announced, never mined
    data.py         # frame/sidecar datasets from mock scene and streams
    predict.py      # coarse-to-fine token transformer (tiny)
    interpolate.py  # cell-lattice flow + in-between synthesis
    score.py        # crossing-rate evaluation harness (extends feed-lab)
  docs/
    ARCHITECTURE.md
    ROADMAP.md
    DEVELOPER-GUIDE.md
```

## Quickstart (future — Phase 0 gate)

```bash
pip install -e .
glyphcast dataset build --engine wireframe --out data/mock_g0
glyphcast score --reader kimi --frames data/mock_g0/val
```

Until Phase 0 lands, the fastest way to see the medium is the feed-lab:
`labs/chiaroscuro/experiments/feed-lab/` in the workspace that spawned
this repo.

## License

Fleet internal. The receipts are the license.
