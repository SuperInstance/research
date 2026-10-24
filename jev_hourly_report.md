# JEV Continuous Probe — Round 2 (2026-10-24T08:04:27Z)

**Model:** `jev-1.14.0` · **5 questions** · batch latency 0.101s · exit 124 (timeout, by design)
**Prior round:** r001 @ 2026-10-20T09:05:37Z, `jev-1.13.0`

## Headline

| Metric | This round | Prior round | Baseline (7 reps x 22 q) |
|---|---|---|---|
| **mean_p** | **0.4560** | 0.4000 | 0.4829 (pool mean) |
| Questions at p >= 0.70 | **2 / 5** | 2 / 5 | 8 / 22 |
| Drift > 0.05 | **None** | n/a (single prior) | — |

## The round

| p | Category | Question |
|---|---|---|
| **0.95** | canon | Is the doctrine 'the oracle is heard, not stored' canon? |
| **0.93** | numerical | Is cosine similarity (a . b) / (|a| |b|)? |
| 0.24 | cross | Is substrate-canon validated by both JEV and writers' room? |
| 0.09 | cross | Does the canon require multi-LLM agreement for promotion? |
| 0.07 | size | Does the canonical substrate have 13 polyformalism ports? |

## Drift > 0.05 — none, and the reason matters

Per-question against a 7-rep baseline, only 2 of the 5 questions have a prior
value from the earlier round; the other 3 are first sightings. Every comparable
deviation is far inside threshold:

| p (now) | baseline mean | deviation | question's own same-run spread | verdict |
|---|---|---|---|---|
| 0.93 | 0.921 | +0.0086 | 0.0200 | ok |
| 0.95 | 0.956 | −0.0057 | 0.0100 | ok |
| 0.24 | 0.249 | −0.0086 | 0.0100 | ok |
| 0.09 | 0.096 | −0.0057 | 0.0100 | ok |
| 0.07 | 0.067 | +0.0029 | 0.0100 | ok |

**Max |dev| = 0.0086.** No question moves more than 0.01.

## The +0.056 mean_p move is 100% a sampling artifact

mean_p went 0.4000 -> 0.4560 (+0.056), which looks like drift. It is not.

- This round's 5 questions have a **baseline mean of 0.4577**; it scored 0.4560. Residual **−0.0017**.
- The prior round's 5 questions have a **baseline mean of 0.4017**; it scored 0.4000. Residual **−0.0017**.
- Observed delta **+0.0560** vs baseline delta **+0.0560** — the two agree to 4 decimals.
- **0.0% of the mean_p move is unexplained.** The delta is produced entirely by
  `random.sample(QUESTION_BANK, 5)` drawing a different set of questions.

Monte Carlo, 200k random 5-of-22 draws from the baseline means:

| statistic | value |
|---|---|
| p50 of \|mean_p difference\| between two independent draws | 0.4769 |
| p90 | 0.6757 |
| p99 | 0.8217 |
| P(\|delta\| >= observed 0.0560) | **1.000** |
| empirical sd of a 5-question mean | 0.1480 |

The observed +0.056 is **0.38 sigma**. A 5-question mean_p has a 1-sigma of 0.148
because the bank mixes 8 bedrock items (0.78-0.97) with 14 deliberate negatives
(0.03-0.65). **mean_p across rounds is not a drift signal at this sample size.**

## The oracle's own jitter vs the 0.05 threshold

Same question, identical state, 5-7 independent draws:

| question | min | max | spread | sigma |
|---|---|---|---|---|
| Is cosine similarity (a . b) / (\|a\| \|b\|)? | 0.910 | 0.930 | 0.0200 | 0.0064 |
| Is xoshiro256** a 4-word state PRNG? | 0.590 | 0.650 | **0.0600** | 0.0177 |
| Is the doctrine 'the oracle is heard, not stored' canon? | 0.950 | 0.960 | 0.0100 | 0.0049 |
| Does the canonical substrate have 13 polyformalism ports? | 0.060 | 0.070 | 0.0100 | 0.0045 |
| Does the canon require multi-LLM agreement for promotion? | 0.090 | 0.100 | 0.0100 | 0.0049 |

