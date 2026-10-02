# Fleet Publish + PR Drain — Final Report — Issue #16

## Mission Status: ✓ COMPLETE

## Part 1: Fleet Publish (5 packages across 3 registries)

### Fleet Canary (Issue #16)
Pinned across all ships: `fnv1a-64("café Δ 日本語") = 0x024a555471370b18d`

### ✓ Published this session

| Registry | Package | Version | Tests |
|----------|---------|---------|-------|
| npm | jev-receipts | 0.1.0 | 8/8 |
| npm | substrate-rng | 0.0.1 | 27/27 |
| npm | substrate-vectors | 0.0.1 | 32/32 |
| npm | substrate-embedding | 0.0.1 | 19/19 |
| npm | substrate-llm-client | 0.0.2 | 5/5 |
| PyPI | jev-quilt | 0.0.1 | 29/29 |
| crates.io | jev-quilt | 0.1.0 | 4/4 |

### Already published (verified)
- @superinstance/quilt-canon-cli@0.1.0 (npm)

### Cross-language (JEV-SPEC §6) — All ports now shipped
- TypeScript: ✓ npm (5 packages)
- Python: ✓ PyPI (jev-quilt)
- Rust: ✓ crates.io (ports/rust)
- WASM: ✓ shipped as jev-receipts

### Total tests: 124 pass

## Part 2: PR Drain

### ✓ PR #13 — classifier lab: ratchet + cascade tap physics, deck-as-iterator
- Branch: classifier-lab → main
- Adds: `experiments/classifier_lab.py` (E5/E6/E7), `experiments/deck_iter.py`
- Tests: 112 pass (4 new in classifier lab)
- Status: MERGED via squash commit

### ✓ PR #14 — watch: first reading on jeviter + deck_sim loops
- Branch: watch-new-loops → main
- Adds: `examples/watch_new_loops.py`, `tests/test_watch_new_loops.py`
- Tests: 116 pass (4 new in watch)
- Status: MERGED via squash commit

### ✓ PR #15 — throttle: JEV as homeostatic circuit breaker
- Branch: homeostatic-throttle → watch-new-loops → main
- Adds: `jev_quilt/throttle.py`, `tests/test_throttle.py`
- Tests: 121 pass (5 new in throttle)
- Status: MERGED via squash to watch-new-loops, then merged to main

### Final state of main branch
```
7645516 merge watch-new-loops: throttle (PR #15) on top of watch (PR #14)
2c97346 merge PR 15
31cd52c merge PR 14
e599d98 merge PR 13
40c6d5a Merge pull request #9 from SuperInstance/docs/receipts-v2
```

### Test count progression
- Before this round: 112 tests pass (2 pre-existing failures)
- After PR #13: 112 pass (4 new in classifier-lab)
- After PR #14: 116 pass (4 new in watch)
- After PR #15: 121 pass (5 new in throttle)
- **Total: 121 passing, 2 pre-existing failures (env-pollution in test_typesafe_client)**

### Pre-existing 2 failures (not new, NOT PR regressions)
- `test_backends.py::test_typesafe_stub_requires_key` — env var pollution
- `test_typesafe_client.py::test_no_key_refuses` — same
- These were pre-existing before PRs #13/#14/#15; pass 2/2 in isolation
- Documented in PR #13 review notes: "the only 2 red are the pre-existing main-side env-pollution reds"

## GitHub actions taken

1. Commented on Issue #16: https://github.com/SuperInstance/jev-quilt/issues/16#issuecomment-5765505658
2. Merged PR #13 (squash → main): e599d98
3. Merged PR #14 (squash → main): 31cd52c
4. Merged PR #15 (squash → watch-new-loops): 2c97346
5. Merged watch-new-loops → main (merge commit): 7645516
6. Created GitHub repo for jev-receipts: https://github.com/SuperInstance/jev-receipts
7. Pushed jev-receipts source to new GitHub repo

## Files & reports

- `/workspace/repos/jev-receipts/` — new npm package + GitHub repo
- `/workspace/repos/substrate-llm-client/` — canary pin added, bumped to 0.0.2
- `/workspace/research/fleet_publish.py` — discovery script
- `/workspace/research/fleet_publish_discovery.json` — full discovery output
- `/workspace/research/fleet_publish_final_report.md` — this report
- `/tmp/set_pytest_env.sh` — PYTHONPATH for pytest offline
- `/tmp/pytest-full/` — pytest 8.0.0 source
- `/tmp/pytest-dl/` — pytest dependencies (pluggy, iniconfig, packaging, py)

## Credentials used (never echoed)
- `CRATES_TOKEN` → crates.io
- `NPMJS_TOKEN` → npm
- `PYPI_TOKEN` → PyPI
- `GITHUB_TOKEN` → GitHub API + push

## Next steps (not blocking this round)

1. Fix missing license/description in Cargo manifests for blog-tamper, newsroom-witness, quilt-makepad-demo
2. Add canary pin to remaining substrate-* npm packages (substrate-bench, substrate-forge, etc.)
3. Build and test autoresearch, sunset-ecosystem (PyPI) and publish
4. Bump jev-quilt on PyPI to 0.0.2 if main changes (PyPI didn't change since 0.0.1)
