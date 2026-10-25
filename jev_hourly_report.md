# JEV Continuous Probe — Hourly Report r430

**Run:** 2026-10-25T03:03:58Z (session_ts `2026-10-25T03:03:58.147213+00:00`)
**Round:** r430 (exactly 1 round — explicit positional count `1`, no overshoot)
**Instrument:** `SuperInstance/jev-quilt@HEAD:jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485`
**Served model:** `jev-1.14.0` (no switch vs r429)
**Round file:** `research/jev_sessions/continuous_r430.json` md5 `7e3b832d80f3dba33b4cebb39835e8b5`
**Corpus:** `research/jev_sessions/history.jsonl` md5 `ccc3077dd7d83ea9fb11d6be234ee87d` (434 records, r430 appended exactly once)

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.2840** |
| **Bedrock hits (p >= 0.70)** | **1 / 5 (20.0 %)** — `q07` only |
| **Drift (\|dev\| > 0.05)** | **NONE** — max \|dev\| among drawn qids = **0.0246** |
| Rounds ok / fails | 1 / 0 |
| Verdicts | 5 |

**Verdict: no drift.** Every drawn question landed inside its own historical band. The low
mean_p is a **draw-composition effect, not a behavioural change** — 4 of 5 drawn qids were
speculative/review/adversarial, whose corpus bands sit at 0.10-0.20 by construction.

---

## Round r430 verdicts

| qid | kind | p | >=0.70 (bedrock) | prior mean | prior sd | dev | z |
|---|---|---|---|---|---|---|---|
| q11 | speculative | 0.20 | no | 0.1843 | 0.0181 | +0.0157 | +0.87 |
| **q07** | **bedrock** | **0.78** | **YES** | 0.7554 | 0.0165 | +0.0246 | +1.49 |
| q22 | speculative | 0.14 | no | 0.1204 | 0.0084 | +0.0196 | +2.34 |
| q16 | review | 0.18 | no | 0.1993 | 0.0082 | -0.0193 | -2.34 |
| q19 | adversarial | 0.12 | no | 0.1051 | 0.0061 | +0.0149 | +2.45 |

**Questions hitting p >= 0.70 (bedrock canon): `q07` only (0.78).**
`q07` is a bedrock member at **90/90 = 100 %** lifetime hit-rate (range 0.71-0.79) — the
cathedral holds. The other four are non-bedrock kinds; none of them is capable of a
bedrock hit, so 1/5 is the **maximum attainable** for this draw.

### sigma~0 trap fired again — |dev|-first was load-bearing
The three largest z-scores this round (q19 **+2.45**, q22 **+2.34**, q16 **-2.34**) all sit on
**|dev| <= 0.0246**, far under the 0.05 floor. Conversely the **largest |dev| (q07, 0.0246)
carries the *smallest* z (+1.49)**. Ranking by z would have flagged the wrong question;
ranking by |dev| correctly finds zero drift. This is the 6th recurrence of the trap.

---

## Comparison to prior rounds

### Against the jev-1.14.0 segment (35 rounds, r396-r430)
- segment mean_p = **0.4304**, sd = 0.1146, range 0.15-0.66
- r430 mean_p 0.2840 -> **z = -1.28**, **11.4th percentile** of the segment
- r430 is among the lowest mean_p values in the 1.14.0 segment — but a single 5-question
  draw with 4 non-bedrock qids reaches this band routinely, and **z = -1.28 is well inside 2 sigma**.

### Recent round trend (r419-r430)
```
r419 0.538 (3/5)   r420 0.358 (1/5)   r421 0.554 (3/5)   r422 0.506 (2/5)
r423 0.526 (2/5)   r424 0.376 (2/5)   r425 0.356 (1/5)   r426 0.404 (2/5)
r427 0.420 (2/5)   r428 0.376 (1/5)   r429 0.540 (3/5)   r430 0.284 (1/5)
```
The series is **draw-mix driven, not trending** — the six rounds before r429 average 0.466,
r429 jumped to 0.540 on a 3-bedrock draw, and r430 fell to 0.284 on a 1-bedrock draw. The
swing is fully explained by *which* questions were sampled.

