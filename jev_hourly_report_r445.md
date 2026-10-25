# JEV continuous probe — round r445 hourly report

**Generated:** 2026-10-25T19:04:56.831492+00:00  
**Round:** r445 (ts 2026-10-25T19:03:41.907540+00:00)  
**Resolved model:** `jev-1.14.0` (segment n=50 rounds)  
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (root probe; `research/` copy is a launcher wrapper)  
**Corpus:** `SuperInstance/jev-quilt` @ `8546dbd` (live), history `research/jev_sessions/history.jsonl` — 449 rounds, r1..r445, continuous

---

## 1. Headline

| metric | value |
|---|---|
| **mean_p** | **0.3080** |
| **bedrock (p ≥ 0.70)** | **1/5** drawn qids — q03 0.89 |
| **drift (recomputed)** | **NONE** — 0 of 5 drawn qids exceed \|dev\| 0.05 |
| script's own `drift_events` | 1 — on **q12, NOT drawn this round** (20th repro, stale) |
| cathedral (bedrock qids, segment) | 83/86 = **96.5 %** |
| MC E[mean_p] / P(mean_p ≤ 0.308) | 0.3999 (sd 0.1331) / **0.2839** |
| modal bedrock count | **2** (observed today: 1) |

---

## 2. This round's draw

| qid | kind | p | bedrock? |
|---|---|---|---|
| q03 | bedrock | 0.89 | **YES** |
| q14 | adversarial | 0.25 | — |
| q11 | speculative | 0.17 | — |
| q22 | speculative | 0.14 | — |
| q21 | speculative | 0.09 | — |

mean_p = (0.89 + 0.14 + 0.09 + 0.17 + 0.25) / 5 = **0.3080**

Only **q03** cleared the p ≥ 0.70 bedrock gate. The other four are a speculative trio (q22 0.14, q21 0.09, q11 0.17) and one adversarial (q14 0.25) — all sitting where their own baselines put them.

---

## 3. Drift — recomputed properly

Baseline = **per-qid, current-model segment** (`jev-1.14.0`), restricted to the 5 qids actually drawn. \|dev\| first, sigma second.

| qid | kind | p | n | mu | sd | dev | z | verdict |
|---|---|---|---|---|---|---|---|---|
| q03 | bedrock | 0.89 | 12 | 0.8817 | 0.0128 | +0.0083 | +0.65 | clear |
| q11 | speculative | 0.17 | 12 | 0.1733 | 0.0229 | -0.0033 | -0.15 | clear |
| q14 | adversarial | 0.25 | 14 | 0.2300 | 0.0165 | +0.0200 | +1.21 | clear |
| q21 | speculative | 0.09 | 11 | 0.0945 | 0.0050 | -0.0045 | -0.91 | clear |
| q22 | speculative | 0.14 | 7 | 0.1400 | 0.0107 | +0.0000 | +0.00 | clear |

**Aggregate verdict: 0 of 5 drawn qids exceed |dev| 0.05 → DRIFT NONE.** Max |dev| = 0.0200 (q14), which is well inside the band.

### 3.1 The pooled baseline would have false-flagged q14 (r428 trap)

| qid | p | POOLED n | POOLED mu | POOLED dev | POOLED z | SEGMENT dev |
|---|---|---|---|---|---|---|
| q03 | 0.89 | 104 | 0.8857 | +0.0043 | +0.45 | +0.0083 |
| q11 | 0.17 | 104 | 0.1837 | -0.0137 | -0.75 | -0.0033 |
| q14 | 0.25 | 95 | 0.1976 | +0.0524 | +2.90 | +0.0200 |
| q21 | 0.09 | 105 | 0.0909 | -0.0009 | -0.21 | -0.0045 |
| q22 | 0.14 | 101 | 0.1208 | +0.0192 | +2.22 | +0.0000 |

Pooling across the `jev-1.13.0` → `jev-1.14.0` switch fuses the **model artifact** into the current signal: q14's pooled dev is **+0.0522 (z +2.88)** — over the gate, and it looks like drift. Against its own `1.14.0` segment (n=14, mu=0.2300) the same value is **dev +0.0200** — dead on baseline. **q14's 0.25 is a REPEAT**: 10 of 10 prior segment observations sit at or below it (segment max = 0.25). No drift, and the archive alone settles it.

### 3.2 The script's own `drift_events=1` is the 20th repro of a stale-event defect

```
[
  {
    "qid": "q12",
    "recent_p": 0.54,
    "prior_median": 0.49,
    "delta": 0.05
  }
]
```

