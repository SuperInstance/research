# JEV Continuous Probe — Hourly Report

**Round:** r422  ·  **Timestamp:** 2026-10-24T19:04:11Z  ·  **Session:** 120th wipe
**Instrument:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged since r397)
**Model:** `jev-1.14.0` (resolved from the round's `model` field) — **no model switch** vs r421
**Doctrinal state:** `framework, core_doctrine, architecture, fleet, spec_notebook, operational_doctrine` — byte-identical to r421
**Run:** 1 round OK, 0 fails, exit 0 (no timeout kill needed), 0.141 s/round

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.5060** |
| **Bedrock hits (p ≥ 0.70)** | **2 / 5** — `q08` 0.88, `q01` 0.85 |
| Below gate (this round) | `q12` 0.46, `q18` 0.25, `q09` 0.09 |
| **Drift > 0.05** | **1 marginal flag — `q12` (see below). No confirmed drift.** |
| Cathedral all-time | 650 / 651 = **99.85 %** |
| Corpus | 2,121 records / 22 qids (1,986 on 1.13.0, 135 on 1.14.0) |

---

## Verdicts drawn this round

| qid | p | Class | Same-model baseline (1.14.0) | dev | z | |dev| pctile | Verdict |
|---|---|---|---|---|---|---|---|---|
| q08 | 0.88 | bedrock | n=4 (too thin) | — | — | — | **no drift** (all-model range 0.87–0.91) |
| q01 | 0.85 | bedrock | mu 0.8567, sd 0.0094, n=6 | −0.0067 | −0.71 | 50 % | **no drift** |
| q12 | 0.46 | speculative | mu 0.5117, sd 0.0318, n=6 | **−0.0517** | **−1.62** | 83 % | **MARGINAL FLAG** |
| q18 | 0.25 | speculative | mu 0.2475, sd 0.0083, n=8 | +0.0025 | +0.30 | 0 % | **no drift** |
| q09 | 0.09 | speculative | n=1 (too thin) | — | — | — | **no drift** (all-model range 0.07–0.11) |

Drift was recomputed from the round archives — **not** taken from the script's own `drift_check()`, which is a *history* reporter that re-fires stale qids (known defect, unpatched). This round the script's `drift_events=0` happens to agree with the recomputation in that no *stale* qid was flagged, but the recomputation additionally surfaced the q12 flag the script missed.

### The q12 flag, honestly

`q12` (speculative: "witness_note is an opcode") reads **0.46**. Against its own 1.14.0 baseline (n=6, mu 0.5117) that is **|dev| = 0.0517, which does exceed the 0.05 floor**. Three things argue this is **not** a substrate shift:

1. **z = −1.62 only.** A ~1.6-sigma move is inside ordinary sampler jitter; the 0.05 floor fired, but the sigma test did not.
2. **0.46 is a REPEAT, not a new extreme** — identical to r403's 0.46. It is the joint-minimum of the 1.14.0 sample, reached before. Full 1.14.0 series: `r398 0.50 · r401 0.51 · r403 0.46 · r407 0.54 · r409 0.56 · r420 0.50 · r422 0.46`.
3. **It sits at the 83rd percentile of q12's own |dev| distribution** — elevated, not extreme. At n=6 the 0.05 absolute bar is mis-calibrated (31–69 % of these qids' own history already sits at/past 0.05 from the mean).

