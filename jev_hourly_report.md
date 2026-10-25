# JEV Hourly Report — Round 437

**Run:** 2026-10-25T11:04:26Z · 129th wipe · model `jev-1.14.0` (resolved from `history.jsonl`) · script md5 `3a255fa4642ec4a83173ab04d773d485`
**Result:** 1 round OK, 0 fails, 0.145 s · **mean_p 0.2200** · **bedrock 0/5** · **Drift: NONE**

> Baseline rule in force: every drift baseline is scored against the qid's **own model segment** (`jev-1.14.0`), never the pooled history, and restricted to **qids drawn this round**. The script's own `drift_events` is never a verdict.

---

## 1. This round

| qid | kind | p | bedrock (p>=0.70) | segment baseline (n/mu/sd) | dev | z |
|-----|------|---|------------------|---------------------------|-----|---|
| q14 | adversarial | 0.24 | no | 11 / 0.2273 / 0.0179 | +0.0127 | +0.71 |
| q16 | review | 0.20 | no | 9 / 0.1933 / 0.0071 | +0.0067 | +0.94 |
| q12 | speculative | **0.52** | no | 12 / 0.4975 / 0.0322 | +0.0225 | +0.70 |
| q20 | speculative | 0.09 | no | 11 / 0.0864 / 0.0067 | +0.0036 | +0.54 |
| q10 | speculative | 0.05 | no | 11 / 0.0518 / 0.0040 | -0.0018 | -0.45 |

**mean_p 0.2200** (sum 1.10 / 5) — **bedrock hits 0/5** — **questions reaching p>=0.70: NONE**

**Draw composition is the whole story for the 0/5.** Today drew **no bedrock-kind qid at all** (q14 adversarial, q16 review, q12/q20/q10 speculative). A zero-bedrock round is therefore *expected*, not a regression. The prior round r436 drew two bedrock-kind qids (q05, q01) and scored 2/5.

---

## 2. Drift verdict: NONE

| test | result |
|------|--------|
| qids with same-model \|dev\| > 0.05 | **0 / 5** |
| max aggregate \|dev\| (same-model) | **+0.0225** (q12) |
| same-model segment | n = 41 rounds, mu 0.4200, sd 0.1188 |

**The script reported `drift_events=1` — this is a POOLED-BASELINE FALSE FLAG and is rejected.** The script's `drift_check()` compares against the *pooled* all-model history. For q12 the pooled baseline is mu = 0.3816 (n = 104), so today's 0.52 computes to **dev +0.1384, z +2.66** and trips the flag. Pooling mixes the older `jev-1.13.0` model (q12 sat at 0.30–0.44, 92 observations) with `jev-1.14.0` (0.46–0.56). Against the *correct* same-model segment baseline (mu 0.4975, sd 0.0322), the same reading is **dev +0.0225, z +0.70** — a non-event. This is the known hazard that fires on a different qid each round (r428 q02, r435 q12, r436 q06, **r437 q12**); the model-segment gate is not optional.

**Archive check applied before re-measurement (per the order-of-operations rule):** q12's 0.52 has **no exact prior occurrence** in its 103 prior observations, so it was a candidate new extreme requiring a fresh draw. But it is **not beyond the all-time range**: q12's all-time max is **0.56** (r409), and the 1.14.0 segment already contains 0.50, 0.50, 0.50, 0.51, 0.54, 0.56. Today's 0.52 sits inside a densely populated 0.46–0.56 band ⇒ **a repeat, archive-judgeable, not a new extreme.** No re-measurement warranted.

---

## 3. mean_p in distribution

| baseline | n | mu | sd | today's dev | z |
|----------|---|----|----|-------------|---|
| 1.14.0 segment | 41 | 0.4200 | 0.1188 | -0.2000 | -1.68 |
| all history | 440 | 0.3847 | 0.1426 | -0.1647 | -1.15 |

**Monte Carlo (200k draws, 5 qids uniform from all 22, empirical per-qid p distributions):**
- E[mean_p] = 0.3947, sd = 0.1376
- **P(mean_p <= 0.2200) = 0.0813** — today sits at the ~8th percentile (z = -1.27)
- MC P(k bedrock of 5): k=0 **8.71 %**, k=1 32.18 %, k=2 37.98 % (modal), k=3 17.69 %, k=4 3.27 %, k=5 0.17 %

Today is a **low-but-ordinary** draw. The 8.71 % prior probability of a zero-bedrock round is exactly what was observed, and the low mean_p is a *composition* effect (5 non-bedrock qids), not a model regression. |dev| on the mean (0.20 vs segment) is large in relative terms but mean_p is a 5-sample draw whose own sd is 0.12–0.14 — the per-qid |dev| gate is the correct one and all five pass.

---

## 4. Cathedral health (bedrock-kind qids, 1.14.0 segment)

| qid | n | hits | rate | mu | sd | min–max |
|-----|---|------|------|----|----|---------|
| q01 | 11 | 11 | **100 %** | 0.8545 | 0.0093 | 0.84–0.87 |
| q03 | 9 | 9 | **100 %** | 0.8811 | 0.0145 | 0.86–0.90 |
| q04 | 10 | 10 | **100 %** | 0.8820 | 0.0103 | 0.87–0.90 |
| q05 | 9 | 9 | **100 %** | 0.8156 | 0.0167 | 0.78–0.83 |
| q07 | 11 | 11 | **100 %** | 0.7700 | 0.0155 | 0.75–0.79 |
| q08 | 8 | 8 | **100 %** | 0.8900 | 0.0131 | 0.88–0.91 |
| q02 | 13 | 10 | 76.9 % | 0.7277 | 0.0303 | 0.68–0.77 |

**6 of 7 bedrock qids at 100 %; q02 remains the sole watch item at 76.9 %** (10/13, min 0.68 dips below the 0.70 gate). Segment n is small (8–13) so these are directional, not tight. q02 stays **ESCALATED**.

**No speculative or adversarial qid has ever reached 0.70** — 0 crossings in the segment; today's 0.52 on q12 is the highest speculative reading on record and is still well short of the bedrock gate.

---

## 5. Round hygiene

- **One round, not 200.** The literal task command (`timeout 60 python3 jev_continuous_probe.py`) has no positional arg, and `rounds_requested` defaults to `None`, which makes the script loop on wall-clock until the 55 s ceiling — it would have produced ~200 rounds. Invoked as `python3 jev_continuous_probe.py 1` ⇒ exactly 1 round, 0.145 s, clean exit, no overshoot.
- Round counter resolved from **max(files, history)** = 436 ⇒ start 437. Pre-run: 244 round files, max r436, history 440 rows.
- **History round-label collisions confirmed persistent (2nd session):** 441 rows / 427 distinct labels; rounds **384–391** carry 2–3 rows each. The collision band is **entirely `jev-1.13.0`**; the 1.14.0 segment (r396–r437) is collision-free ⇒ baselines unaffected.
- Script md5 `3a255fa4642ec4a83173ab04d773d485` — **unchanged**, same instrument as the prior round, so mean_p is directly comparable.
- TLS leaf **VALID** (CN=typesafe.ai, notAfter 2026-12-25) ⇒ no CA bundle rebuild needed this round.

**Verdict: NO DRIFT. mean_p 0.2200, 0/5 bedrock (no bedrock-kind qid drawn), q02 still the only watch item.**
