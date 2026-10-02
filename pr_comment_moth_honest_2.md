## Review — moth-honest #2 cells-bench

**Verdict**: MERGEABLE (after #1 lands).

Cleanest pairing with the substrate. The `CLAIM_CLASS` vocabulary unification addresses the real bug found:

> "first fixture run scored tp=0 purely from kernel↔evaluator vocabulary drift; that drift is a false-positive machine"

This is **load-bearing** for any honest scoring system — without a shared vocabulary, every disagreement defaults to FP.

**Adversarial-review gate inside the evaluator** is the right structural move. A judge that's only judged by external benches can drift toward its own favorite false positives; embedding a judge-the-judge pattern catches drift early.

**Suggestions (non-blocking)**:
- The 5-cell panel looks like a known-good + planted-truth mix. Make sure the cell IDs match the exercise names in planted.py so the surface is grep-able from outside.
- When scaling beyond 5 cells, the panel might want a stochastic generator (cells.E-style adversarial profile).

**Net**: ready.
