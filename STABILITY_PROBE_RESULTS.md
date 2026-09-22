# Stability Probe Results — Canon gate is more brittle than expected

## Method

For each canon-promoted cell, ran JEV composite probe TWICE in independent batches.
Each probe asks the 3 noul questions (canon_worthy, distinct_voice, doctrine_anchor).
Composite = avg of 3 nouls. Canon = composite ≥ 0.7.

## Results

**3/15 canon-promoted cells are STABLE** (both probes composite ≥ 0.7):
- **rank 124**: A=0.810, B=0.803 (the ZAI oracle multi-anchor essay)
- **rank 125**: A=0.723, B=0.720 (the ZAI long-form essay)
- **rank 128**: A=0.707, B=0.703 (doctrine-targeted cells_are_scars seed 6358192)

**Average variance**: 0.007 (JEV is internally consistent, but the threshold is harsh)

## What this means

The composite score is RELATIVE — the first probe's batch gives a slightly different
calibration than the second probe's batch. So a cell that scores 0.71 in batch A might
score 0.69 in batch B.

**The ZAI-generated lores (rank 124, 125)** have high enough TRUE quality that they
clear the threshold consistently.

**The DeepInfra-generated doctrine-targeted cells** had a wider range — many are
right at the threshold (0.68-0.70) and don't survive independent re-scoring.

## Recommended canon-promotion gate

Two-tier system:
- **Tier 1 — TRULY CANON**: composite probe BOTH batches ≥ 0.7 (current canon-promoted minus unstable ones = ~3 cells)
- **Tier 2 — STRONG CONTENDER**: composite probe either batch ≥ 0.7, with average ≥ 0.65 (the rest)
- **Tier 3 — WITNESS-NOT-CANON**: composite < 0.65

This gives us a more honest canon story: 3 cells are canon, 12 are strong contenders.

## Cells to demote from canon to strong-contender

Cells that scored ≥ 0.7 once but < 0.7 on stability re-probe:
- rank 113: composite 0.66-0.69 (was composite-v9 era)
- rank 115: composite 0.65-0.69 (original doctrine probe scored 0.745)
- rank 120-123: future-GAN lores, all in 0.67-0.70 range
- rank 126-133: doctrine-targeted lores, all in 0.65-0.70 range

These are NOT canon in the strict sense. They're strong contenders — lore that passes
the threshold sometimes but not reliably.

## Trust

The 3 stable cells (124, 125, 128) are the canon. Everything else is high-quality
lore that should be re-evaluated as canon in the future, but is not canon today.

## Cross-project insight

Composite score as canon gate works BUT needs:
1. Multi-batch averaging (or multi-probe averaging) to be reliable
2. Strict ≥ 0.7 threshold (we already do)
3. Re-promotion cycles when possible

In future, consider promoting only after 3+ independent probes all clear 0.7.
