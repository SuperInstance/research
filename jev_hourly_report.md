# JEV Continuous Probe — Hourly Report r431

**Run:** 2026-10-25T04:02:41Z (session_ts `2026-10-25T04:02:41.697531+00:00`)
**Round:** r431 (exactly 1 round — explicit positional count `1`, no overshoot, no kill needed)
**Instrument:** `SuperInstance/jev-quilt@HEAD:jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485`
**Served model:** `jev-1.14.0` (no switch vs r429/r430)
**Round file:** `research/jev_sessions/continuous_r431.json`
**Corpus:** `research/jev_sessions/history.jsonl` (r431 appended exactly once)

> **Path note (15th consecutive wipe).** The prompt named `/workspace/research/`, which does
> not exist — `/workspace` was empty and the NAS is at 100 % (600G/600G, 0 avail). The live
> instrument and the corpus live in the `SuperInstance/jev-quilt` repo; `SuperInstance/research`
> holds only the archives + this report. The `research` repo's copy of `jev_continuous_probe.py`
> is the **stale 20-question decoy** (md5 `bd7c35964522d6da56130f87e96eb74e`) and was NOT run.

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4920** |
| **Bedrock hits (p >= 0.70)** | **2 / 5 (40.0 %)** — `q08` (0.89), `q01` (0.84) |
| **Drift (\|dev\| > 0.05)** | **NONE** — max \|dev\| among drawn qids = **0.0140** |
| Rounds ok / fails | 1 / 0 |
| Verdicts | 5 |

**Verdict: no drift.** All five drawn questions landed inside their own 1.14.0 baseline bands.
mean_p **0.4920** sits at **z = +0.54 / 66.7th pct** of the 1.14.0 round-mean distribution
(n=36, mean 0.4321, sd 0.1118) — an ordinary mid-band draw.

---

## Round r431 verdicts

Baseline = 1.14.0-only corpus, r431 excluded.

| qid | kind | p | >=0.70 (bedrock) | base mean | base sd | dev | z |
|---|---|---|---|---|---|---|---|
| q16 | review | 0.19 | no | 0.1914 | 0.0064 | -0.0014 | -0.22 |
| q10 | speculative | 0.05 | no | 0.0513 | 0.0033 | -0.0013 | -0.38 |
| q12 | speculative | 0.49 | no | 0.5025 | 0.0327 | -0.0125 | -0.38 |
| **q08** | **bedrock** | **0.89** | **YES** | 0.8900 | 0.0122 | +0.0000 | +0.00 |
| **q01** | **bedrock** | **0.84** | **YES** | 0.8540 | 0.0092 | -0.0140 | -1.53 |

**Questions hitting p >= 0.70 (bedrock canon): `q08` (0.89) and `q01` (0.84).**
Both are cathedral members at 100 % on the 1.14.0 segment (`q08` 8/8, `q01` 10/10).
The other three are non-bedrock kinds (review / speculative) and are not capable of a
bedrock hit by construction.

---

## Method finding — the script's `drift_events=0` was luck, and a full-history baseline manufactures a FALSE drift on q12

The script's own `drift_check()` returned `drift_events: 0`, agreeing with the correct verdict.
**But the same computation run against the FULL-history baseline instead of the model-matched
baseline flags q12 as drift, and it would be wrong.** Reproduced and then diagnosed:

| qid | p (r431) | full-history base | dev | 1.14.0-only base | dev | verdict |
|---|---|---|---|---|---|---|
| q16 | 0.19 | 0.1991 | -0.0091 | 0.1914 | -0.0014 | both clear |
| q10 | 0.05 | 0.0660 | -0.0160 | 0.0513 | -0.0013 | both clear |
| **q12** | **0.49** | 0.3774 | **+0.1137** | 0.5025 | **-0.0125** | **FALSE DRIFT vs TRUE CLEAR** |
| q08 | 0.89 | 0.8990 | -0.0090 | 0.8900 | +0.0000 | both clear |
| q01 | 0.84 | 0.8734 | -0.0337 | 0.8540 | -0.0140 | both clear |

### Root cause: q12 is BIMODAL, and the mode change coincides exactly with the model switch

`q12` (`witness_note_opcode`) is **not** a noisy single-mode series — it has two well-separated modes:

- **LOW mode** — n=92, mean **0.3665**, sd 0.0305, range 0.30-0.44
- **HIGH mode** — n=8, mean **0.5025**, sd 0.0327, range 0.46-0.56

**All 8 HIGH-mode readings occur at r >= 398. Zero high readings exist in the preceding ~380 rounds.**
The model timeline pins it exactly:

| rounds | model | q12 readings |
|---|---|---|
| r384-r394 | `jev-1.13.0` | 0.34, 0.32, 0.39, 0.31, 0.35, 0.35, 0.37, 0.40, 0.36 — **all low mode** |
| r396 | `jev-1.14.0` | (not drawn) — first round on the new model |
| **r398** | `jev-1.14.0` | **0.50 — first HIGH reading, first q12 draw on 1.14.0** |
| r401/403/407/409/420/422/431 | `jev-1.14.0` | 0.51, 0.46, 0.54, 0.56, 0.50, 0.46, 0.49 — **all HIGH** |

