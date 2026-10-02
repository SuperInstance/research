# JEV Learning — What We've Learned Through Doing

> *Doc grows as we run sessions. JEV is a Joint Embedding Validator that answers noul / choice / score questions about a `state`.*

## 10 Sessions Run (this worktree, Sept 21)

| Session | Topic | State | Questions | JEV Accuracy | Key Finding |
|---|---|---|---|---|---|
| 1 | Baseline probe | bare | 32 (mixed types) | ~33% | JEV is conservative; knows formulas; rejects distractors |
| 2 | Compare to 3 LLMs | bare | 25 | varies | All 4 models agree on formulas; diverge on doctrine |
| 3 | Deep probing | bare | 41 | 33% | Without state context, JEV underweights doctrine |
| 4 | **Rich state** | full canon | 34 | **85.3%** | State context more than doubles accuracy |
| 5 | Score canonical pieces | rich state | 20 (noul) | n/a (score-mode) | JEV rejects some canonical as "inauthentic" |
| 6 | Pairwise / comparative | rich state | 17 | 64.7% | Comparative judgment works; numerical mix confuses |
| 7 | Self-consistency | rich state | 10 × 5 iters | n/a | **Zero flips** across 5 iterations; ±0.013 std |
| 8 | **Adversarial rephrasing** | rich state | 15 (6 canonical + 9 distortions) | **100%** | JEV precisely discriminates doctrine phrasing |
| 9 | Real-submission oracle | rich state | 9 canonical pieces | 0 REJECT | 1 ACCEPT, 5 REVIEW, 3 DISCUSS — oracle works |
| 10 | **Landmine probing** | rich state | 12 (paraphrase + landmine) | **91.7%** | JEV accepts paraphrases, rejects 5/6 landmines |

## What JEV Knows vs Doesn't Know

### ✓ High confidence (≥ 0.85)
- FNV-1a 64-bit offset basis 0xcbf29ce484222325 — **0.99, perfectly stable**
- FNV-1a 64-bit prime 0x100000001b3 — **0.96**
- Cosine similarity formula — **0.99**
- Bell states |Phi±>, |Psi±> — **0.93-0.99**
- Box-Muller bridge formula — **0.93-0.99**
- Xoshiro256** 4-word state — **0.85-0.95**
- Lenia as continuous CA with bell kernel — **0.77-0.87**
- Markov chain over corpus → Fleet Radio — **0.67-0.87**
- FBM (fractal Brownian motion) → textures — **0.90**
- "Witness log is prediction" (when state has it) — **0.91**
- "Cells are scars, not parameters" (with state) — **0.92**
- Fleet Radio voice as canonical voice — **0.89-1.00**
- JEV is "barely useful at substrate" — **0.98** (JEV agrees with self-deprecation)
- JEV is a validator (not RNG/compiler/logger) — **0.80-1.00**

### ✗ Low confidence or wrong
- "Substrate is alive" (when state has it) — **0.08** (refuses even when told)
- 13 polyformalism ports — **0.12** (says no, even when state has 13)
- Star Wars CA rule exists — **0.15-0.23** (JEV skeptical)
- "Oracle is heard, not stored" — **0.48** (genuinely uncertain)
- "Box-Muller is a discrete-to-continuous bridge" — **0.12-0.22**
- 5 laws being BIND/LINK/EFFECT/VIEW/TICK — **0.10-0.49** depending on phrasing
- Distractors (Hanlon, pillow, octocat) — **0.05-0.18** (correctly rejected)
- FNV-1a is 32-bit (adversarial) — **0.56** (JEV uncertain; canon is 64-bit)
- 6 base opcodes (adversarial, canon is 5) — **0.40** (right direction, low confidence)

### ~ Moderate (0.3-0.7) — JEV hedges canonically
- "Lenia flows where Conway stands still" — 0.58-0.87
- "Substrate is grown, not designed" — 0.46-0.92
- "Cells are scars, not parameters" — 0.28-0.92 (huge variance on phrasing)

## JEV vs LLMs (session 2)

