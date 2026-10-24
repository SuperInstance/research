# JEV Continuous Probe — Round 4 (2026-10-24T16:03:48Z)

**Model:** `jev-1.14.0` (same as baseline) · **5 questions** · batch latency 0.146s · exit 124 (timeout, clean SIGTERM after 1 round)
**Prior round:** r003 @ 2026-10-24T09:03:53Z (`jev-1.14.0`) · **prior-prior:** r002 @ 2026-10-24T08:04:27Z (`jev-1.14.0`) · **r001** @ 2026-10-20T09:05:37Z (`jev-1.13.0`)

## Headline

| Metric | This round | Prior round (09:03Z) | Prior-prior (08:04Z) | Baseline (7 reps x 22 q) |
|---|---|---|---|---|
| **mean_p** | **0.1740** | 0.4520 | 0.4560 | 0.4829 (pool mean) |
| Questions at p >= 0.70 | **0 / 5** | 2 / 5 | 2 / 5 | 8 / 22 |
| Drift > 0.05 | **None** | None | None | — |
| Max \|dev\| vs baseline | **0.0086** | 0.0114 | 0.0086 | — |

**Verdict: no canon drift.** The mean_p collapse from 0.452 to 0.174 is a
**class-mix artifact, not a change in the canon.** This round drew 5 of 5
questions from the 14-qid *below* pool and 0 of 5 from the 8-qid *BEDROCK* pool.
Every one of the five qids sits within 0.0086 of its own baseline mean.

## The round

| p | Category | Question | Class | Baseline mean | Deviation | own sigma | z |
|---|---|---|---|---|---|---|---|
| 0.18 | speculative | Is JEV the synaptic spike between cells? | below | 0.184 | -0.0043 | 0.0049 | -0.87 |
| 0.09 | cross | Does the canon require multi-LLM agreement for promotion? | below | 0.096 | -0.0057 | 0.0049 | -1.15 |
| 0.32 | speculative | Is the signal-chain framing canonical? | below | 0.316 | +0.0043 | 0.0118 | +0.36 |
| 0.04 | adversarial | Are cells parameters, not scars? | below | 0.040 | +0.0000 | 0.0000 | n/a |
| 0.24 | cross | Is substrate-canon validated by both JEV and writers' room? | below | 0.249 | -0.0086 | 0.0035 | -2.45 |

**Bedrock (p >= 0.70): 0 of 5.** No question in this draw reached the
bedrock band — but that is because **no bedrock question was drawn**, not because
any doctrine lost confidence. The five qids drawn are the ones the baseline
predicts should score low: baseline means 0.184, 0.096, 0.316, 0.040, 0.249.

## Drift > 0.05 — none

| p (now) | baseline mean | dev | own spread | own sigma | verdict |
|---|---|---|---|---|---|
| 0.18 | 0.184 | -0.0043 | 0.0100 | 0.0049 | within own spread |
| 0.09 | 0.096 | -0.0057 | 0.0100 | 0.0049 | within own spread |
| 0.32 | 0.316 | +0.0043 | 0.0400 | 0.0118 | within own spread |
| 0.04 | 0.040 | +0.0000 | 0.0000 | 0.0000 | within own spread |
| 0.24 | 0.249 | -0.0086 | 0.0100 | 0.0035 | within own spread |

**No deviation exceeds 0.05.** The largest is 0.0086 (`substrate-canon validated by both JEV and writers' room`), which is 0.0086 below the flat threshold and sits inside its own measured spread of 0.0100.

### The sigma~0 trap, again, in a new disguise

The largest z in this round is **-2.45** — on a deviation of **-0.0086**
(`substrate-canon validated by both JEV and writers' room`, own sigma 0.0035).
The eye catches the z and reads it as a 2.45-sigma event. It is a 0.0086 move
on a 0.0035-sigma question, i.e. **less than 3% of the drift threshold**, and it
is inside the question's own observed spread. **Check |dev| against 0.05 first;
the largest z is routinely the smallest real movement.** This is the fourth
recurrence of that shape: q07 at -1.77 sigma on a 0.0076 dev (r221), q20 at
+1.74 sigma on a 0.0146 dev (r221), q12/q05 across the 1.13 -> 1.14 model switch,
and now q20 at -2.45 sigma on a 0.0086 dev (r004).

## Why mean_p 0.174 is a class-mix lottery, not drift

The bank is 22 qids: **8 BEDROCK** (baseline means 0.779-0.970) and **14 below**
(0.029-0.651). A round draws 5 at random. Monte-Carlo over 200,000 draws of
5-of-22 from the baseline means:

- E[mean_p] = 0.4830, sd = 0.1493
- P(mean_p <= 0.1740) = 0.0192  (5th pct = 0.2457, 95th pct = 0.7349)
- **P(0 of 5 bedrock) = 0.075** — a 0/5 draw is COMMON
- P(>=3 bedrock) = 0.235