**Verdict: marginal flag, not confirmed drift.** q12 remains speculative and unpromoted — no speculative or adversarial qid has ever reached p ≥ 0.70 in the corpus (q12's all-time max is 0.56). Next q12 draw is the decider.

---

## Comparison to previous rounds (table regenerated from the archives, not a hand-typed draft)

| round | mean_p | bedrock | timestamp |
|---|---|---|---|
| r411 | 0.4240 | 2/5 | 2026-10-24T03:08:33Z |
| r412 | 0.5520 | 3/5 | 2026-10-24T04:04:32Z |
| r413 | 0.4540 | 2/5 | 2026-10-24T05:02:59Z |
| r414 | 0.2800 | 1/5 | 2026-10-24T06:04:12Z |
| r415 | 0.3860 | 1/5 | 2026-10-24T07:03:41Z |
| r416 | 0.2400 | 0/5 | 2026-10-24T10:03:50Z |
| r417 | 0.4180 | 2/5 | 2026-10-24T11:02:33Z |
| r418 | 0.1480 | 0/5 | 2026-10-24T12:03:32Z |
| r419 | 0.5380 | 3/5 | 2026-10-24T13:04:19Z |
| r420 | 0.3580 | 1/5 | 2026-10-24T14:01:35Z |
| r421 | 0.5540 | 3/5 | 2026-10-24T15:02:02Z |
| **r422** | **0.5060** | **2/5** | **2026-10-24T19:04:11Z** |

**last-20 mean_p:** `0.292 0.440 0.390 0.294 0.458 0.438 0.368 0.418 0.424 0.552 0.454 0.280 0.386 0.240 0.418 0.148 0.538 0.358 0.554 0.506`
**last-20 bedrock:** `1 2 2 1 2 2 1 2 2 3 2 1 1 0 2 0 3 1 3 2`

- last-20 mean_p: mu **0.3978**, sd 0.1042 → today's **z = +1.04**. Ordinary.
- 413 rounds total in the corpus.

### Class-mix (why mean_p is a property of the DRAW, not of the canon)

MC over 5-of-22 same-model qids, 200,000 draws: **E[mean_p] = 0.4003**, sd 0.1333.

| bedrock count | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| P | 8.66 % | 32.00 % | **37.99 %** | 17.89 % | 3.27 % | 0.19 % |

- **P(exactly 2 bedrock) = 37.99 %** — today's draw is the **single most likely outcome**.
- P(mean_p ≤ 0.506) = **0.766** (77th percentile) — a comfortably ordinary high-ish draw.
- Today's z against the MC = **+0.79**.

⇒ **mean_p 0.506 is an ordinary 2-bedrock draw.** A 2/5 result is uninformative, not strong.

---

## Standing watch items (both unchanged — no new evidence this round)

- **q02 — fragile cathedral member.** On 1.14.0: n=10, mu 0.7370, min 0.69, **9/10 ≥ 0.70**. All-time 86/87. The bedrock gate breach (a draw ≤ 0.70) has *not* been observed on 1.14.0, but the margin is one value wide. **q02 was not drawn this round.**
- **q05 — AMBER since r419.** 0.78 there was the only sub-0.80 value in its 1.14.0 sample (n=6, mu 0.8183, min 0.78). **q05 was not drawn this round**, so the item stays open with no new evidence.

---

## Cathedral (explicit qid list — never a `kind` tag)

| qid | this round | all-time |
|---|---|---|
| q01 | DRAWN 0.85 → **HIT** | 102/102 = 100 % |
| q02 | not drawn | 86/87 = 98.9 % |
| q03 | not drawn | 98/98 = 100 % |
| q04 | not drawn | 99/99 = 100 % |
| q05 | not drawn | 94/94 = 100 % |
| q07 | not drawn | 87/87 = 100 % |
| q08 | DRAWN 0.88 → **HIT** | 84/84 = 100 % |
| **total** | | **650/651 = 99.85 %** |

---

## Method notes / receipts

- **Bootstrap:** `/workspace` arrived empty (NAS 600G/600G, 0 avail) — the 12th consecutive time the prompt named an ephemeral `/workspace/research/` path. Rebuilt from git: `SuperInstance/research` + `SuperInstance/jev-quilt` into `/tmp/jevroot/`, symlinked into `/workspace/research` and `/workspace/repos/jev-quilt`. Round counter derived from disk (max of round files and `history.jsonl`) → start = 422.
- **One round, explicitly:** this is Variant A (`rounds` is a positional `sys.argv[1]` defaulting to 200), so the run was launched as `python3 jev_continuous_probe.py 1` rather than relying on `timeout 60` to stop a 200-round writer. `timeout 60` was still the ceiling; the run finished on its own in 0.3 s.
- **Credential mapping:** client reads `JEV_API_KEY` / `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY`; the vault holds `TYPESAFE_AI_TOKEN` ⇒ ran with `JEV_API_KEY="$TYPESAFE_AI_TOKEN"`.
- **TLS:** leaf valid (`notAfter Dec 25 2026`), default context verified `VERIFY OK TLSv1.3` ⇒ **no CA-bundle rebuild** (4th round running).
- **🔴 A DEDUP BUG FOUND AND CORRECTED IN THIS ROUND'S OWN ANALYSIS.** The first drift table keyed dedup on `(qid, p, ts)`, but the round file and `history.jsonl` carry **different `ts` for the same verdict**, so the same observation was counted twice — once in the baseline and once as "today". That made q12's baseline n=7 instead of n=6 and its dev read −0.0443 (clear) instead of −0.0517 (flag). **The corrected key is `(qid, p, round)`.** This is the same class as the r222/r223 finding: *dedup on a field that is not unique across sources corrupts the baseline in whichever direction the duplicate sits.*
- **σ≈0 guard:** |dev| was checked against the 0.05 floor **first**, every time. The largest |z| this round was q12 at −1.62 — which also happened to be the largest |dev|, so the trap did not fire.
- **Baselines are model-segmented.** The corpus spans the r396 `jev-1.13.0 → jev-1.14.0` boundary; pooling across it inflates sigma and manufactures supra-threshold z on sub-threshold shifts (measured in r413). Every baseline above is 1.14.0-only.
- **History table regenerated programmatically** from `rounds/*.json` + `history.jsonl` — the r6 lesson that a hand-typed comparison table is a hand-typed claim.