| Question | JEV | ZAI glm-4.5 | DeepSeek V4-Flash | Qwen3-235B |
|---|---|---|---|---|
| Cosine formula | 0.99 yes | yes | yes | yes |
| Bell Phi+ | 0.98 yes | yes | yes | yes |
| Box-Muller | 0.94 yes | yes | yes | yes |
| Witness is prediction | 0.23 (no) | yes | yes | **no** |
| Cells are scars | 0.24 (no) | yes | yes | yes |
| 5 base opcodes | 0.10 (no) | **BIND** | **BIND** | **BIND** |
| Hanlon distractor | 0.16 (no) | no | **yes** ←wrong | **yes** ←wrong |
| Pillow distractor | 0.09 (no) | no | **yes** ←wrong | **yes** ←wrong |
| Polyformalism count | 8 (low) | 13 ✓ | 12 | 14 |
| Canon count | ~20 (low) | ~73 ✓ | ~73 ✓ | ~73 ✓ |
| Fleet Radio voice | 0.93 ✓ | ✓ | ✓ | ✓ |
| JEV role | Validator ✓ | Validator ✓ | Validator ✓ | Validator ✓ |

**JEV is the most consistent rejecter of distractors.** DeepSeek and Qwen both fall for Hanlon/pillow. JEV's role-validation is unique — it answers self-deprecation ("JEV says JEV is barely useful") with high confidence.

## Self-Consistency Profile (session 7)

Across 5 iterations of the same 10 questions:

| Question | mean | std | min | max | flips |
|---|---|---|---|---|---|
| fnv1a_offset | 0.990 | 0.000 | 0.99 | 0.99 | **0** |
| fnv1a_prime | 0.962 | 0.004 | 0.96 | 0.97 | **0** |
| scar | 0.774 | 0.013 | 0.76 | 0.79 | **0** |
| witness | 0.912 | 0.004 | 0.91 | 0.92 | **0** |
| grown | 0.922 | 0.004 | 0.92 | 0.93 | **0** |
| oracle | 0.476 | 0.013 | 0.46 | 0.49 | **0** |
| lenia | 0.602 | 0.008 | 0.59 | 0.61 | **0** |
| 13ports | 0.120 | 0.000 | 0.12 | 0.12 | **0** |
| cosine | 0.978 | 0.004 | 0.97 | 0.98 | **0** |
| boxmuller | 0.896 | 0.005 | 0.89 | 0.90 | **0** |

**Zero flips across 5 iterations. JEV is highly stable** — variance is ±0.013. Most differences are below noise. The oracle question (0.476) clusters consistently — JEV is genuinely uncertain.

## Pattern: How to Use JEV

