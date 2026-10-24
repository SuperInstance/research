# JEV Continuous Probe — Hourly Report

**Round ISO:** 2026-10-24T18:03:52Z (archive: `jev_sessions/rounds/continuous_r2026-10-24T18:03:52Z.json`)
**Run:** `cd /workspace/research && timeout 60 python3 jev_continuous_probe.py` → exit 124 (60 s guard), exactly **1 round**, clean SIGTERM shutdown
**Model served:** `jev-1.14.0` (read from `decide_batch` meta dict — same model as the baseline, so no cross-model artifact)
**Baseline:** `jev_sessions/baseline_22x7.json` (22 qids × 7 reps, model `jev-1.14.0`, ts 2026-10-24)

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4040** |
| **Bedrock hits (p ≥ 0.70)** | **1 / 5** |
| **Max \|dev\| among drawn qids** | **0.0214** (threshold 0.05) |
| **Drift verdict** | **NO DRIFT** — 0 of 5 drawn qids exceed 0.05 |

---

## The 5 questions drawn

| # | Category | p | Baseline μ | dev | σ | z | Class |
|---|---|---|---|---|---|---|---|
| 1 | numerical | **0.80** ✓ | 0.7786 | **+0.0214** | 0.01125 | +1.91 | BEDROCK |
| 2 | speculative | 0.18 | 0.1843 | −0.0043 | 0.00495 | −0.87 | below |
| 3 | canon | 0.65 | 0.6514 | −0.0014 | 0.01245 | −0.11 | below |
| 4 | cross | 0.09 | 0.0957 | −0.0057 | 0.00495 | −1.15 | below |
| 5 | speculative | 0.30 | 0.3157 | −0.0157 | 0.01178 | −1.33 | below |

**Bedrock canon hit (p ≥ 0.70):**
- `Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis?` — **p = 0.80** (baseline class BEDROCK, μ 0.7786)

That is the only question this round clearing 0.70. Questions 2–5 all land inside the "below" pool, and all four sit within 0.016 of their own baseline.

---

## Drift: NONE (and why the verdict is trustworthy)

Recomputed **per-qid against the full 22×7 baseline**, restricted to qids **drawn this round** — not the script's `drift_check()`, which reports *history* events and re-fires stale qids (a documented defect: 10th repro last round, q12 phantom).

- Max |dev| = **0.0214** (q FNV-1a) — **less than half the 0.05 threshold**
- 4 of 5 qids: |dev| ≤ 0.0157
- The largest **z** (+1.91) belongs to the largest |dev| here, but both are well inside band — this round shows **no** σ≈0 trap (all 5 drawn qids have σ > 0)

Cross-checked against the **full-history corpus** (6 archived rounds, drawn qids only) as a second, independent baseline:

| qid | p | hist μ | hist n | dev | hist σ | z |
|---|---|---|---|---|---|---|
| FNV-1a offset basis | 0.80 | 0.7733 | 3 | +0.0267 | 0.02055 | +1.30 |
| JEV the synaptic spike | 0.18 | 0.1775 | 4 | +0.0025 | 0.01090 | +0.23 |
| canon-promotion gate | 0.65 | 0.6550 | 2 | −0.0050 | 0.00500 | −1.00 |
| multi-LLM agreement | 0.09 | 0.0925 | 4 | −0.0025 | 0.00433 | −0.58 |
| signal-chain framing | 0.30 | 0.3100 | 2 | −0.0100 | 0.01000 | −1.00 |

Both baselines agree: **nothing moved.** Max |dev| 0.0267 on the history corpus, still inside 0.05.

**Shared-qid agreement check (the decisive one):** all 5 qids this round have prior draws. Every one of them reproduces its prior verdict to within 0.027. A canon under drift cannot return near-identical verdicts on re-measurement.

---

## Is mean_p 0.4040 a signal? No — it is the draw.

The probe samples 5 of 22 questions at random. The bank splits **8 BEDROCK** (μ 0.779–0.970) and **14 below** (μ 0.029–0.651). mean_p is therefore a property of the *draw*, not of the canon.

