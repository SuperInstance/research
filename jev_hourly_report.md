# JEV continuous probe — round r446 hourly report

**Generated:** 2026-10-25T20:06:00+00:00
**Round:** r446 (ts 2026-10-25T20:04:19.294124+00:00), elapsed 0.126 s
**Resolved model:** `jev-1.14.0` (segment n=55 rounds, r396..r446)
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (root probe; `research/` copy is the launcher wrapper `2bdd4768`)
**Corpus:** `SuperInstance/jev-quilt` @ `7d0a4a6` (live) — 445 distinct rounds r1..r446, 4,200 deduped `(qid,p,round)` verdicts, 22 live qids
**Prior report:** archived as `jev_hourly_report_r445.md`

---

## 1. Headline

| metric | value |
|---|---|
| **mean_p** | **0.4240** |
| **bedrock (p >= 0.70)** | **2/5** drawn qids — q08 0.90, q03 0.88 |
| **drift (recomputed)** | **NONE** — 0 of 5 drawn qids exceed \|dev\| 0.05 |
| script's own `drift_events` | 1 — on **q12, NOT drawn this round** (21st repro, 8 rounds stale) |
| cathedral (7 bedrock qids, segment) | 98/101 = **97.0 %** — 6 of 7 at 100 % |
| MC E[mean_p] / P(mean_p <= 0.4240) | 0.4975 (sd 0.1426) / **0.3132** |
| modal bedrock count | **2** (36.7 %) — today's 2/5 is the modal outcome |

---

## 2. This round's draw

| qid | kind | p | bedrock? |
|---|---|---|---|
| q08 | bedrock | **0.90** | **YES** |
| q03 | bedrock | **0.88** | **YES** |
| q13 | speculative | 0.17 | — |
| q09 | speculative | 0.09 | — |
| q20 | speculative | 0.08 | — |

mean_p = (0.90 + 0.88 + 0.17 + 0.09 + 0.08) / 5 = **0.4240**

Two cathedral qids cleared the p >= 0.70 gate, both of them cathedral members at 100 % on the segment. The three speculative draws sit exactly where their own baselines put them. No qid was drawn at a value outside its segment range.

**Straddler audit (required before publishing a hit count):** q08 0.90 and q03 0.88 are both *well* clear of the gate — the low edge of q03's segment range is 0.86 and q08's is 0.88, so neither is a boundary case. **No straddler contributed to this round's count.** The 2/5 is a clean 2, not 2-plus-a-lucky-boundary. (Contrast r433, where q17 at 0.73 turned a 2/5 into a 3/5.)

---

## 3. Drift — recomputed properly

Baseline = **per-qid, current-model segment** (`jev-1.14.0`), restricted to the 5 qids actually drawn. |dev| first, sigma second.

| qid | kind | p | n | mu | sd | dev | z | verdict |
|---|---|---|---|---|---|---|---|---|
| q08 | bedrock | 0.90 | 13 | 0.8900 | 0.0111 | +0.0100 | +0.90 | clear |
| q03 | bedrock | 0.88 | 14 | 0.8829 | 0.0122 | -0.0029 | -0.23 | clear |
| q13 | speculative | 0.17 | 13 | 0.1585 | 0.0095 | +0.0115 | +1.22 | clear |
| q09 | speculative | 0.09 | 9 | 0.0922 | 0.0131 | -0.0022 | -0.17 | clear |
| q20 | speculative | 0.08 | 17 | 0.0894 | 0.0121 | -0.0094 | -0.78 | clear |

**Aggregate verdict: 0 of 5 drawn qids exceed |dev| 0.05 -> DRIFT NONE.** Max |dev| = 0.0115 (q13) — well inside the band.

### 3.1 The sigma-approx-0 trap, 8th recurrence (q13)

q13's **pooled** z is **+3.14** (n=102, mu 0.1362, sd 0.0108) — the largest z of the round, and it sits on a pooled |dev| of only 0.0338. Against its own `1.14.0` segment (n=13, mu 0.1585) the same 0.17 reads **dev +0.0115, z +1.22** — squarely on baseline. The pooled z fuses the `1.13.0` -> `1.14.0` model artifact into the current signal. **|dev| first, z second** — the largest z is routinely the smallest real movement. 11 of 13 prior segment observations sit at or below 0.17 (segment max = 0.17, so it ties the high but never exceeds it). Archive alone settles it: no re-measurement warranted.