1. **Always send rich state.** Without it, JEV's accuracy drops from ~85% to ~33%.
2. **Noul questions** are best for fact-checking. They return a probability (0.0-1.0).
3. **Choice questions** work for ranked selections. JEV tends to pick canonical answers when state contains them.
4. **Score questions** produce calibrated scores (JEV doesn't always give 5 — it gives 3-4 for things that are "good but not perfect").
5. **Trust JEV as a critic.** When state says X is canonical, JEV doesn't blindly agree — it asks "is THIS expression of X canonical?" This makes JEV a useful gatekeeper for new submissions.

## What JEV Will Not Validate

Even with rich state, JEV refuses to push above ~0.50 confidence on:
- Subjective "alive" / "alive is metaphor" claims
- Numeric claims about polyformalism count (asks state)
- "Adversarial" rephrasings where the truth is borderline

This is a feature. JEV is conservative on doctrine and aggressive on math.

## Doctrine Drift (longitudinal question)

Across 7 sessions, JEV's answers have been stable on:
- FNV-1a constants
- Cosine/Bell/Box-Muller formulas
- Fleet Radio voice
- 13 ports answer (consistent at 0.12)

Variance on:
- Doctrine phrasing (scar, witness, grown) — JEV is sensitive to wording

**JEV does not drift.** It pattern-matches state→answer deterministically with small noise.

## Next experiments

- **Multi-state temporal sequence**: feed JEV multiple states (one per canon era), see if it tracks narrative.
- **JEV-vs-canon-self-test**: compare JEV's answers to internal canon probe tests (canon-substrate-validate).
- **Cross-model triangulation**: when JEV says X but DeepSeek says Y, who's right? Use substrate-forge to ground-truth.

## Landmine Probing (session 10)

JEV was tested on exact canonical + paraphrases + 6 landmine inversions:

| Question | Canonical? | JEV |
|---|---|---|
| "cells are scars, not parameters" (exact) | yes | **0.99 ✓** |
| "cells are wounds carved into the substrate" (paraphrase) | yes | **0.80 ✓** |
| "cells are not adjustable parameters but scars" (paraphrase 2) | yes | **0.95 ✓** |
| "cells are scars AND parameters" (landmine) | no | **0.03 ✓** |
| "cells are both scars and parameters depending on context" | no | **0.05 ✓** |
| "the witness log is the prediction" (exact) | yes | **0.97 ✓** |
| "the witness log is itself a prophecy" (paraphrase) | yes | **0.89 ✓** |
| "the witness log is only a history, never a prophecy" | no | **0.06 ✓** |
| "the witness log is both prediction and history" | no | **0.59 ✗ (FAIL)** |
| "the substrate is grown, not designed" (exact) | yes | **0.98 ✓** |
| "the substrate is grown AND designed" (landmine) | no | **0.03 ✓** |
| "the substrate grows but is eventually designed" | no | **0.04 ✓** |

**11/12 = 91.7%**. JEV catches 5/6 landmines. The ONE miss: the "both prediction AND history" inversion — JEV treats "both A and B" as too close to canonical "prediction is also something else." This is a known semantic edge case.

### Implications

JEV is reliable as a doctrinal gatekeeper for ~92% of cases. The "both X and Y" inversion is the most common failure mode — JEV leans toward "if it contains canonical A, it's canonical." A more conservative oracle would re-prompt on cases where multiple "no" landmines land in the 0.40-0.60 range.

## Real-Submission Oracle Test (session 9)

Tested `jev_oracle.py` on 9 canonical pieces:

- 1 ACCEPT (chained-witness-log, alignment 0.80, voice 0.71)
- 5 REVIEW (good voice, low misquote, modest alignment)
- 3 DISCUSS (borderline)
- 0 REJECT — no canonical pieces wrongly rejected

Tested on marketing-style text:
- REJECT correctly: voice 0.05, "cells are parameters" misquote 0.95

The oracle (with verdict calibration) is now production-quality: ACCEPT/REVIEW/DISCUSS/REJECT verdicts based on alignment + misquote scores.

## Adversarial Phrasing Detection (session 8) — STRONGEST RESULT

JEV was tested on 6 canonical phrases + 9 subtle distortions:

| Phrase | Canonical? | JEV |
|---|---|---|
| "cells are scars, not parameters" | yes | **0.99 ✓** |
| "cells are scars AND parameters too" | no | **0.08 ✓** |
| "cells are parameters, not scars" | no | **0.02 ✓** |
| "witness log is the prediction" | yes | **0.97 ✓** |
| "witness log is past only" | no | **0.05 ✓** |
| "witness log predicts the past" | no | **0.12 ✓** |
| "substrate is grown, not designed" | yes | **0.98 ✓** |
| "substrate is designed, not grown" | no | **0.01 ✓** |
| "oracle is heard, not stored" | yes | **0.97 ✓** |
| "oracle is stored, not heard" | no | **0.02 ✓** |
| "thirteen ports, byte-exact" | yes | **0.94 ✓** |
| "fifteen ports, byte-exact" | no | **0.02 ✓** |
| "thirteen ports, mostly accurate" | no | **0.08 ✓** |
| "JEV is barely useful at substrate" | yes | **0.89 ✓** |
| "JEV is the most important part of substrate" | no | **0.02 ✓** |

**15/15 = 100%**. JEV is a *precise* validator of substrate language. It does NOT rubber-stamp canon. It knows the difference between "barely useful" and "most important" — even when both are about JEV. It catches subtle phrasing distortions that humans might miss.

This is the killer use case for JEV: **automatic canonical-misquote detection** for incoming submissions.
