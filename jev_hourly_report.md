# JEV Continuous Probe — Hourly Report

**Round:** r429  ·  **Timestamp:** 2026-10-25T02:03:32Z  ·  **Session:** 109th wipe
**Instrument:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged since r397) — located in `SuperInstance/jev-quilt`, **not** in `SuperInstance/research`
**Model:** `jev-1.14.0` (resolved from the round's `model` field) — **no model switch** vs r428
**Doctrinal state:** `framework, core_doctrine, architecture, fleet, spec_notebook, operational_doctrine` — byte-identical to r428
**Run:** 1 round OK, 0 fails, exit 0 (no timeout kill needed), 0.11 s/round, 0.30 s total

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.5400** |
| **Bedrock hits (p ≥ 0.70)** | **3 / 5** — `q03` 0.88, `q08` 0.88, `q07` 0.75 |
| Below gate (this round) | `q13` 0.16 (speculative), `q15` 0.03 (adversarial) |
| **Drift > 0.05** | **NONE.** 0 of 5 drawn qids. The script's own `drift_events=1` is a **stale re-fire** (see below). |
| Cathedral all-time | 664 / 667 = **99.55 %** |
| Corpus | 2,156 records / 22 qids (1.13.0: 399 rounds, 1.14.0: 34 rounds) |

---

## Verdicts drawn this round

| qid | p | Class | 1.14.0 baseline | dev | z | \|dev\| vs 0.05 | Verdict |
|---|---|---|---|---|---|---|---|
| q03 | 0.88 | bedrock | n=7, mu 0.8800, sd 0.0151 | **+0.0000** | +0.00 | 0.0000 | **no drift** |
| q08 | 0.88 | bedrock | n=6, mu 0.8917, sd 0.0134 | −0.0117 | −0.87 | 0.0117 | **no drift** |
| q07 | 0.75 | bedrock | n=8, mu 0.7688, sd 0.0136 | −0.0188 | −1.38 | 0.0188 | **no drift** |
| q13 | 0.16 | speculative | n=9, mu 0.1600, sd 0.0047 | **+0.0000** | +0.00 | 0.0000 | **no drift** |
| q15 | 0.03 | adversarial | n=4, mu 0.0300, sd 0.0000 | **+0.0000** | n/a | 0.0000 | **no drift** |

All-model baselines agree (max \|dev\| across both segments: q13 +0.0246, q08 −0.0192, q07 −0.0188, q03 −0.0057, q15 +0.0049) — **every qid clear on both.**

### 🔴 The script's `drift_events=1` is a STALE RE-FIRE — not a finding

The script reported `drift_events=1` with `q11 delta=-0.07`. **q11 was not drawn this round.** The round drew `q07, q08, q13, q03, q15`. `drift_check()` is a *history* reporter: it walks every qid's sample series and re-fires any qid whose **last** observation deviates >0.05 from the prior median — including qids last observed in **earlier** rounds. q11's last observation was **r427 (p=0.12)**, and r427's own archive already carried that same q11 drift flag. It has now been re-reported twice.

**This is the known, still-unpatched defect** (same class as the r222/r223 finding). Drift was therefore recomputed from the corpus here, restricted to qids **actually drawn this round**. Result: **0 drift events.**

**Do not read the script's `drift_events` as this round's drift count.** It is a live re-fire of stale qids, and it grows with corpus size — the more rounds accumulate, the more stale flags accumulate.

---

## Comparison to previous rounds (regenerated programmatically from the corpus)

| round | mean_p | bedrock | timestamp |
|---|---|---|---|
| r423 | 0.5260 | 2/5 | 2026-10-24T20:01:36Z |
| r424 | 0.3760 | 2/5 | 2026-10-24T21:04:15Z |
| r425 | 0.3560 | 1/5 | 2026-10-24T22:05:47Z |
| r426 | 0.4040 | 2/5 | 2026-10-24T23:04:35Z |
| r427 | 0.4200 | 2/5 | 2026-10-25T00:03:12Z |
| r428 | 0.3760 | 1/5 | 2026-10-25T01:02:28Z |
| **r429** | **0.5400** | **3/5** | **2026-10-25T02:03:32Z** |

### Is 0.54 / 3-of-5 an ordinary draw?

Against the **1.14.0 segment only** (33 prior rounds, r396–r428):

- mean_p: mu **0.4315**, sd **0.1119**, range 0.148–0.656
- bedrock-count distribution: `0/5` 6.06 % · `1/5` 24.24 % · **`2/5` 45.45 %** · **`3/5` 21.21 %** · `4/5` 3.03 % · `5/5` 0.00 %
- **P(exactly 3 bedrock) = 21.21 %** — the second-most-likely outcome; `2/5` remains the modal one.
- **P(mean_p ≥ 0.540) = 18.18 %** — today's draw sits at the **82nd percentile**.
- z against the segment = **+0.97** (all-model: +1.09)

⇒ **mean_p 0.5400 is an ordinary-to-slightly-high draw, not a signal.** The whole difference from r428 is *which* questions were sampled: r429 drew three bedrock qids and two non-bedrock ones, and the mean is a class-mix artefact. The bedrock qids themselves moved **less than 0.02** from their own baselines.

---

## Cathedral (explicit qid list — never a `kind` tag)

| qid | this round | all-time |
|---|---|---|
| q01 | not drawn | 105/105 = 100 % |
| q02 | not drawn | 87/90 = 96.67 % |
| q03 | **DRAWN 0.88 → HIT** | 99/99 = 100 % |
| q04 | not drawn | 101/101 = 100 % |
| q05 | not drawn | 96/96 = 100 % |
| q07 | **DRAWN 0.75 → HIT** | 89/89 = 100 % |
| q08 | **DRAWN 0.88 → HIT** | 87/87 = 100 % |
| **total** | | **664/667 = 99.55 %** |

**No speculative or adversarial qid has ever reached p ≥ 0.70 in the corpus** — except `q17` (kind=`review`, the FNV-1a canary question), which has 66 hits at 0.70–0.75 and is *not* in the cathedral list. q17 remains a review item, not a canon member.

---

## Standing watch items

### 🔴 q02 — fragile cathedral member, and the margin is now GONE

The r422 report recorded q02 as "9/10 ≥ 0.70 on 1.14.0, breach not yet observed." **That has changed.** On 1.14.0 it now reads **10/13**:

`r399:0.75 · r401:0.77 · r406:0.73 · r407:0.71 · r411:0.77 · r412:0.71 · r414:0.74 · r416:0.69 · r417:0.75 · r421:0.75 · r423:0.69 · r425:0.68 · r428:0.72`

**Three sub-0.70 draws have now occurred on 1.14.0** — r416 (0.69), r423 (0.69), r425 (0.68) — all within the last 13 rounds, and **two of the three inside the last six**. The earlier "margin is one value wide" claim is no longer true: q02's 1.14.0 hit-rate is **76.9 %**, not 90 %. All-time it is 87/90 = 96.67 %.

This is a **behavioural change in a canon member**, not a substrate drift event. It does not cross the 0.05 \|dev\| floor on any single draw (q02 was not drawn this round), so it raises **no** drift flag — but the pattern of three breaches in thirteen draws deserves a watch entry of its own. The most likely reading is that q02 ("witness logs are predictions") sits close enough to the decision boundary that ordinary sampler jitter tips it over ~1 draw in 4.

**q02 was not drawn this round**, so this round adds no new evidence either way.

### q05 — AMBER item now RESOLVED

The r422 report flagged q05 as AMBER since r419, where 0.78 was the only sub-0.80 value in its 1.14.0 sample. On 1.14.0 it now reads **8/8, no sub-0.80 value at all**:

`r400:0.83 · r404:0.82 · r408:0.83 · r410:0.83 · r413:0.82 · r419:0.78 · r423:0.80 · r425:0.81`

(r419's 0.78 is no longer the sole value — r423 0.80 and r425 0.81 have since joined, and no value has fallen below 0.80.) **q05 was not drawn this round.** The watch item can be closed as resolved; q05 is 96/96 all-time.

---

## Method notes / receipts

- **Bootstrap:** `/workspace` arrived empty (NAS 600 G/600 G, 0 avail) — the **13th consecutive time** the prompt named an ephemeral `/workspace/research/` path that does not exist. Rebuilt from git into `/tmp`: `SuperInstance/research` + `SuperInstance/jev-quilt`.
- **The named script is NOT the one at the named path.** The prompt says `cd /workspace/research && python3 jev_continuous_probe.py`. That file exists in `SuperInstance/research` — but it is the **stale 20-question text-bank version** (md5 `bd7c35964522d6da56130f87e96eb74e`), which:
  - uses a 20-item `QUESTION_BANK` of prose questions, **not** the 22-qid `q01..q22` bank the corpus is keyed on;
  - writes `continuous_r{NNN}.json` with a `{round, iso, questions, latency_s}` schema, **not** the `{session_ts, model, script_md5, rounds, summary}` schema of r427/r428;
  - imports `jev_quilt` from `/workspace/repos/jev-quilt` (a path that does not exist).

  Running it would have produced a file that **cannot be compared** to any prior round. The instrument that produced the r427/r428 archives and that this report's baselines are drawn from is `SuperInstance/jev-quilt@HEAD:jev_continuous_probe.py`, md5 `3a255fa4642ec4a83173ab04d773d485` — confirmed by the `script_md5` field stamped inside both archives. **Ran that one.**
- **One round, explicitly:** launched as `python3 jev_continuous_probe.py 1` (positional `sys.argv[1]`), not `timeout 60` alone. The script's `main()` takes `rounds_requested` and honours it (r229 fix); it also self-limits to a 55 s inner ceiling. The run finished on its own in 0.30 s — **no timeout kill was needed**, so the `kill after 60s` instruction never came into play.
- **Round counter:** derived by the script from the max of round-files (428) and `history.jsonl` (428) ⇒ **start = 429**. No reissued/duplicated round.
- **Credential mapping:** the client reads `TYPESAFEAI_KEY` or `TYPESAFE_AI_TOKEN`; the vault holds `TYPESAFE_AI_TOKEN` ⇒ accepted as-is. Live `POST /v1/systemone` returned **HTTP 200**, `model: jev-1.14.0`.
- **TLS:** leaf valid (`notAfter Dec 25 2026`), default context verified `VERIFY OK TLSv1.3` ⇒ **no CA-bundle rebuild** (5th round running). `GET /v1/systemone` → 405 confirms the endpoint is live and POST-only.
- **Batching is load-bearing.** A single-question `POST` of q01 alone returns **0.15**; in the 5-question batched round q01 reads 0.85–0.88. The context the other four questions carry materially changes the answer. Comparisons must therefore be drawn from **batched** rounds only — a single-question probe is not a substitute and must not be compared against corpus values.
- **Dedup key:** `(qid, p, round)` — the round file and `history.jsonl` carry different `ts` for the same verdict, so dedup on `ts` double-counts (r222/r223 lesson). 2,156 unique verdicts after dedup.
- **σ≈0 guard:** \|dev\| was checked against the 0.05 floor **first**, every time, before any z was read. This round it mattered: **q08 has z = −2.09 on the all-model baseline while its \|dev\| is only 0.0192** — the largest z is the smallest real movement. A z-first reading would have raised a false drift flag on a cathedral member. Conversely q13 has z = +2.53 on \|dev\| 0.0246 — same trap, opposite sign.
- **Baselines are model-segmented.** The corpus spans the r396 `jev-1.13.0 → jev-1.14.0` boundary (399 rounds on 1.13.0, 34 on 1.14.0). Pooling across it inflates sigma and manufactures supra-threshold z on sub-threshold shifts (measured r413). **Both** the 1.14.0-only and all-model baselines are reported above, and they agree.
- **History table regenerated programmatically** from `history.jsonl` — the r6 lesson that a hand-typed comparison table is a hand-typed claim.
- **The corpus contains duplicate round records** (rounds 384–391 each appear twice in `history.jsonl`, from the r229 reissue defect). Dedup on `(qid, p, round)` removes the inflation; the all-time cathedral counts above are the deduped ones.
- **Delivery:** NAS at 100 % ⇒ `/workspace/research/jev_hourly_report.md` **cannot be written this session**; the durable copy is this file, committed to `SuperInstance/research` and verified byte-for-byte through the remote blob API.
