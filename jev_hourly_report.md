# JEV Continuous Probe — Hourly Report r433

**Run:** 2026-10-25T07:03:39Z (session_ts `2026-10-25T07:03:39.003122+00:00`)
**Round:** r433 (exactly 1 round — explicit positional count `1`, no overshoot, no kill needed)
**Instrument:** `SuperInstance/jev-quilt@HEAD:jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485`
**Served model:** `jev-1.14.0` (no switch vs r430/r431/r432)
**Round file:** `jev-quilt/research/jev_sessions/continuous_r433.json`
**Corpus:** `jev-quilt/research/jev_sessions/history.jsonl` (r433 appended exactly once; 437 ok / 0 fail)

> **Path note (16th consecutive wipe).** The prompt named `/workspace/research/` and
> `/workspace/research/jev_sessions/continuous_r*.json`. `/workspace` was empty and the NAS is
> at 100 % (600G/600G, 0 avail). The live instrument and the corpus live in
> `SuperInstance/jev-quilt`; `SuperInstance/research` holds only the archives + this report.
> The `research` repo's copy of `jev_continuous_probe.py` is the **stale 20-question decoy**
> (md5 `bd7c35964522d6da56130f87e96eb74e`) and was NOT run. The archives were read from
> `research/jev_sessions/rounds/continuous_r*.json` (9 files, r429/r430 + the 3 latest
> session files) and cross-checked against the canonical `jev-quilt` history corpus.

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.5060** |
| **Bedrock hits (p >= 0.70)** | **3 / 5 (60.0 %)** — `q03` (0.89), `q07` (0.79), `q17` (0.73) |
| **Drift (\|dev\| > 0.05)** | **NONE** — max \|dev\| among drawn qids = **0.0220** (q07) |
| Rounds ok / fails | 1 / 0 |
| Verdicts | 5 |

**Verdict: no drift.** All five drawn questions landed inside their own `jev-1.14.0` baseline
bands. mean_p **0.5060** sits at **z = +0.69 / 70.3rd pct** of the 1.14.0 round-mean
distribution (n=37, mean 0.4255, sd 0.1172) — an ordinary mid-band draw.

---

## Round r433 verdicts

Baseline = `jev-1.14.0`-only corpus, r433 excluded.

| qid | kind | p | >=0.70 (bedrock) | base mean | base sd | dev | z |
|---|---|---|---|---|---|---|---|
| **q07** | **bedrock** | **0.79** | **YES** | 0.7680 | 0.0140 | +0.0220 | +1.57 |
| **q03** | **bedrock** | **0.89** | **YES** | 0.8800 | 0.0141 | +0.0100 | +0.71 |
| q15 | adversarial | 0.03 | no | 0.0300 | 0.0000 | +0.0000 | n/a (σ=0) |
| q20 | speculative | 0.09 | no | 0.0856 | 0.0068 | +0.0044 | +0.65 |
| **q17** | **review** | **0.73** | **YES** | 0.7087 | 0.0203 | +0.0212 | +1.05 |

**Questions hitting p >= 0.70 (bedrock canon): `q03` (0.89), `q07` (0.79), `q17` (0.73).**

- `q03` ("substrates are grown, not designed") and `q07` ("11 opcodes across cell/quilt/qult")
  are **cathedral members at 100 %** on the 1.14.0 segment (`q03` 8/8, `q07` 10/10).
- `q17` ("FNV-1a canary pinned across the fleet") is a `review` qid, **not** a bedrock-class
  doctrine. It straddles the 0.70 threshold: 6/8 hits (75 %), range 0.68–0.75. It is counted
  as a bedrock *hit* by the instrument's `p >= 0.70` rule, but it is **not** a cathedral
  member and does not count toward canon-promotion. See the q17 note below.
- `q15` (adversarial) and `q20` (speculative) are non-bedrock kinds and are not capable of a
  bedrock hit by construction. Both read at their expected low values.

---

## q17 is the round's only interesting movement — and it is a threshold artifact, not drift

`q17` posted p=0.73, the third bedrock hit of the round. Its 1.14.0 history shows it sitting
**directly on the 0.70 line**:

| round | p | hit? |
|---|---|---|
| 396 | 0.71 | yes |
| 398 | 0.70 | yes |
| 402 | 0.72 | yes |
| 405 | 0.70 | yes |
| 409 | 0.72 | yes |
| 415 | 0.68 | **no** |
| 424 | 0.75 | yes |
| 428 | 0.69 | **no** |
| **433** | **0.73** | **yes** |

r433's +0.0212 dev is a normal move for this qid (sd 0.0203, z +1.05) — **well inside the
0.05 floor**. But the *reason* the round shows 3 bedrock hits instead of 2 is that `q17`
happens to land 0.03 above the cut rather than 0.03 below it. Two of its eight prior readings
(0.68, 0.69) were misses for exactly that reason. **The bedrock-hit count of this round is a
coin-flip on a straddling qid, not a signal about the oracle.** The honest read: 2 cathedral
bedrock hits (`q03`, `q07`) plus 1 threshold-straddling `review` hit (`q17`).