### 3.2 Pooled baseline would NOT have false-flagged any qid this round

| qid | p | pooled n | pooled mu | pooled dev | pooled z | segment dev | segment z |
|---|---|---|---|---|---|---|---|
| q08 | 0.90 | 90 | 0.8982 | +0.0018 | +0.18 | +0.0100 | +0.90 |
| q03 | 0.88 | 103 | 0.8856 | -0.0056 | -0.58 | -0.0029 | -0.23 |
| q13 | 0.17 | 102 | 0.1362 | +0.0338 | +3.14 | +0.0115 | +1.22 |
| q09 | 0.09 | 95 | 0.0780 | +0.0120 | +1.55 | -0.0022 | -0.17 |
| q20 | 0.08 | 99 | 0.1024 | -0.0224 | -1.91 | -0.0094 | -0.78 |

The r428 trap (pooled baseline false-flagging q14) did **not** fire this round — no qid crosses 0.05 on either baseline. Worth stating: the segment baseline remains the correct instrument, and today it happens to be the conservative one.

### 3.3 The script's own `drift_events=1` is the 21st repro of a stale-event defect

```
[{"qid": "q12", "recent_p": 0.54, "prior_median": 0.49, "delta": 0.05}]
```

- **q12 was NOT drawn in r446.** Its last observation was **r438** — this event is **8 rounds stale**.
- `drift_check()` (jev_continuous_probe.py:317) takes `samples[-1][1]` for **every** qid, so it re-reports a qid that was not measured this round.
- The delta is **exactly 0.05** — a boundary float case, not a breach.
- q12 is a flat plateau: segment n=15, mu 0.4813, med 0.5000, range 0.30-0.56, **never crossed 0.70** (0/105 in segment).

**FIX (unchanged, still open): `drift_check` must only consider qids present in the current round's verdict set.** Until that lands, the script's `drift_events` field must be recomputed by hand before it is quoted.

---

## 4. Cathedral (bedrock qids, `jev-1.14.0` segment)

| qid | hits | rate | mu | sd | min | max |
|---|---|---|---|---|---|---|
| q01 | 14/14 | **100.0 %** | 0.8550 | 0.0098 | 0.84 | 0.87 |
| q03 | 14/14 | **100.0 %** | 0.8829 | 0.0122 | 0.86 | 0.90 |
| q04 | 14/14 | **100.0 %** | 0.8829 | 0.0128 | 0.86 | 0.91 |
| q05 | 14/14 | **100.0 %** | 0.8193 | 0.0198 | 0.78 | 0.86 |
| q07 | 15/15 | **100.0 %** | 0.7660 | 0.0178 | 0.74 | 0.79 |
| q08 | 13/13 | **100.0 %** | 0.8900 | 0.0111 | 0.88 | 0.91 |
| **q02** | **14/17** | **82.4 %** | 0.7406 | **0.0447** | **0.68** | 0.84 |

**Cathedral total: 98/101 = 97.0 %.** Six of seven at 100 %.

**q02 remains the sole watch item, and remains ESCALATED.** Its three sub-gate readings are the *same three* as before — r416 0.69, r423 0.69, r425 0.68 — hair-under-gate misses, **no new breach**. Its sd (0.0447) is ~4-5x every other cathedral qid, so q02 is not a stable 82 %; it is a qid whose distribution straddles the 0.70 gate and occasionally lands under it. Per the standing rule: **ESCALATE, do not promote, do not call drift** — the 0.05 floor is not breached. What would move it to a genuine drift finding: a **4th** q02 breach, or a breach from **any other** cathedral qid.

---

## 5. Speculative / adversarial — still never

**0 of 1,358** speculative-or-adversarial observations have ever reached p >= 0.70, across 445 rounds. Not one. The three speculative draws today (q13 0.17, q09 0.09, q20 0.08) are nowhere near it.

**q17 (`review`) is excluded from every such claim** — it is not bedrock, and it is the only non-bedrock qid that ever crosses 0.70 (segment 10/13 = 76.9 %, range 0.68-0.75). It was not drawn this round.

---

## 6. Is 0.4240 mean_p / 2-of-5 meaningful? (the class-mix lottery)

`mean_p` is a **class-mix lottery over a 5-of-22 draw**, not a health verdict. Monte-Carlo, 200,000 draws from the per-qid `1.14.0` segment pools:

