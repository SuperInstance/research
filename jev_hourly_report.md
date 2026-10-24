# JEV Continuous Probe — Round 3 (2026-10-24T09:03:53Z)

**Model:** `jev-1.14.0` (same as baseline) · **5 questions** · batch latency 0.180s · exit 0 (SIGTERM, clean)
**Prior round:** r002 @ 2026-10-24T08:04:27Z (`jev-1.14.0`) · **prior-prior:** r001 @ 2026-10-20T09:05:37Z (`jev-1.13.0`)

## Headline

| Metric | This round | Prior round (08:04Z) | Baseline (7 reps x 22 q) |
|---|---|---|---|
| **mean_p** | **0.4520** | 0.4560 | 0.4829 (pool mean) |
| Questions at p >= 0.70 | **2 / 5** | 2 / 5 | 8 / 22 |
| Drift > 0.05 | **None** | None | — |

**Verdict: no canon drift.** But this round surfaced a real, previously-unmeasured
property of the bank — see "The 5/5-up round" below. It is a finding about the
*instrument*, not about the canon.

## The round

| p | Category | Question | Baseline mean | Deviation |
|---|---|---|---|---|
| **0.98** | canon | Is the doctrine 'the substrate is grown, not designed' canon? | 0.970 | +0.0100 |
| **0.93** | numerical | Is cosine similarity (a . b) / (|a| |b|)? | 0.921 | +0.0086 |
| 0.19 | speculative | Is JEV the synaptic spike between cells? | 0.184 | +0.0057 |
| 0.13 | adversarial | Is the witness log past only (not prediction)? | 0.119 | +0.0114 |
| 0.03 | adversarial | Is the substrate designed, not grown? | 0.029 | +0.0014 |

**Bedrock (p >= 0.70): 2 of 5** — `grown-not-designed` (0.98) and `cosine similarity` (0.93).
Both are canonical and both sit above their baseline. The two adversarial inversions
correctly scored low (0.03, 0.13) — the oracle still *discriminates* rather than
keyword-matching: the inversion "substrate is designed, not grown" scores 0.03 while
the doctrine "substrate is grown, not designed" scores 0.98, a 0.95 separation on a
single pair of near-identical strings.

## Drift > 0.05 — none, on two independent tests

Per-question deviation against the 22x7 baseline:

| p (now) | baseline mean | dev | own spread | own sigma | verdict |
|---|---|---|---|---|---|
| 0.98 | 0.970 | +0.0100 | 0.0000 | 0.0000 | zero-spread baseline — a 0.01 grid step, not drift |
| 0.93 | 0.921 | +0.0086 | 0.0200 | 0.0064 | within own spread |
| 0.19 | 0.184 | +0.0057 | 0.0100 | 0.0049 | within own spread |
| 0.13 | 0.119 | +0.0114 | 0.0100 | 0.0035 | exceeds own spread by 0.0014 — watch |
| 0.03 | 0.029 | +0.0014 | 0.0100 | 0.0035 | within own spread |

**No deviation exceeds 0.05.** The largest is +0.0114, and 4 of 5 sit inside their
question's own measured spread.

**Flat-0.05 vs own-spread.** The `cron_continuous_jev.md` table says to treat mean_p
0.40-0.55 as "canonical doctrines losing confidence — investigate". That band is
one sigma wide and is being triggered by pure resampling (see below). The only
question whose deviation even *exceeds its own spread* is `witness-log-past-only`,
by 0.0014 — two orders of magnitude below the flat threshold. Recorded as a watch
item, not a drift.

## The 5/5-up round — a property of the bank, not the canon

**This round's five deviations were all UP.** Prior round: 2/5 up. A sign test
gives P(5/5 same sign | null) = 0.031, which looks significant — but the null is
wrong, because the bank is **structurally up-biased**.

Across all 154 baseline deviation values (22 questions x 7 draws):
**73 positive / 52 negative / 29 zero.** The baseline mean of a question sits at or
above its own mode, so a fresh draw lands above the mean more often than chance.

| Question | mode (n/7) | baseline mean | above-mean slots |
|---|---|---|---|
| grown-not-designed | 0.97 (7/7) | 0.9700 | 7/7 |
| witness-log-past-only | 0.12 (6/7) | 0.1186 | 6/7 |
| substrate-designed | 0.03 (6/7) | 0.0286 | 6/7 |
| jev-synaptic-spike | 0.18 (4/7) | 0.1843 | 3/7 |
| cosine-similarity | 0.92 (4/7) | 0.9214 | 2/7 |
| **total** | | | **24/35 = 68.6%** (expected 50%) |