This is the same shape as the `q12` plateau diagnosed in r431 — a qid parked on a boundary
produces an apparently meaningful count that is really a lottery. The `spec_notebook` guard
does not apply to `q17` (it is `review`, not one of q10/q11/q12/q13), so nothing blocks the
hit; but nothing promotes it either.

---

## σ≈0 trap, 8th recurrence — `q15` has a degenerate baseline

`q15` (adversarial, "24 ports across cell/quilt") has a **perfectly degenerate baseline on
1.14.0**: 5 readings, all exactly 0.03, sd = 0.0000. Its z-score is therefore undefined
(0/0), and a naive z-computation would either emit `nan` or crash.

This is the 8th recurrence of the trap in this corpus, and the **|dev|-first** rule handled it
correctly: q15's dev is **+0.0000**, the smallest movement in the round. A z-first read would
have had to skip it entirely (undefined) while the eye is drawn to the two largest z's
(q07 +1.57, q17 +1.05) — both of which are *smaller* real movements than q07's absolute
position suggests, and both comfortably clear.

Note also that `q15` has been **flat at 0.02–0.03 across all 437 rounds and both model
versions** (129 readings). It is one of the most stable qids in the corpus. Its stability is
the reason the round is clean, not the reason it is suspicious.

---

## Method confirmation — the full-history baseline is benign this round

Last round (r431) the full-history baseline manufactured a **false drift on q12**. This round
it does not, but the contrast is still worth recording because the failure mode is a property
of the baseline, not of the round:

| qid | p (r433) | 1.14.0-seg base | dev | full-history base | dev | verdict |
|---|---|---|---|---|---|---|
| q07 | 0.79 | 0.7680 | +0.0220 | 0.7557 | +0.0343 | both clear |
| q03 | 0.89 | 0.8800 | +0.0100 | 0.8857 | +0.0043 | both clear |
| q15 | 0.03 | 0.0300 | +0.0000 | 0.0251 | +0.0049 | both clear |
| q20 | 0.09 | 0.0856 | +0.0044 | 0.1034 | −0.0134 | both clear |
| q17 | 0.73 | 0.7087 | +0.0212 | 0.7030 | +0.0270 | both clear |

Both baselines agree on "no drift" here. The rule stays in force: **the model-matched
segment carries the verdict**, because the full-history baseline mixes the 1.13.0 regime
(399 rounds) with the 1.14.0 regime (38 rounds) and will invent drift on any qid whose
distribution shifted with the model. `q12` is still bimodal and would still trip it — it just
was not drawn this round.

---

## Cathedral status — `jev-1.14.0` segment (n=38 rounds, 190 verdicts)

**Bedrock class (5 doctrines + 2 architecture + canary):**

| qid | n | hits | hit-rate | mean | sd | min | max |
|---|---|---|---|---|---|---|---|
| q01 | 10 | 10 | **100 %** | 0.8540 | 0.0092 | 0.84 | 0.87 |
| q02 | 13 | 10 | 76.9 % | 0.7277 | 0.0291 | 0.68 | 0.77 |
| **q03** | 8 | 8 | **100 %** | 0.8800 | 0.0141 | 0.86 | 0.90 |
| q04 | 9 | 9 | **100 %** | 0.8822 | 0.0103 | 0.87 | 0.90 |
| q05 | 8 | 8 | **100 %** | 0.8150 | 0.0166 | 0.78 | 0.83 |
| **q07** | 10 | 10 | **100 %** | 0.7680 | 0.0140 | 0.75 | 0.79 |
| q08 | 8 | 8 | **100 %** | 0.8900 | 0.0122 | 0.88 | 0.91 |
| q17 | 8 | 6 | 75.0 % | 0.7087 | 0.0203 | 0.68 | 0.75 |

**Cathedral = 6 qids at 100 %: `q01`, `q03`, `q04`, `q05`, `q07`, `q08`.**
`q02` (76.9 %) and `q17` (75.0 %) sit just below the 100 % bar. All 6 cathedral members are
above 0.70 on every single 1.14.0 reading — 53/53 clean, no regressions.

**Speculative / adversarial / review (must stay low):**

| qid | kind | n | hits | mean | sd |
|---|---|---|---|---|---|
| q06 | speculative | 10 | 0 | 0.1400 | 0.0063 |
| q09 | speculative | 4 | 0 | 0.1000 | 0.0100 |
| q10 | speculative | 9 | 0 | 0.0511 | 0.0031 |
| q11 | speculative | 7 | 0 | 0.1771 | 0.0260 |
| q12 | speculative | 9 | 0 | 0.4989 | 0.0325 |
| q13 | speculative | 10 | 0 | 0.1600 | 0.0045 |
| q14 | adversarial | 10 | 0 | 0.2260 | 0.0174 |
| q15 | adversarial | 5 | 0 | 0.0300 | 0.0000 |
| q16 | review | 7 | 0 | 0.1914 | 0.0064 |
| q18 | speculative | 9 | 0 | 0.2478 | 0.0079 |
| q19 | adversarial | 10 | 0 | 0.1040 | 0.0080 |
| q20 | speculative | 9 | 0 | 0.0856 | 0.0068 |
| q21 | speculative | 7 | 0 | 0.0929 | 0.0045 |
| q22 | speculative | 5 | 0 | 0.1440 | 0.0080 |

