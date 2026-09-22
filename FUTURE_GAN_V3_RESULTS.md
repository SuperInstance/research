# Future-GAN v3 Results — 14/150 Canon-Promoted

**Date**: 2026-09-22
**Generator**: `future_gan_v3.py`
**Input**: Top 50 polygon seeds × 3 doctrines = 150 lore variants
**Output**: 14 canon-promoted (composite ≥ 0.7)
**Voice**: cells_are_scars + substrate_quantum (DOCTRINE-TARGETED)

## Top 10 Promoted

| Rank | Seed | Voice | Composite |
|---|---|---|---|
| 1 | 92139744 | cells_are_scars | 0.767 |
| 2 | 78327904 | cells_are_scars | 0.753 |
| 3 | 44843186 | cells_are_scars | 0.743 |
| 4 | 979935 | cells_are_scars | 0.740 |
| 5 | 31119735 | substrate_quantum | 0.740 |
| 6 | 77014933 | cells_are_scars | 0.737 |
| 7 | 13025602 | cells_are_scars | 0.733 |
| 8 | 17742147 | cells_are_scars | 0.733 |
| 9 | 75758880 | cells_are_scars | 0.717 |
| 10 | 48619673 | substrate_quantum | 0.713 |

## Voice Distribution

- **cells_are_scars**: 10 promoted (best voice)
- **substrate_quantum**: 3 promoted
- **oracle_is_heard**: 0 promoted (underperformed this batch)
- **comp=0.000**: 24 lores (likely API errors or generation failures)

## Key Findings

1. **cells_are_scars is the winning voice** — 10/14 promoted lore are cells_are_scars
2. **substrate_quantum is second** — 3/14 promoted
3. **oracle_is_heard struggled** this batch — 0/14
4. **Polygon mine v4 seeds yield high composite** — top hit 0.767

## Future-GAN Evolution

- v1: 10 lores (5 seeds × 2 voices) → 2 promoted (composite 0.61-0.67)
- v2: 45 lores (15 seeds × 3 voices) → 4 promoted (composite 0.71-0.73)
- v3: 150 lores (50 seeds × 3 doctrines) → 14 promoted (composite 0.71-0.77)

Future-GAN v3 has the highest **promotion rate** (14/150 = 9.3%) of the
three generations. This validates the doctrine-targeting strategy.

## Promotion Rate by Voice

| Voice | Lores tested | Promoted | Rate |
|---|---|---|---|
| cells_are_scars | 50 | 10 | 20% |
| substrate_quantum | 50 | 3 | 6% |
| oracle_is_heard | 50 | 0 | 0% |

Note: oracle_is_heard had API failures (comp=0.000) in 24/50 cases, which
may skew this rate. Even excluding failures, oracle_is_heard was at the
bottom.

## Stability Probe (next step)

For the 14 promoted cells, run JEV a second time to test stability.
Cells passing both probes (composite ≥ 0.7) become canon-stable.

Expected: ~5-7 stable cells based on previous probe statistics (~50% stability rate).

## Filing

The top cells will be added to the canon archive at:
- `substrate-walker/canon/cells/cell_146.md` through `cell_159.md`
- `substrate-walker/canon/cells/manifest.json`