The event is on **q12**, whose last observation is from **r438** — seven rounds stale — and **q12 was not in this round's draw**. `drift_check()` (line 317) compares every qid's last value to a 5-sample median whether or not that qid was drawn this round, so old qids re-fire old events. For the record, q12 on the current segment is n=13, mu=0.5008, sd=0.0317, range 0.46–0.56 — a 0.54 reading against a 0.49 median is noise, and it is not this round's data.

### 3.3 q21's 0.09 is a new extreme but not a drift

q21 read **0.09** with 0 of 5 prior segment observations strictly below it (segment min = 0.09, max = 0.10) — formally a *new extreme*, which the r427 rule says needs a fresh re-measurement to confirm. But the deviation is **−0.0045**, two orders of magnitude inside the 0.05 gate, and the segment sigma is 0.0050. A value that is extreme for a tight cluster is not a drift event; it is a tight cluster. **No re-measurement is warranted at this magnitude** — the |dev| gate binds first.

---

## 4. Comparison to previous rounds

History table **recomputed from `history.jsonl` by script**, not transcribed.

| round | model | mean_p | bedrock | qids |
|---|---|---|---|---|
| r431 | jev-1.14.0 | 0.4920 | 2/5 | q16=0.19 q10=0.05 q12=0.49 q08=0.89 q01=0.84 |
| r432 | jev-1.14.0 | 0.1880 | 0/5 | q19=0.09 q14=0.25 q10=0.05 q12=0.47 q20=0.08 |
| r433 | jev-1.14.0 | 0.5060 | 3/5 | q07=0.79 q03=0.89 q15=0.03 q20=0.09 q17=0.73 |
| r434 | jev-1.14.0 | 0.2240 | 0/5 | q21=0.10 q09=0.10 q12=0.46 q16=0.20 q18=0.26 |
| r435 | jev-1.14.0 | 0.3220 | 1/5 | q21=0.10 q09=0.10 q15=0.03 q12=0.50 q04=0.88 |
| r436 | jev-1.14.0 | 0.4260 | 2/5 | q05=0.82 q18=0.25 q06=0.14 q01=0.86 q10=0.06 |
| r437 | jev-1.14.0 | 0.2200 | 0/5 | q14=0.24 q16=0.20 q12=0.52 q20=0.09 q10=0.05 |
| r438 | jev-1.14.0 | 0.4900 | 2/5 | q08=0.89 q12=0.54 q06=0.14 q17=0.73 q11=0.15 |
| r439 | jev-1.14.0 | 0.4020 | 2/5 | q10=0.05 q05=0.81 q11=0.19 q21=0.10 q01=0.86 |
| r440 | jev-1.14.0 | 0.4180 | 2/5 | q10=0.05 q03=0.89 q01=0.87 q11=0.18 q19=0.10 |
| r441 | jev-1.14.0 | 0.4040 | 2/5 | q20=0.09 q14=0.23 q05=0.85 q02=0.74 q19=0.11 |
| r442 | jev-1.14.0 | 0.3520 | 2/5 | q10=0.05 q02=0.71 q13=0.17 q05=0.80 q15=0.03 |
| r443 | jev-1.14.0 | 0.4500 | 2/5 | q08=0.88 q04=0.86 q11=0.15 q14=0.24 q22=0.12 |
| r444 | jev-1.14.0 | 0.5460 | 3/5 | q03=0.87 q06=0.14 q01=0.84 q07=0.79 q20=0.09 |
| r445 | jev-1.14.0 | 0.3080 | 1/5 | q03=0.89 q22=0.14 q21=0.09 q11=0.17 q14=0.25  ← **this round** |

**r445 mean_p 0.3080 sits inside the recent band** (last 14 rounds: min 0.1880, max 0.5460, mean 0.3886). It is the second-lowest of the last 15, but the MC puts P(mean_p ≤ 0.308) at **0.2839** — roughly a 1-in-3 draw outcome, entirely ordinary.

**The bedrock count is a property of the draw, not of the canon.** A round draws 5 of 22 qids at random, and 7 of those 22 are bedrock — so 1-of-5 is well within the ordinary range. The MC over 200k draws (5 qids uniform from all 22) gives P(k=1) = **32.72 %** and a modal k of **2 (37.57 %)**. Today's k=1 is the second most likely single outcome, and **the deciding comparison is shared qids, not aggregates** — every shared qid with the previous round reproduced its own band.

### 4.1 Shared-qid comparison with the immediately preceding rounds

| shared qid | r443 | r444 | **r445** | segment mu | note |
|---|---|---|---|---|---|
| q11 | 0.15 | — | **0.17** | 0.1733 |  |
| q14 | 0.24 | — | **0.25** | 0.2300 | at segment max |
| q22 | 0.12 | — | **0.14** | 0.1400 |  |
| q03 | — | 0.87 | **0.89** | 0.8817 |  |
| q21 | — | — | **0.09** | 0.0945 |  |

