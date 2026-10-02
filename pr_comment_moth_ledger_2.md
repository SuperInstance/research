## Review — moth-ledger trial-balance (Pacioli canary)

**Verdict**: REQUEST CHANGES (merge conflict + 49 ruff errors + CI failing).

### State observed

- mergeable: **False** (state=draft/dirty) — branch is stale against main
- trial-balance branch is at `bf8258a`; main has progressed past it (with ruff-fix-ci-gate landed)
- CI #9, #10 (branch trial-balance): **failed** on `ruff check src tests` (49 errors, mechanical)
- CI #11, #12 (branch ruff-fix-ci-gate): green
- CI #13 (main): green

### Same 17-error pattern as moth-corpus #1

`ruff check --fix` resolves most. Manual fixes needed for `BLE001` and `RUF022`. ~10 minutes of work.

### Suggested action (3 sub-tasks)

1. **`git rebase main`** the trial-balance branch onto current main. Resolves the mergeable=False.
2. Then `ruff check --fix src tests` + manual sorting/typing.
3. Push the rebased-and-cleaned branch. Re-run CI. PR should merge.

### Doctrine check (this is the important part)

The Pacioli canary mechanic is sound and important:

> **Honest close and the honest miss cost the same ink; a book that will not balance was a choice.**

Concretely:
- `verify_chain` is blind to bookkeeping (correct — chain law is residue, not policy).
- `verify_close` re-derives the close from residue (correct — close claims are receipts, not opinions).
- Refusal bookkeeping (REFUSED, MISSED, CAUGHT) preserves honesty as a first-class cell type.
- `ROUND_CLOSE/v1` chained; `verify_close` rejects silent imbalance.
- The seam (chain vs close) is load-bearing — this is the right place to put it.

### Cross-project durable insight (moth-ledger ↔ cellforge)

This is the dual of cellforge's write-lock safety interlock:
- **cellforge**: writes to canon are blocked when dispatcher is PLAYING (force=True bypasses).
- **moth-ledger**: writes to balance are blocked when close doesn't balance (no bypass).

Both systems make honesty the **default state** and require explicit operator action to deviate. Receipted refusal > silent failure.

### Suggestions for the canary itself

1. Add a `close_round_id` cross-ref so multiple rounds in one ledger don't entangle.
2. `TrialImbalance` should carry the **specific imbalance type** (`UNCLOSED`/`DOUBLE_DEBIT`/etc.) — already there per body, confirm in code.
3. The CLI's `--verify-close-id ROW_ID` is good — consider also `--verify-close-all` for batch-check.

### When this lands

The fleet polyformalism canary `0x24a555471370b18d` depends on consistent FNV1A-64 implementations across all moth-* repos. moth-ledger v1 → v2 → trial-balance should preserve the chain law (proven receipt shown — FNV1A-64 of `""` = `0xCBF29CE484222325`). Once trial-balance is rebased + clean, we can proceed.