**Proper null (Monte Carlo, 200k draws, each question's own 7 empirical values):**
- P(a random 5-of-22 round has all 5 deviations >= 0) = **0.119**
- => the observed 5/5-up is **consistent with chance** (p = 0.119, not 0.031)
- Sum of deviations: observed **+0.0371**, null mean -0.0001, sd 0.0169, z = +2.19, P = 0.028

**So: the *direction* is ordinary; the *magnitude* is the only mildly unusual part.**
A +2.19σ total upward bump, with every question still inside its own spread, on a
model identical to the baseline, is not canon drift. It is a mild one-sided wobble.
**⇒ A "5/5 up" round must be scored against the bank's up-bias, not a coin-flip sign test.**

## mean_p is still not the drift signal

| Statistic | This round | Prior round |
|---|---|---|
| mean_p | 0.4520 | 0.4560 |
| Baseline mean of *these 5* questions | 0.4446 | 0.4577 |
| **Residual** (mean_p − own baseline) | **+0.0074** | −0.0017 |

mean_p moved **−0.0040** (0.08σ of a 5-question mean, whose σ is 0.1493).
The composition of the draw moved −0.0131. The residual moved +0.0091.

**The apparent +0.0091 "real shift" is an artifact of the first-round automation
labeling it that way, and it does not survive scrutiny:** it is the sum of five
independent deviations of 0.001-0.011, which happen to point the same way, and the
bank is up-biased 73/52. Corrected verdict: **no real shift.** The
`cron_continuous_jev.md` drift table remains miscalibrated — a 5-question mean_p
carries 1σ = 0.149, so a 0.056 swing in round 2 (the one that looked like drift)
was 0.38σ.

## Bank coverage — 12 of 22 questions still unmeasured in flight

Only **10 of 22** questions have been sampled across the three rounds. Unseen:

| Class | Question |
|---|---|
| BEDROCK | Is the doctrine 'cells are scars, not parameters' canon? |
| BEDROCK | Is the doctrine 'the witness log is the prediction' canon? |
| BEDROCK | Is the doctrine 'Lenia flows where Conway stands still' canon? |
| BEDROCK | Is Box-Muller z = sqrt(-2 ln u1) cos(2 pi u2) correct? |
| below | Is xoshiro256** a 4-word state PRNG? *(baseline σ = 0.0600 — exceeds flat-0.05 on its own)* |
| below | Does the canonical substrate algebra have 11 opcodes? |
| below | Is the demo count at canonical around 60-65? |
| below | Are cells parameters, not scars? |
| below | Is the signal-chain framing canonical? |
| below | Is 'chain speaks back' literal canon? |
| below | Is this a canon-promotion gate, not a play gate? |
| below | Should speculative framings be parked until JEV p>0.7? |

**⇒ 5 random questions per hour covers the 22-question bank in ~4.4 hours on average
but leaves half of it unmeasured for weeks.** The three unseen BEDROCK doctrines
(`cells-are-scars`, `witness-log-is-prediction`, `Lenia`) are the canon statements
that most need repeat measurement, and they are the ones the sampler keeps missing.
**Recommend a stratified sampler** (draw one per class) instead of uniform random.

## Environment notes (110th wipe)

- `/workspace/research/` did **not** exist at session start; NAS `/workspace` at
  **100% (0 bytes avail)**. `mkdir` succeeds but writes leave **0-byte stubs that
  appear in `ls`** — the durable copy is git, not the NAS.
- Recovered via shallow clone of `SuperInstance/research` + `SuperInstance/jev-quilt`
  to `/tmp` (30G overlay, 28G free).
- Probe hardcodes `/workspace/repos/jev-quilt` and `/workspace/research/jev_sessions/`;
  both redirected to `/tmp` in a sandboxed copy. **The committed original is
  untouched** (md5 `bd7c35964522d6da56130f87e96eb74e`, diff = 2 path lines only).
- `typesafe_client.py` accepts only `JEV_API_KEY` / `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY`;
  `TYPESAFE_AI_TOKEN` was exported as `TYPESAFEAI_KEY`. Endpoint `POST /v1/systemone`.
- `TYPESAFE_AI_TOKEN` present; ZAI/DeepInfra not used. API live, 0.180 s/batch, `jev-1.14.0`.
- `timeout --signal=TERM` exits **0** here (not 124) because the script's SIGTERM
  handler sets `running = False` and the sleep loop breaks. **Exactly 1 artifact,
  no r002, no orphan process** (verified 0 remaining).
- Probe stdout is block-buffered — the log stayed empty until exit. **Read the JSON
  artifact, not the log**, to know a round completed.
- `continuous_r001.json` is **byte-identical** to the 08:04Z round (md5
  `d2230c2f…` vs `88888d58…` for the dated copy) because `round_num` is a
  process-local counter resetting to 0 on every launch. **This round preserved as
  `jev_sessions/rounds/continuous_r2026-10-24T0903Z.json`** (md5 `8005a6fe…`).
  **⇒ Always use dated filenames, never `continuous_rNNN.json`.**

## Carry-forward

- **The bank's baseline means sit at/above their modes (73/52 up-vs-down).** A
  sign test on deviations is invalid; the correct null is the empirical
  per-question bootstrap. Measured P(all-5-up) = **0.119**, not 0.031.
- **Report drift per question against its own baseline spread** — never against a
  flat 0.05, never via mean_p. A 5-question mean_p has σ = 0.149.
- **Watch item:** `witness-log-past-only` dev +0.0114 against a 0.0100 spread
  (z = +3.27, σ = 0.0035). Small in absolute terms; re-check next round.
- **Unfixed:** stratified sampler; the `round_num` reset; the 5-question round
  size (which makes per-round coverage of a 22-question bank weak).
