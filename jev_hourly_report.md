# JEV Continuous Probe — Round 1

**Run:** 2026-10-20T09:05:37Z · model `jev-1.13.0` · 5 questions · batch latency 0.169s

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4000** |
| Questions at p >= 0.70 | **2 / 5** |
| Drift vs prior rounds | **Not computable — no prior rounds exist** |

## p >= 0.70 (bedrock canon)

| p | Category | Question |
|---|---|---|
| **0.95** | numerical | Is cosine similarity (a . b) / (\|a\| \|b\|)? |
| **0.77** | numerical | Is 0xcbf29ce484222325 the FNV-1a 64-bit offset basis? |

Below threshold — the discriminators behave correctly, they just score low by design:

| p | Category | Question |
|---|---|---|
| 0.16 | speculative | Is JEV the synaptic spike between cells? |
| 0.10 | cross | Does the canon require multi-LLM agreement for promotion? |
| 0.02 | adversarial | Is the substrate designed, not grown? |

**Read:** the two numerical facts hold as canon. The adversarial inversion ("designed, not grown") is correctly rejected at 0.02 — JEV is not answering by keyword overlap, it's discriminating. The low mean_p (0.40) is a **good** sign here, not a warning: 3 of 5 questions are designed to be false.

## Drift > 0.05

**None reported, because there is no baseline.** This is round 1 of 1.

Verified rather than assumed:
- `jev_sessions/continuous_r*.json` — **0 files** in the working tree.
- `git log --all --diff-filter=A -- 'jev_sessions/continuous_r*'` — **no commits, any branch**. The file has never been committed in the repo's history.
- `jev_hourly_report.md` — did not previously exist.

## Blockers found and fixed

The probe could not run as shipped. Three independent faults, in order:

1. **NAS full.** `/workspace` is an NFS mount at **100% quota (500G used, 0 available)**, mounted but empty. Every path the script depends on was gone. Recovered by shallow-cloning `SuperInstance/research` and `SuperInstance/jev-quilt` to `/tmp`.
2. **Env-var name mismatch (silent, the real one).** `typesafe_client.py:43-47` accepts only `JEV_API_KEY` / `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY`. The environment ships **`TYPESAFE_AI_TOKEN`**. The key was present and valid the whole time; the client just refused to look at it. Confirmed live (`available(): True`, model `jev-1.13.0`, 184ms). **A missing credential and a misnamed one produce the identical error message.**
3. **Wrong endpoint while probing.** The client posts to `/v1/systemone`; `/decide`, `/v1/decide` and `/batch` all 404. Guessing the path would have produced a false "API is down."

## Design defect: this probe cannot measure drift

`round_num = 0` is a **process-local counter that resets on every launch**, and the script never reads prior artifacts (only one `open()`, mode `'w'`, the file it is writing). Consequences:

- Every fresh start overwrites `continuous_r001.json`. History is destroyed on each restart.
- There is no load, compare, or delta step — so "drift > 0.05" has nothing to diff against, ever.
- `random.sample(QUESTION_BANK, 5)` draws a **different 5 of 23 each round** with no seed, so round-to-round movement conflates real drift with which questions happened to be drawn.

Until it loads prior rounds and fixes or records the sample, per-question drift across rounds is not a valid signal.

## Recommended fixes

1. In `typesafe_client.py`, accept `TYPESAFE_AI_TOKEN` in the key chain.
2. Derive `round_num` from existing artifacts (`max(round)+1`), not from zero.
3. Persist the sample or seed it, so rounds are comparable.
4. Treat `/workspace` as unusable until the NAS quota clears; run from a local clone.

---
*Round 1. Artifact: `jev_sessions/continuous_r001.json`.*