The predicted mean of the five qids actually drawn is **0.1769**; the observed
mean_p is **0.1740** — agreement to 0.003. The round is a textbook draw.

The same MC also explains the prior round's 5/5-UP sign pattern (P = 0.031 under
a sign test, which looks significant but is exactly what a resampling lottery
produces). The "73/52 up-biased" note in the r003 commit message is a
**single-round sign count, not a property of the bank** — and this round
immediately contradicts it with 3 down / 2 up (DDUUD).

## The decisive check: shared qids are bit-identical across rounds

Because rounds sample different qids, the cleanest drift evidence is a qid
measured in two different rounds. Three are shared with recent rounds:

| qid | r002 (08:04Z) | r003 (09:03Z) | r004 (16:03Z, now) | delta vs prior |
|---|---|---|---|---|
| Does the canon require multi-LLM agreement for promotion? | 0.09 | — | **0.09** | +0.0000 |
| Is JEV the synaptic spike between cells? | — | 0.19 | **0.18** | -0.0100 |
| Is substrate-canon validated by both JEV and writers' room? | 0.24 | — | **0.24** | +0.0000 |

`multi-LLM agreement for promotion` reads **0.09 in r002 and 0.09 now**;
`substrate-canon validated by both JEV and writers' room` reads **0.24 in r002
and 0.24 now**; `JEV the synaptic spike` moved 0.19 -> 0.18. The oracle is
**stable to the grid step.** A canon under drift could not produce identical
verdicts on re-measurement two hours apart.

## Cross-round summary

| round | iso | mean_p | bedrock | max \|dev\| | max \|z\| | draw composition | signs |
|---|---|---|---|---|---|---|---|
| r001 | 2026-10-20T09:05:37Z | 0.4000 | 2/5 | 0.0286 | 4.91 | {'BEDROCK': 2, 'below': 3} | DDUDU |
| r002 | 2026-10-24T08:04:27Z | 0.4560 | 2/5 | 0.0086 | 2.45 | {'below': 3, 'BEDROCK': 2} | UDDDU |
| r003 | 2026-10-24T09:03:53Z | 0.4520 | 2/5 | 0.0114 | 999.00 | {'BEDROCK': 2, 'below': 3} | UUUUU |
| r004 (now) | 2026-10-24T16:03:48Z | 0.1740 | 0/5 | 0.0086 | 2.45 | {'below': 5} | DDUUD |

## Cathedral status (bedrock qids, all-time)

Unchanged — no promotion, no demotion, no class change. The 8 BEDROCK qids were
not drawn this round, so this round contributes **no new evidence** to their
hit-rate either way. A 0/5 draw must not be read as 5 weak results; it is 5
uninformative results.

## Environment

- `/workspace` arrived **EMPTY** (only `.plugin-cache`) — **10th consecutive** time the
  prompt named ephemeral `/workspace/research/` paths that did not exist.
- NAS 100% (0 avail) ⇒ the **29th observation** of the silent-zero trap. The
  durable path was NOT attempted: work was done in `/tmp` (overlay, 28G free) and
  `/workspace/research` + `/workspace/repos/jev-quilt` were symlinked into it.
- `SSL_CERT_FILE` is the gateway-anchor-only bundle again, but the **live leaf
  verified OK** (`Verify return code: 0`, subject `CN = typesafe.ai`) with 147 certs
  in the default context — **no bundle rebuild needed this round** (first time in 14).
- Credential shape: the env provides **`TYPESAFE_AI_TOKEN`**, but the client only
  reads `JEV_API_KEY` / `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY`. Mapped
  `JEV_API_KEY=$TYPESAFE_AI_TOKEN` for the run.
- Model returned `jev-1.14.0` — matches baseline. No model switch.
- `timeout 60` → exit **124**, SIGTERM handler set `running=False` and the process
  exited cleanly after exactly **1 round**. The script's `rounds` positional arg
  does not exist in this variant (it loops on a 3600s sleep), so the timeout is
  the correct one-round control here.
- The script's round counter **restarts at 1 on every invocation** and overwrites
  `jev_sessions/continuous_r001.json`. The prior 08:04Z round is preserved in
  `jev_sessions/rounds/continuous_r2026-10-24T0804Z.json` and was verified
  byte-identical to the pre-run file before the overwrite (md5
  `d2230c2ff283bab59db76b00b35a6809`).

## Open items

- **Round counter is not persistent.** `continuous_rNNN.json` cannot be trusted as a
  sequence number; the `rounds/continuous_r<ISO>.json` archive is the real
  timeline. Recommend the script write the ISO-stamped archive name directly.
- **`/workspace/research/` is not durable across wipes** and the prompt keeps
  naming it. The repo (`SuperInstance/research`) is the durable copy; this report
  is committed there.
- No canon drift to escalate. Next round decides whether the 0/5 draw recurs.