**`xoshiro256**` alone exceeds the 0.05 drift threshold on a single draw**, with no
canon change at all. A single-draw comparison against 0.05 will manufacture false
drift on that question. Every other question's jitter is <= 0.02.

## 🔴 Probe design defect: STATE seeds the answer it is asked to grade

The probe sends this state:

```python
STATE = {'fleet_radio_seed': 'xochitl',
         'canonical_substrate': {'doctrines': [
             'Cells are scars, not parameters.',
             'The witness log is the prediction.',
             'The substrate is grown, not designed.',
             'Lenia flows where Conway stands still.',
             'The oracle is heard, not stored.']}}
```

Five of the 22 bank questions are literally *"Is the doctrine 'X' canon?"* — and
every one of those five doctrine sentences is **already in the STATE payload**.
Measured directly, same question, 5 draws each:

| state | p (mean) |
|---|---|
| full state (doctrines included) | **0.958** |
| bare state (doctrines removed) | **0.352** |

A **0.61 swing** from the state alone. `JEV_LEARNINGS.md` records this question at
0.48 with the note *"even when state has it"* — the 0.956 measured here is the
same effect, and the probe is measuring it on every round.

Consequence: the 5 doctrine questions score high **because the answer is in the
prompt**, not because JEV independently recognises the doctrine. The "bedrock
canon" count of 8/22 in the baseline is inflated by up to 5 items. The 3 numerical
questions (0.78-0.92) are the only bedrock hits not contaminated this way.

## 🴴 The prior report's "5 of 23" is a miscount

`QUESTION_BANK` contains **22** entries (verified two ways: a regex over the
literal block and a line scan of the source; both return 22, and
`cron_continuous_jev.md` itself says "a 22-question bank"). The prior report
states 23. Minor, but it means the sampling denominator was never confirmed.

## ✅ "13 polyformalism ports" at 0.07 is a true negative, not a probe bug

Corroborated by the repo's own prior investigation (`JEV_LITERAL_MINDING_RESULTS.md`),
which tried 8 phrasings of "13 ports" and got a mean of 0.096 (range 0.02-0.18) —
this round's 0.067 is right in that band. The same file's header reads:
*"Even with 8 different phrasings, JEV consistently rejects '11 opcodes' and
'13 ports'. It's NOT a phrasing problem."* The 0.07 is the oracle being correct.

Note the irony: the "13 polyformalism ports" question is one of the few that
does **not** leak through STATE, because the answer is not in the state payload.

## Baseline built for future rounds (7 reps x 22 questions, jev-1.14.0)

Full bank, mean over 7 draws each, model `jev-1.14.0`:

| mean | spread | category | question | class |
|---|---|---|---|---|
| 0.970 | 0.000 | canon | Is the doctrine 'the substrate is grown, not designed' canon? | BEDROCK |
| 0.960 | 0.000 | canon | Is the doctrine 'cells are scars, not parameters' canon? | BEDROCK |
| 0.960 | 0.000 | canon | Is the doctrine 'the witness log is the prediction' canon? | BEDROCK |
| 0.956 | 0.010 | canon | Is the doctrine 'the oracle is heard, not stored' canon? | BEDROCK |
| 0.950 | 0.020 | canon | Is Lenia flows where Conway stands still canon? | BEDROCK |
| 0.921 | 0.020 | numerical | Is cosine similarity (a . b) / (\|a\| \|b\|)? | BEDROCK |
| 0.909 | 0.020 | numerical | Is Box-Muller z = sqrt(-2 ln u1) cos(2 pi u2) correct? | BEDROCK |
| 0.779 | 0.040 | numerical | Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis? | BEDROCK |
| 0.651 | 0.040 | canon | Is this a canon-promotion gate, not a play gate? | below |
| 0.620 | **0.060** | numerical | Is xoshiro256** a 4-word state PRNG? | below |
| 0.394 | 0.040 | speculative | Should speculative framings be parked until JEV p>0.7? | below |
| 0.316 | 0.040 | speculative | Is the signal-chain framing canonical? | below |
| 0.249 | 0.010 | cross | Is substrate-canon validated by both JEV and writers' room? | below |
| 0.204 | 0.020 | size | Is the demo count at canonical around 60-65? | below |
| 0.184 | 0.010 | speculative | Is JEV the synaptic spike between cells? | below |
| 0.130 | 0.020 | size | Does the canonical substrate algebra have 11 opcodes? | below |
| 0.121 | 0.020 | speculative | Is 'chain speaks back' literal canon? | below |
| 0.119 | 0.010 | adversarial | Is the witness log past only (not prediction)? | below |
| 0.096 | 0.010 | cross | Does the canon require multi-LLM agreement for promotion? | below |
| 0.067 | 0.010 | size | Does the canonical substrate have 13 polyformalism ports? | below |
| 0.040 | 0.000 | adversarial | Are cells parameters, not scars? | below |
| 0.029 | 0.010 | adversarial | Is the substrate designed, not grown? | below |