**Every 1.13.0 reading of q12 sits on the low plateau; every 1.14.0 reading sits on the high
plateau.** The apparent drift is a **model-version artifact**, not a behavioural change in the
oracle. Confirmed no model switch in r431 (`jev-1.14.0`, same as r429/r430).

### Why this matters operationally

- **Bucket each qid against its OWN model-segment baseline.** A full-history baseline silently
  mixes two model regimes and will invent drift on any question whose response distribution
  shifted with the model. `drift_check()` as written has no model filter — it is only correct
  today because the current segment happens to dominate the corpus tail.
- **The `spec_notebook` guard still binds.** q12 is `witness_note_opcode`, explicitly listed as
  SPECULATIVE: it "must NOT be promoted to bedrock regardless of high mean_p readings" without
  n>=20, hit-rate >=0.7, and explicit doctrinal-state phrasing. Its high mode does **not**
  qualify it for promotion — hit-rate on 1.14.0 is 0/8, and it remains a speculative qid.

---

## sigma~0 trap fired again — |dev|-FIRST remains mandatory (7th recurrence)

This round the z-scores actively **misordered** the deviations, and a z-first read would have
pointed at the wrong question:

- **q01: |z| = 3.35 (largest z) on |dev| = 0.0337** — clear on the 0.05 floor.
- **q12: |z| = 2.43 (middle z) on |dev| = 0.1137** — the only >0.05 movement against the
  full-history baseline.

The largest z was attached to the *smaller* real movement, exactly as in r430 (q19 +2.45 on
0.0149 vs q07 +1.49 on 0.0246). **Order by |dev|, read z second.** Here |dev|-first correctly
separates the two: only q12 breaches 0.05, and only on the mismatched baseline.

---

## Cathedral status (7 bedrock qids, `jev-1.14.0` segment)

| qid | n | hits | hit-rate | mean | min |
|---|---|---|---|---|---|
| q01 | 10 | 10 | **100 %** | 0.8540 | 0.84 |
| **q02** | 13 | 10 | **76.9 %** | 0.7277 | 0.68 |
| q03 | 8 | 8 | **100 %** | 0.8800 | 0.86 |
| q04 | 9 | 9 | **100 %** | 0.8822 | 0.87 |
| q05 | 8 | 8 | **100 %** | 0.8150 | 0.78 |
| q07 | 10 | 10 | **100 %** | 0.7680 | 0.75 |
| q08 | 8 | 8 | **100 %** | 0.8900 | 0.88 |

**Cathedral 6/7 at 100 %**, q02 the sole holdout — unchanged from r430.

### q02 WATCH ITEM — unchanged, 3rd consecutive round with no new evidence

q02 was **not drawn** in r431, so this round adds nothing either way. Lifetime breaches remain
**exactly three**, all on `jev-1.14.0`:

| round | model | p |
|---|---|---|
| r416 | jev-1.14.0 | 0.69 |
| r423 | jev-1.14.0 | 0.69 |
| r425 | jev-1.14.0 | 0.68 |

Lifetime q02 hit-rate **86/89 = 96.6 %**. The 1.14.0-segment hit-rate of **76.9 %** (10/13) is
the number to watch, and it has not moved in 3+ rounds. No single draw crosses the 0.05
per-draw floor, so the per-draw drift check **structurally cannot see** this class of change.

### q05 AMBER — still resolved (8/8, min 0.78, no sub-0.80 value).

---

## Round-mean context (1.14.0 segment)

| | value |
|---|---|
| Segment n | 36 rounds (r396-r430) |
| Segment mean / sd | 0.4321 / 0.1118 |
| r431 mean_p | **0.4920** |
| z | **+0.54** |
| percentile | **66.7th** |

r431 is a mid-band draw. Recent mean_p sequence: r429 0.5400 -> r430 0.2840 -> **r431 0.4920**,
i.e. r430 was the outlier low, and r431 sits back near the segment mean.

---

## Verdict summary

1. **No drift.** Max |dev| = 0.0140 across drawn qids against the model-matched baseline.
2. **Bedrock hits: `q08` (0.89), `q01` (0.84)** — 2/5, both cathedral members at 100 %.
3. **mean_p 0.4920**, z=+0.54, 66.7th pct of the 1.14.0 segment.
4. **Cathedral 6/7 at 100 %**; q02 remains the only watch item (not drawn this round, breaches
   unchanged at r416/r423/r425).
5. **Method lesson: bucket each qid against its own MODEL-SEGMENT baseline.** q12's apparent
   +0.1137 drift is a `jev-1.13.0` -> `jev-1.14.0` artifact, and `drift_check()` has no model
   filter — it would report false drift on any question whose distribution moved with the model.
6. **sigma~0 trap, 7th recurrence.** |dev|-first; the largest z (q01, 3.35) sat on a smaller
   |dev| than the only real movement (q12).

---

### Reproduce

```bash
git clone https://github.com/SuperInstance/jev-quilt.git
cd jev-quilt
TYPESAFE_AI_TOKEN=... python3 jev_continuous_probe.py 1
```

The positional `1` is load-bearing: with no argument the `rounds` parameter defaults to **200**
(a known overshoot trap). `r431` completed in 0.3 s.