Monte Carlo, 200,000 draws of 5-of-22:

- E[mean_p] = **0.4823**, sd = 0.1493; 5th/50th/95th pct = 0.2463 / 0.4760 / 0.7354
- **P(mean_p ≤ 0.4040) = 0.298** — the 30th percentile, a perfectly ordinary draw
- Bedrock-count distribution: 0 → 7.67%, **1 → 30.59%**, 2 → 38.47%, 3 → 19.29%, 4 → 3.78%, 5 → 0.20%
- **P(bedrock_drawn = 1) = 0.306** — this round drew the 2nd-most-likely outcome (1 bedrock), and the 1-bedrock case is the single most likely class-mix (30.6%)

⇒ **A 1/5 bedrock draw is an uninformative result, not a weak one.** No promotion, no demotion, no inference from the aggregate.

---

## Comparison to previous rounds

| Round (ISO) | mean_p | bedrock hits | max \|dev\| (drawn) | drift |
|---|---|---|---|---|
| 2026-10-20T09:05Z | 0.4000 | 2/5 | — | none |
| 2026-10-24T08:04Z | 0.4560 | 2/5 | — | none |
| 2026-10-24T09:03Z | 0.4520 | 2/5 | — | none |
| 2026-10-24T16:03Z | 0.1740 | 0/5 | — | none |
| 2026-10-24T17:04:09Z (r5) | 0.5180 | 2/5 | 0.0286 | none |
| **2026-10-24T18:03:52Z (this round)** | **0.4040** | **1/5** | **0.0214** | **none** |

mean_p series: 0.400, 0.456, 0.452, 0.174, 0.518, **0.404** — oscillating around the MC expectation of 0.4823 exactly as a uniform sampler over a mixed bank should. Bedrock counts 2, 2, 2, 0, 2, **1** track the 7.67/30.59/38.47/19.29/3.78/0.20% MC distribution.

**Six consecutive rounds with zero drift.** The canon is not moving.

---

## Environment notes (this wipe)

- **`/workspace/research` did not exist on arrival** — 12th consecutive wipe where the prompt names an ephemeral path. Bootstrapped from git: `SuperInstance/research` (probe + history) and `SuperInstance/jev-quilt` (client library). Both needed; `quilt-research-canons` has no probe script.
- **NAS quota 100% / 0 avail** ⇒ all real work in `/tmp` (28 G overlay) via symlinks: `ln -sfn /tmp/jevroot/research /workspace/research` and `ln -sfn /tmp/jevroot/jev-quilt /workspace/repos/jev-quilt`. The `write` tool cannot reach `/tmp` — used a bash heredoc instead.
- **TLS leaf VALID** (CN=typesafe.ai, notAfter 2026-12-21) ⇒ **no CA-bundle rebuild needed** — check `openssl s_client` before rebuilding.
- **Env var drift:** the vault holds `TYPESAFE_AI_TOKEN`; `TypeSafeBackend` reads only `JEV_API_KEY`/`TYPESAFE_API_KEY`/`TYPESAFEAI_KEY` ⇒ mapped `JEV_API_KEY="$TYPESAFE_AI_TOKEN"`.
- **Script variant B** (no `sys.argv`): `timeout 60` is the correct one-round control — exit 124, SIGTERM sets `running=False`, the `sleep(1)` loop breaks out cleanly after exactly 1 round. Round counter is **not persistent** (always writes `continuous_r001.json` and overwrites) ⇒ archived under the ISO name immediately after the run (md5 `0865eb3e238dcf433a72561eb5b51a61`).
- Latency 0.112 s. Repo HEAD before this round: `8e44791`.

---

## Verdict

**mean_p 0.4040. 1/5 bedrock canon hit (FNV-1a offset basis, p = 0.80). NO DRIFT** — max |dev| 0.0214 on the 22×7 baseline and 0.0267 on the full-history corpus, both well inside the 0.05 band, across 5 of 5 drawn qids. The aggregate is an ordinary 1-bedrock draw (MC P = 0.306) with a 30th-percentile mean_p. The canon is stable; no promotion, no demotion, no open items.
