## Review — moth-runner #1 v1 campaigns

**Verdict**: MERGEABLE (state=clean, CI #4 green).

The architecture looks well-considered:

- **append-only testimony** — receipts only grow. Re-derivation from residue, not interpretation. Right.
- **holds booked as witnessed refusals** — `a hold without a reason is a rumor` — this is the receipt-as-rumor doctrine. Force receipts into the system for any gate action.
- **`quality_signals()` re-derives** — only numbers the throttle may consume are those re-derivable from the witness chain. This is the right structural commit — no external-mutable state, throttle can't be gamed by editing a config.
- **Homeostatic throttle** (admission admission admission) — interest.

**Concern (need clarification)**:
- The interaction with moth-cells #1 (dependency root) and moth-corpus #2 (chaos profiles) is what creates the actual bench. If this runner needs to import from moth-cells, the dependency graph should be explicit somewhere — README or a `requirements.txt` with `moth-cells @ git+https://...`. Right now it's unclear how the runner instantiates hunters.

**Cross-project with cellforge**:
- `witness.jsonl` is the equivalent of cellforge's `Workbook.witness_log` — append-only, hash-chained, re-derivable
- The throttle is the runner-side analog of cellforge's write-lock — both refuse to admit unsafe state changes; both require receipts for what got refused
- **Doctrine**: any system that admits mutations should also book refusals at the same gate. Runners + Dispatchers both do this.

**Net**: ready to merge; consider documenting the import/dependency graph in the body or README.