**No speculative or adversarial qid has ever hit bedrock on 1.14.0 (0/116).** The `q10` leak
stays resolved (0.0511, n=9). `q12` remains the high-plateau speculative at 0.4989 with a
0.0 hit rate — it is NOT promotable (spec_notebook requires n>=20 AND hit-rate >=0.7 AND
explicit doctrinal-state phrasing; it has 0/9).

---

## Recent rounds (context for the mean_p read)

| round | model | mean_p | hits | verdicts |
|---|---|---|---|---|
| r429 | jev-1.14.0 | 0.540 | 3 | q07:0.75 q08:0.88 q13:0.16 q03:0.88 q15:0.03 |
| r430 | jev-1.14.0 | 0.284 | 1 | q11:0.20 q07:0.78 q22:0.14 q16:0.18 q19:0.12 |
| r431 | jev-1.14.0 | 0.492 | 2 | q16:0.19 q10:0.05 q12:0.49 q08:0.89 q01:0.84 |
| r432 | jev-1.14.0 | 0.188 | 0 | q19:0.09 q14:0.25 q10:0.05 q12:0.47 q20:0.08 |
| **r433** | **jev-1.14.0** | **0.506** | **3** | **q07:0.79 q03:0.89 q15:0.03 q20:0.09 q17:0.73** |

mean_p is a class-mix lottery, not a health metric: r432 (0.188) and r429 (0.540) differ by
0.35 with **identical instruments and model**. The only reason to read r433's 0.506 is as
"70th percentile of the 1.14.0 round-mean distribution" — which is an ordinary draw. The
round-mean is dominated by **which question kinds get drawn**, not by oracle behaviour.

---

## Method rules applied (carry forward)

1. **Model-segmented baseline.** Every qid bucketed against its own `jev-1.14.0` segment
   (r396–r433), never the full history.
2. **|dev| before z.** Drift threshold is |dev| > 0.05. z is reported for context only. The
   σ≈0 trap (q15) makes z undefined in exactly the case where |dev| is most informative.
3. **Aggregate drift verdict.** "N of 5 qids within 0.05, 0 beyond" — never one-qid.
4. **Explicit positional round count.** `python3 jev_continuous_probe.py 1` ⇒ exactly one
   round. The loop is `while (elapsed < 55s and len(rounds) < rounds_requested)`, so a
   count of 1 terminates cleanly with **no kill and no overshoot** — the r154 lesson learned
   the hard way.
5. **q17-style threshold straddlers are reported, not counted as signal.**
6. **Self-comparison is not a cross-round check.** The r433 round file is compared against
   the independent prior corpus, not against a copy of itself.

---

## Environment

- **16th consecutive wipe.** `/workspace` empty; NAS 100 % (600G/600G, 0 avail) — durable
  copies live in git, not on the NAS.
- **`gh` CLI is not installed** in this sandbox; used the REST API via `curl -sk` with
  `$GITHUB_TOKEN` instead. `/users/SuperInstance/repos` works — the account is a **user**,
  not an org, so `/orgs/SuperInstance/repos` returns 404.
- **Strict TLS works** for `api.typesafe.ai` (verified `urllib` with default context, HTTP
  200 on `/v1/models`). The `JEV_INSECURE_TLS=1` escape hatch was **not** used.
- **`read` tool is jailed to the workspace root** — cannot read `/tmp`; use bash for cloned
  files. The `write` tool also cannot write outside `/workspace`.
- **The 0-byte write trap fired.** A heredoc straight to `/workspace/research/` produced a
  **0-byte file** and `cat: write error: Disk quota exceeded` — the file *appears* in `ls`
  but holds nothing. Fix: author to `/tmp` (overlay fs, 28G free) and `cp` across, or push
  the durable copy to git.
- **Round counter derived correctly**: files->432, history->432 ⇒ start=433, and the script
  aborts if the target round file already exists (no overwrite risk).
- **Corpus integrity**: 437 rounds, all `status: ok`, 0 fails. r433 present exactly once.

## Open items carried forward

1. **q10/q11/q12/q13 state-leak patch** — the live instrument is the `jev-quilt` repo-ROOT
   `jev_continuous_probe.py` (md5 `3a255fa4...`), NOT the `research` repo's stale decoy
   (md5 `bd7c3596...`). The two are easy to confuse and the decoy is the one committed to
   the *report* repo. Worth deleting the decoy from `research` or adding a header banner.
2. **JEV round-file flush** — the 60-round `history.jsonl` is still not committed as its own
   artefact (it lives inside `jev-quilt`, which is the correct home, but the `research` side
   has no pointer to it).
3. **q02 / q17 sub-100 %** — the two non-cathedral bedrock-class qids. `q17`'s 0.68–0.75
   straddling is the reason this round's hit count is fragile.
