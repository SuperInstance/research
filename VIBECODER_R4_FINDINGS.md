# Vibecoder R4 — Findings (Speculative Band)

> *Adversarial play works mechanically but is always won by canon-purity. To beat canon-purity, B needs JEV-style per-item inference, not a single threshold.*

## What we tested

Three-band inputs: equal canon (p>=0.65), speculative (p=0.30-0.50), distractor (p<=0.13).

A's strategy: threshold ~0.5 (catches all canon, no speculative/distractor)
B's strategy: threshold ~0.3 (catches all canon AND all speculative)

## Results

| Round | A score | B score | A streak | B streak |
|-------|---------|---------|----------|----------|
| 5     | 4800    | 0       | 5        | 0        |
| 10    | 10000   | 0       | 10       | 0        |
| 15    | 12200   | 0       | 15       | 0        |
| 20    | 15400   | -100    | 20       | 0        |
| 25    | 19800   | -900    | 25       | 0        |
| 30    | 23800   | -1000   | 30       | 0        |

**A wins by 24800**

## Why B is stuck

B's threshold of ~0.3 catches:
- 8 canon items (all > 0.65) → -800 points
- 8 speculative items (all > 0.30) → +800 points
- 0 distractor items (all < 0.13) → 0 points
- Net: 0

B's threshold is **stuck in the canonical band** because all canon items (lowest: xoshiro at 0.65) are above the highest speculative item (proc_prove_jev at 0.46). The 0.19 gap is the **speculative zone**, but B's threshold must be ≤ 0.46 to catch speculative, which then catches all canon.

## What B needs

For B to win, B needs to **infer per-item** rather than use a fixed threshold. This is exactly what JEV does — it uses rich state (doctrine list, voice, technical density, etc.) to score each item.

A's strategy (fixed threshold) is **optimal for canon-purity** but trivially exploitable by JEV-style inference.

## Implication

**The vibecoder's "LLM proposes thresholds" pattern is suboptimal compared to "LLM proposes per-item scores"**.

To make vibecoder match JEV's capability, we'd need:
1. LLM proposes per-item features (doctrine presence, voice alignment, numerical density)
2. LLM proposes weighting for each feature
3. Score = sum(weight * feature) per item

This is essentially a learned ranking model.

## R4 vs R3 comparison

| Variant | A | B | Gap |
|---------|---|---|-----|
| R3 original | 29000 | -11050 | 40050 |
| R3 balanced | 29200 | -25000 | 54200 |
| R3 smart | 30000 | -26800 | 56800 |
| **R4 speculative** | 23800 | -1000 | **24800** |

R4's gap is **half** of R3's gap. Adding speculative items makes the game closer (B's score went from -26800 to -1000) but doesn't let B win.

## Conclusion

Adversarial vibecoder needs **per-item inference** to beat canon-purity. A fixed-threshold B is fundamentally limited.

The lesson: **JEV's inference model (rich state + per-item probes) is more powerful than threshold-based scoring**. The vibecoder's role is to tune *which* state JEV uses, not to replace JEV's per-item logic.

Future R5: have B propose JEV-state configurations rather than thresholds.