- E[mean_p] = **0.4975**, sd 0.1426
- **P(mean_p <= 0.4240) = 0.3132** — today sits in the lower third, well within ordinary spread
- P(bedrock hits): 0 -> 7.2 %, 1 -> 27.0 %, **2 -> 36.7 % (modal)**, 3 -> 22.4 %, 4 -> 6.0 %, 5 -> 0.6 %

**2/5 is the modal outcome.** Today's 2 bedrock hits and 0.4240 mean_p are the unremarkable centre of the distribution, not a signal in either direction.

Full-series context (5-draw rounds only, n=244): mu 0.3866, median 0.3990, sd 0.1452. **z_series = +0.26, rank 153/244 (62.7th pct).** Bedrock-count distribution over the series: 0 x27, 1 x86, **2 x86**, 3 x38, 4 x5, 5 x2.

Segment series (n=55): mu 0.4151, sd 0.1141, median 0.4180 -> **z_segment = +0.08**, rank 31/55 (56.4th pct).

Last 12 segment rounds: r435 0.3220 · r436 0.4260 · r437 0.2200 · r438 0.4900 · r439 0.4020 · r440 0.4180 · r441 0.4040 · r442 0.3520 · r443 0.4500 · r444 0.5460 · r445 0.3080 · **r446 0.4240**. No trend; r446 lands mid-band.

---

## 7. Verdict

**No drift. No new breach. No promotion.** r446 is an ordinary, well-centred round:

- mean_p **0.4240**, 2/5 bedrock (q08 0.90, q03 0.88) — the modal outcome
- **0 of 5** drawn qids beyond |dev| 0.05 against their own-model segment; max |dev| 0.0115
- The script's `drift_events=1` is a **stale q12 event, 8 rounds old, not drawn this round** (21st repro)
- Cathedral **97.0 %**, six of seven at 100 %; **q02 82.4 %** — the same three hair-under-gate misses, no new one
- **0/1,358** speculative or adversarial observations have ever reached 0.70
- q13's pooled z +3.14 is the sigma-approx-0 trap, not a movement (segment dev +0.0115)

**Standing watch item: q02** (ESCALATED — 4th breach would be a real drift finding).

---

## 8. Method and environment

- **One round, correctly.** `rounds` is a **positional** arg on the root script and defaults to **200**; the literal `timeout 60 python3 jev_continuous_probe.py` (no arg) would have raced the writer to flush ~154 rounds, not one. Ran `python3 jev_continuous_probe.py 1` -> exactly 1 round in 0.126 s, 0 fails, 5 verdicts. The requested command shape is not the requested behaviour.
- **Script placement.** `SESSION_DIR` resolves relative to the script file (`<script_dir>/research/jev_sessions`), so the root script must stay at the repo root; `research/jev_continuous_probe.py` is a `runpy` launcher (md5 `2bdd4768`) that forwards argv, so the documented `cd /workspace/research && python3 jev_continuous_probe.py 1` works verbatim.
- **Corpus.** Assembled from **all** session trees — `research/jev_sessions/` (357 files, + `r087/` 100 + `rounds/` 3), `jev_sessions/` (308, + `r087/` 100), `runs/*/jev_sessions/` (183), plus `history.jsonl` from both trees (449 + 389 lines). Dedup key `(qid, p, round)` -> 445 distinct rounds, 4,200 records, 22 live qids. **A glob over a single directory finds only a fraction of the corpus** (flat `jev_sessions/` alone tops out at r386; `research/jev_sessions/` at r445).
- **Model segmentation is load-bearing.** `jev-1.13.0` covers 382 rounds (r2..r395) and `jev-1.14.0` covers 55 (r1..r446). Every baseline in this report is segment-scoped.
- **Environment.** 30th wipe — `/workspace` empty again (30th consecutive), no `research/` tree, no sessions, no script. Bootstrapped `SuperInstance/jev-quilt` + `SuperInstance/research` to `/tmp`. NAS 100 % (600G/600G, 0 avail) => `/workspace/research` is a **symlink** to `/tmp/jev-quilt/research` (`rm -rf` first, then `ln -s`; `ln -sfn` onto an existing directory nests the link inside it). TLS leaf **VALID** (CN=typesafe.ai, Let's Encrypt, notAfter 2026-12-25) -> no CA rebuild. `TYPESAFE_AI_TOKEN` is read natively by the script (no `JEV_API_KEY` mapping needed). Round file: `research/jev_sessions/continuous_r446.json`, script_md5 `3a255fa4` matches the prior round -> **mean_p directly comparable to r445**.
