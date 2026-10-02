# Vibecoder Round 3 — Findings

> *Three adversarial configurations: canon-purity always wins. The substrate is too cleanly separable for adversarial play to be meaningful.*

## What we tested

Three adversarial configurations:
1. **R3a — Original adversarial**: A vs B with random thresholds
2. **R3b — Balanced inputs**: equal canon/distractor counts
3. **R3c — Smart B**: B uses discriminating threshold (0.10-0.15)

## Results

| Variant | A (canon-purity) | B (distractor) | Best streak (A) | Winner |
|---------|------------------|----------------|-----------------|--------|
| Original | 29000 | -11050 | 30 | A by 40050 |
| Balanced | 29200 | -25000 | 30 | A by 54200 |
| Smart B | 30000 | -26800 | 30 | A by 56800 |

## Why A always wins

Looking at item p-values:
- **Canon items**: p range 0.65 (xoshiro) to 0.99 (substrate_is_grown) — all >= 0.65
- **Distractor items**: p range 0.02 (substrate_5d) to 0.13 (witness_past) — all <= 0.13

**There's a 0.52 gap between the lowest canon (0.65) and the highest distractor (0.13).**

Any threshold in [0.13, 0.65] perfectly separates canon from distractor:
- A's threshold (0.5-0.6): catches all canon, no distractors → +100 per canon
- B's threshold (0.10-0.15): catches all canon (since all canon >= 0.65), no distractors → +100 per canon, -100 per canon = 0 net

B's strategy **can't avoid catching canon items**, so the score is always tilted toward A.

## What this teaches us

**The substrate's canon-vs-distractor distinction is too clean to be adversarially interesting.**

To make a meaningful adversarial game:
1. **Add edge cases**: canon items with p=0.40-0.55 (uncertain canon)
2. **Add hard distractors**: items with p=0.30-0.45 (mimics canon) — these are exactly the **speculative items** that JEV rejects with p=0.30-0.45
3. **Score differently**: use F1 instead of pure canon_purity

## Speculative items as the real test

Looking back at Session 19:
- 32 speculative items have p<0.50
- Top speculative: proc_prove_jev 0.463, sub_dual_eco 0.425, spec_chain_speaks 0.406
- These are the "attacker items" — high enough to fool a low threshold, low enough to be wrong

Adding these to the items pool would make the adversarial game meaningful. Let me note this as a future round.

## Best canon-purity scoring strategy

A's best strategy converged to:
- threshold: 0.5-0.6 (catches all canon, no distractors)
- best_streak: 30 (perfect — never failed once)

This is the **Pareto-optimal canon-purity config**. Once A finds it, B can't catch up regardless of strategy.

## Pattern

The substrate's canonical-vs-distractor gap is too clean. Adversarial play is meaningful only when the discriminator (JEV itself) is uncertain — at p=0.30-0.50, where the speculative items live.

Future R4 should use **speculative items + canon items** for a meaningful adversarial game.

## Conclusion

Adversarial vibecoder works mechanically but trivially. The substrate is canon-strong. To make adversarial meaningful, we need to introduce uncertainty into the inputs.