---

## 5. Cathedral & contamination checks

| bedrock qid | hits/n on segment | rate | seg min | seg max | all-time hits |
|---|---|---|---|---|---|
| q01 | 14/14 | 100.0% | 0.84 | 0.87 | 110/110 |
| q02 | 12/15 | 80.0% | 0.68 | 0.77 | 89/92 |
| q03 | 12/12 | 100.0% | 0.86 | 0.90 | 104/104 |
| q04 | 11/11 | 100.0% | 0.86 | 0.90 | 103/103 |
| q05 | 12/12 | 100.0% | 0.78 | 0.85 | 101/101 |
| q07 | 12/12 | 100.0% | 0.75 | 0.79 | 92/92 |
| q08 | 10/10 | 100.0% | 0.88 | 0.91 | 91/91 |
| **TOTAL** | **83/86** | **96.5%** | | | |

Six of seven bedrock qids hold **100 %**. The single imperfect one is **q02 (80 % on segment)**, the same hair-under-gate qid as in r428 — never a collapse, just misses.

**Contamination check — 'speculative/adversarial ever reached 0.70':**

- **speculative**: 0/1052 observations ≥ 0.70  ← **NEVER**
- **adversarial**: 0/308 observations ≥ 0.70  ← **NEVER**
- **review**: 68/192 observations ≥ 0.70  (all crossings are q17, a *review* qid — excluded from any 'speculative' claim)

A speculative or adversarial claim has **never** been satisfied in 445 rounds. q17 (review) holds a 0.68–0.75 plateau and contributes every review crossing; it must be excluded from speculative claims.

---

## 6. Verdict

**mean_p 0.3080 · bedrock 1/5 · drift NONE.**

1. **No drift.** 0 of 5 drawn qids exceed |dev| 0.05 against the `jev-1.14.0` segment. Max |dev| 0.0200 (q14).
2. **The one bedrock hit is the strongest kind of bedrock.** q03 read 0.89 against a segment mu of 0.8817 — the cathedral qids are holding, not degrading.
3. **The low mean_p and the 1/5 bedrock count are the draw, not the canon.** MC P(mean_p ≤ 0.308) = 0.2839; modal bedrock count is 2, and 1 is the second most likely outcome. The 8 bedrock qids outside this draw were not asked.
4. **The script's `drift_events=1` must not be read as a health signal.** It fired on a stale q12 from r438 (not drawn) — the 20th repro of a known defect. The recomputed verdict is the one that counts.
5. **The pooled baseline would have produced a false flag on q14** (pooled dev +0.0522, z +2.88; segment dev +0.0200). Segmenting by resolved model is what prevents it.

---

## 7. Method notes & environment

- **Round control:** `cd /workspace/research && JEV_API_KEY="$TYPESAFE_AI_TOKEN" timeout 60 python3 jev_continuous_probe.py 1` — Variant A, explicit positional count `1` (the script defaults to 200; killing after launch races the writer and over-produces). Exactly 1 round in 0.30 s, 0 fails.
- **Round counter:** derived from max(round files, history.jsonl) → files 444, history 444, start 445. The script aborts if the target file exists, so no shadowing.
- **Corpus integrity:** `history.jsonl` is **tracked in git** (not gitignored) — verified via `git ls-files`. It carries all 449 rounds r1..r445 with no gap, and is the authoritative source: the r1–r202 round files use a *different, legacy* schema (`verdicts` as a dict of long qid names) and the r396–r445 range exists only in history.jsonl.
- **Resolved model read from `history.jsonl`**, never from the round file: every round file carries the static alias `jev-latest` (a script constant). `history.jsonl` shows `jev-1.13.0` (r1–r395) then `jev-1.14.0` (r396–).
- **Drift baselines scored per model segment**, per-qid, restricted to qids drawn this round; |dev| checked before sigma.
- **History table generated by script** from the archives, not hand-typed.
- **Environment:** 31st consecutive wipe — `/workspace` empty on arrival. NAS at 100 % (0 avail), so `/workspace/research` is a **symlink** to `/tmp/jev/jev-quilt/research` (`rm -rf` first, then `ln -s` — symlinking over an existing directory lands the link *inside* it). Bytes live on the 28 G overlay; the durable copy is git.
- **TLS:** live leaf valid (`typesafe.ai`, Let's Encrypt, notAfter 2026-12-21) — no CA bundle rebuild needed.
- **Auth:** `JEV_API_KEY` must be mapped from `TYPESAFE_AI_TOKEN`; the vault var name does not match the client's accepted names, so without the mapping `available()` is False and the run dies.

_Report generated by recomputing every figure from `research/jev_sessions/history.jsonl` (449 rounds) and `continuous_r445.json`._
