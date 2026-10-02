# GAN Round 0 — Highest-Level Doctrine Candidates

**Generator** proposed 6 candidates. **Adversary** finds the holes in each.

## Doctrine Candidates (TFM + SFM evaluated)

| # | Doctrine | canon_prob | alignment | action |
|---|----------|-----------|-----------|--------|
| 1 | Workbook where every cell is an observer and every flow is an observation | 0.345 | +1.000 | continue |
| 2 | Three projections reveal one workbook to three observers | 0.443 | +1.000 | continue |
| 3 | Double-entry bookkeeping — books must close | 0.407 | +0.995 | continue |
| 4 | The verb "project" was implicit; other verbs wait | 0.011 | +0.985 | continue |
| 5 | Cells are first-person observers; each owns its axes and witness log | 0.079 | +0.966 | continue |
| 6 | Quilt is a field where observation becomes the cell, flow, projection | 0.412 | +0.935 | continue |

## Adversarial Critique (the holes the Generator is hiding)

**Doctrine 1** — "every cell is an observer": circular. If a cell IS an observer, who observes the observer? Where is the witness log of the cell observing itself? *Hidden question: who observes?*

**Doctrine 2** — "three projections": static. What if the cell needs a fourth, fifth, sixth projection? What about the cell's view of the workbook — where is the *Quilt's* projection of itself? *Hidden question: are 3 enough, or are we freezing the abstraction?*

**Doctrine 3** — "double-entry bookkeeping": assumes balance is a *good* thing. What if the cell needs to be unbalanced on purpose? What if the imbalance IS the cell's state? *Hidden question: is balance always desired?*

**Doctrine 4** — "other verbs wait": assumes the verbs are *finite and discoverable*. What if new verbs are *generated* by the system itself, not discovered? *Hidden question: is the verb-space closed or open?*

**Doctrine 5** — "first-person observer": assumes a single observer. What if a cell is *multiple observers* (a swarm inside a cell)? *Hidden question: can a cell be plural?*

**Doctrine 6** — "field of observation": poetic but vague. What IS a field? What are its equations? What does it predict? *Hidden question: where is the math?*

## Adversary's Synthesis

The Generator is hiding **time**, **cost**, **failure**, and **plurality** behind its doctrines.

- The cell exists in *ticks* but the workbook doesn't model time.
- The cell has a *cost* (energy, compute, money) but the workbook doesn't track cost.
- The cell can *fail* but the workbook has no failure semantics.
- The cell is *singular* but a system of cells might be plural (a swarm, a federation, a chorus).

The next 4 challenges the Adversary surfaces:

1. **Time**: build a cell that exists in a tick. The TFM clock is private; the workbook has no shared time.
2. **Cost**: build a cell that has a price. The Porter can price it; the Designer can budget it.
3. **Failure**: build a cell that can be sick, dead, resurrected. The Quilt has a witness log but no death log.
4. **Plurality**: build a cell that contains cells. An embedded quilt that is itself a quilt. The recursion must terminate.

These are the 4 next-build candidates. Run the Generator on each, have the Adversary poke holes, iterate.
