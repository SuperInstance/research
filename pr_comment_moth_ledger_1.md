## Review — moth-ledger #1 v2 envelopes

**Verdict**: REQUEST CHANGES (mergeable=False, state=dirty).

Same situation as #2 trial-balance — branch `moth-ledger-v2-envelopes` is stale against main. CI #6 (push) failed, CI #7 and #8 (subsequent pushes) green — meaning the branch was fixed locally but the PR hasn't been refreshed.

### Mechanism is correct

The two envelope upgrades are the load-bearing moves:

1. **FINDING/v2 — replay binding**: `genome_hash` + `dice_seed` + walk context. A finding you cannot replay is a rumor. This is the receiptable-execution doctrine: stochastic in shape, deterministic in residue.
2. **REFUSAL/v2 — polarity**: distinguishes `positive` (had means, refused: decoy_resisted, window_full) from `negative` (abstention: starvation, dormancy). The honesty test: "counting negative refusals as honesty is how a hungry hunter fakes a virtuous one."

This polarity law unlocks everything downstream — moth-honest's refusal-track scoring, moth-cells's death-as-refusal, moth-runner's homeostatic throttle. The whole family depends on it.

### Action

```bash
git checkout moth-ledger-v2-envelopes
git rebase main
# Resolve any conflicts (the rebase pulled in ruff-fix changes too)
git push --force-with-lease
```

Once the push happens, CI re-runs and PR should merge cleanly. The rebase will pick up the ruff-fix-ci-gate changes that already landed on main.

### Cross-project insight (moth family + cellforge)

The polarity law is the moth-side analog of cellforge's causal-consistency verdict (v0.4.1). Both are **structural commitments to honesty**:
- cellforge: rewind is a *trust claim* → return a verdict (proceed/warn/block)
- moth-ledger: refusal is a *characterization* → label positive vs negative

Both refuse to let a system silently fail or silently succeed. The auditor can later verify by re-derivation.

### Net

Once rebased and CI green: MERGEABLE.