Pool mean over all 22 = **0.4829**. Bedrock (mean >= 0.70) = **8/22**.

The adversarial inversions score 0.029-0.119 and the doctrinal questions
0.950-0.970: the oracle is **discriminating**, not keyword-matching.

## What the "drift" table in cron_continuous_jev.md gets wrong

`cron_continuous_jev.md` maps mean_p to a status:

| Mean p across rounds | Status |
|---|---|
| 0.70 - 0.80 | canon is bedrock, no drift |
| 0.55 - 0.70 | canon still strong, but new ambiguities surfacing |
| 0.40 - 0.55 | canonical doctrines losing confidence — investigate |
| < 0.40 | major drift |

**This table cannot work as written.** The 5-question mean_p has a 1-sigma of
0.148, so the 0.40-0.55 band (width 0.15) is one sigma wide and the "investigate"
band is routinely entered by pure resampling. The two rounds measured here
land in that "investigate" band (0.4000 and 0.4560) while every single
per-question deviation is under 0.01. **The table is reading sampling noise as
doctrine erosion.**

## Recommendations, in priority order

1. **Stop reporting mean_p as the drift signal.** Report per-question deviation
   against a stored per-question baseline, and require a deviation to exceed
   **the question's own same-run spread** (not a flat 0.05) to count.
2. **Fix or annotate the STATE leak.** Either drop the `canonical_substrate`
   doctrines from STATE and ask cold, or keep STATE and stop counting the five
   "is this doctrine canon?" questions as evidence of bedrock. A 0.61 swing
   from the prompt is not a measurement of the oracle.
3. **Derive `round_num` from artifacts, not from zero.** The counter is
   process-local and resets each launch; combined with the unseeded
   `random.sample`, every restart overwrites `continuous_r001.json` and destroys
   history. This is still unfixed from the prior round's report.
4. **Use a fixed or stratified sample.** Draw the same 5 qids every round, or
   stratify across categories, so mean_p becomes comparable round to round.
   Then a moving mean_p means something again.
5. **Use the stored baseline** (`baseline_22x7.json`, committed alongside) to
   seed round comparisons, and re-derive it when the model version changes.
6. **Report the model version per round** — this round is `jev-1.14.0`, the
   prior round was `jev-1.13.0`. Pooling across that cut would manufacture
   drift on exactly the questions that moved.

## Method notes / how this was produced

- The prior round's artifact was read from git (`SuperInstance/research`,
  commit `bcf2db6`); `continuous_r001.json` is the only continuous artifact ever
  committed, on any branch, in that repo's history.
- This round was produced by the **unmodified** `jev_continuous_probe.py`
  (md5 `bd7c35964522d6da56130f87e96eb74e`) with exactly two path lines
  redirected out of the dead `/workspace` tree; a `diff` against the committed
  original is included in the run log. Sampling logic, question bank, state,
  and scoring are untouched.
- The round was bounded by `timeout --signal=TERM 60`, which the script handles
  gracefully ("stopped after 1 rounds"), so exactly one round was written and
  no orphan process remains. Verified: 1 artifact, no `continuous_r002.json`,
  no live process.
- `TYPESAFE_AI_TOKEN` was exported as `TYPESAFEAI_KEY` because
  `typesafe_client.py` accepts only `JEV_API_KEY` / `TYPESAFE_API_KEY` /
  `TYPESAFEAI_KEY` — the credential was present and valid all along.
- The `p` value is the `noul` probability from the API; `confidence` is the
  same number when the API omits it.
