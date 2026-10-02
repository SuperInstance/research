## Review — moth-corpus #2 chaos-hunt pack

**Verdict**: **MERGEABLE (state=clean, CI #7, #8 green).**

Mechanism review (verified against `src/moth_corpus/chaos.py` shipped):

- **Profile contracts correctly enforced**: `rushing` claims every cell (precision-blind test); `dull` walks but never claims (refusal-track test); `sycophant` claims only on cells the planted-truth panel flags (confidence-curve test). These are the right adversarial profiles.

- **`confidence_q16=65536` invariant on sycophant**: `{65536}` exact match, both seeds. This means sycophant never admits uncertainty — it's the textbook charlatan signal. Correct.

- **Speculative tag (`experiment=SPECULATIVE`)** + per-row `dice_seed`: lets the bench attribute findings to the right generator without needing a separate header. Clean.

- **`splitmix64` vendored inline** at `chaos.py:43` (`_GOLDEN = 0x9E3779B97F4A7C15`, keyed by `(seed,tick)`). stdlib only — no sibling-repo imports. Determinism survives refactors.

- **Café canary pin preserved**: `0x24A555471370B18D` in `vendor_hashes.py`, with `:noqa: UP012/UP007 -- vendored verbatim`. Correct refusal to upgrade.

- **Stacked on #1** as claimed: 4 commits, base `moth-corpus-v1`, +592/−14 across 19 files. `read_index` still exported (the test_receipts import-line change drops only an unused name).

**Chain law intact**: `verify_rows` on shipped rushing fixture → `(True, [])`; one-field value tamper → `(False, [...])` — the refusal IS loud.

**17 test functions (37 collected cases)**, each pinning a body claim by name. Each mechanism → each test → mapped.

**Net**: ready to merge into `moth-corpus-v1` once #1 lands. The basis is healthy.

**Suggestion (optional)**: when the chaos profiles grow beyond 3 (5+, 10+), consider a `register_profile()` API so consumers can extend without forking — the splitmix64 seed-mixin is already 90% of the way there.
