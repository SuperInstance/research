## Review — moth-honest v1: the evaluator

**Verdict**: **MERGEABLE** (CI #4 green, state=clean).

This is the right answer to the 78.2% self-report problem. The doctrine is correct:

> **our own number before yours is trusted**

Concretely:
- **planted.py** seeds 7 bug-class exercises + 3 zero-FN controls. The clean-control inclusion is important — it prevents hunters from gaming by claiming everywhere.
- **evaluate.py** with **explicit refusal track** is the load-bearing piece. A hunter that walks but abstains earns `correct_refusals` (positive restraint). A hunter that walks but stays silent earns nothing — silence ≠ refusal, refusal is bookkeeping under chain law.
- **Per-exercise verdict** is right granularity — aggregate scores hide per-class weakness.

**Cross-project alignment with moth-ledger**:
- moth-honest's planted ground truth closes the loop with moth-ledger's POLARITY field. Negative refusal (starvation = no claim made, capacity testimony) vs positive refusal (decoy_resisted = claim made but explicit restraint). The honest hunter books both under `REFUSAL/v2` with `polarity=` distinguishing them.
- Without this, a "polite" hungry hunter gets indistinguishable virtue credit from a refraining strategic hunter.

**Suggestion**: include in PR body an example run (`python -m moth_honest plant && python -m moth_honest evaluate out.jsonl`) — show actual TP/FP/FN counts for a known input. Buyers of an evaluator need to see it grade.

**Net**: ready to merge.