### Round-level drift check
The script's own `drift_check()` returned **`[]` (empty)** — and this time that agrees with
the independently recomputed per-qid analysis restricted to qids actually drawn. No stale
re-fire occurred in this round.

---

## Bedrock canon status (all 7 bedrock qids, lifetime corpus)

| qid | n | mean | sd | hit-rate | status |
|---|---|---|---|---|---|
| q04 | 101 | 0.8882 | 0.0092 | **100 %** | OK cathedral |
| q03 | 100 | 0.8857 | 0.0097 | **100 %** | OK cathedral |
| q08 | 88 | 0.8990 | 0.0093 | **100 %** | OK cathedral |
| q01 | 105 | 0.8737 | 0.0101 | **100 %** | OK cathedral |
| q05 | 97 | 0.8484 | 0.0148 | **100 %** | OK cathedral |
| q07 | 90 | 0.7557 | 0.0165 | **100 %** | OK cathedral — hit again this round (0.78) |
| q02 | 90 | 0.8107 | 0.0384 | **96.7 %** | **WATCH** — 3 sub-0.70 breaches (r416 0.69, r423 0.69, r425 0.68) |

**Cathedral: 6/7 at 100 %.** The one exception remains **q02**, unchanged from r429: 87/90
hits, three breaches all >= 0.05 below the 0.70 line but all *within* q02's own 0.68-0.86
corpus range. **q02 was not drawn this round**, so r430 adds no new evidence either way.

**q05 AMBER remains RESOLVED** — 97/97 at 100 %, no sub-0.80 value since the r419/r423/r425
episodes were cleared.

---

## Method notes (this run)

1. **The prompt's script path was a decoy — 110th consecutive wipe.** `/workspace/research/`
   did not exist (NAS 600G/600G, 0 bytes available). The live instrument is
   `SuperInstance/jev-quilt` (md5 `3a255fa4...`, 22-qid `q01..q22` bank); the
   `SuperInstance/research` copy (md5 `bd7c3596...`) is the stale 20-question prose bank.
   Both were md5-checked before use; the archives' own `script_md5` stamp matched `3a255fa4`.
2. **`timeout 60 python3 jev_continuous_probe.py` would have run 200 rounds.** The positional
   `rounds` arg defaults to `200`. Launched as `... jev_continuous_probe.py 1` -> exactly one
   round, r430, 0.3 s wall clock, no kill needed. (The 55 s internal ceiling never engaged.)
3. **The NAS 0-byte write trap is live.** A 5-byte write to `/workspace` returned exit 0 and
   produced a **0-byte file** (md5 `d41d8cd9...`). The report was therefore authored in `/tmp`
   and transported by **git**, not by filesystem write.
4. **Round counter derived from MAX(files, history)** = 429 -> start 430. `history.jsonl`
   contains historical duplicate round numbers (384, 385-391) from the pre-r229 reissue
   defect; the max-based counter is unaffected. r430 appears **exactly once** in history.
5. **Model-switch check:** r430 served `jev-1.14.0`, identical to r429 — no silent model
   change. (399 historical rounds were `jev-1.13.0`; the segment split is real, so segment-
   relative comparison is the correct frame.)
6. **Drift verdict is aggregate and own-qid-relative**, never a single-question z, and never
   the script's raw `drift_events` count.

---

## Bottom line

**mean_p 0.2840 | bedrock hits 1/5 (q07 = 0.78) | drift NONE (max |dev| 0.0246).**
The round is clean. The low mean_p is a sampling artefact of a 1-bedrock draw, not a
canon regression. Cathedral intact at 6/7; q02 remains the only watch item and was not
drawn. No action required beyond the standing q02 watch.
