# Continuous JEV Probe — Schedule Plan

> *How to wire up hourly JEV drift detection without burning tokens.*

## The script

`/workspace/research/jev_continuous_probe.py`

- Loops every hour (3600s)
- Each round: 5 random questions from a 22-question bank
- Saves to `/workspace/research/jev_sessions/continuous_rNNN.json`
- Mean p logged each round
- Stops cleanly on SIGTERM

## How to schedule it

Use `mavis cron create`:

```bash
mavis cron create \
  --agent-name me \
  --cron-name "JEV hourly probe" \
  --schedule "0 * * * *" \
  --prompt "Run /workspace/research/jev_continuous_probe.py for one round. Read /workspace/research/jev_sessions/continuous_rNNN.json. Compare to previous round. Report drift > 0.05 in any category." \
  --active-hours '{"start":"00:00","end":"23:59"}'
```

OR run as a long-lived background process:

```bash
nohup python3 /workspace/research/jev_continuous_probe.py > /tmp/jev_cont.log 2>&1 &
```

The cron-task approach is better — agent reviews output each hour, no resource leak.

## What drift looks like

| Mean p across rounds | Status |
|---------------------|--------|
| 0.70 - 0.80 | canon is bedrock, no drift |
| 0.55 - 0.70 | canon still strong, but new ambiguities surfacing |
| 0.40 - 0.55 | canonical doctrines losing confidence — investigate |
| < 0.40 | major drift — re-run JEV with different model, check for model updates |

## What we'll learn

After 24 hours:
- Whether JEV's verdicts drift over time (probably not — std ≤ 0.013 in Session 7)
- Which doctrines are most stable across model versions
- Which probes produce the highest variance

After 1 week:
- Full weekly stability report
- Identify any doctrines that need re-validation

## Cost estimate

5 questions × 24 rounds/day × 365 days = 43,800 questions/year
~30,000 tokens/day, ~10M tokens/year
JEV pricing ~$2/MTok = ~$20/year

Acceptable. Run.

## What we'll save

Per round:
```json
{
  "round": 1,
  "iso": "2026-09-21T16:25:00Z",
  "questions": [
    {"category": "canon", "q": "...", "p": 0.93, "confidence": 0.95},
    ...
  ],
  "latency_s": 0.4
}
```

Easy to graph p over time per category. Heatmap of doctrine stability.
