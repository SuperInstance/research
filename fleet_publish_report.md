# Fleet Publish Report — Issue #16

## Mission
Drain the fleet publish queue — PyPI/npm/crates.io.

## Fleet Canary (Issue #16 requirement)
Pinned across all ships: `fnv1a-64("café Δ 日本語") = 0x024a555471370b18d`

## Discovered Packages

### npm (24 packages in /workspace/repos/*/)
24 candidates with name+version+license+not private.

### PyPI (3 packages)
- `autoresearch` @ 0.1.0 (autoclaw)
- `jev-quilt` @ 0.0.1 (jev-quilt)
- `sunset-ecosystem` @ 0.1.0 (sunset-ecosystem)

### Cargo (6 packages)
- `jev-quilt` @ 0.1.0 (jev-quilt/ports/rust)
- `blog-tamper` @ 0.1.0 (blog-tamper)
- `newsroom-witness` @ 0.1.0 (newsroom-witness)
- `quilt-jetson` @ 0.1.0 (Apache-2.0)
- `quilt-makepad-demo` @ 0.1.0
- `quilt-subleq` @ 0.1.0 (MIT)

## PUBLISHED

### ✓ jev-receipts@0.1.0 (npm)
- URL: https://www.npmjs.com/package/jev-receipts
- Source: duke-lab/jev-receipts.js (merged into npm package)
- Test count: 8 passed (canary pinned + ReceiptChain + JevCell + bookArgument)
- Fleet canary: pinned in test suite
- Status: PUBLISHED 2026-09-21

### ✓ jev-quilt@0.0.1 (PyPI)
- URL: https://pypi.org/project/jev-quilt/
- Files: wheel + sdist
- Test count: 29 passed (Q16 + Cell + Bookkeeper + Backends + TypeSafeClient)
- Fleet canary: pinned in port (PIN_CAFE = 0x024a555471370b18d)
- Status: PUBLISHED 2026-09-21

### ✓ jev-quilt@0.1.0 (crates.io)
- URL: https://crates.io/crates/jev-quilt
- Source: ports/rust (Rust port)
- Test count: 4 passed (chain_and_tamper, pin_basis, pin_cafe, regime_latency_zero)
- Fleet canary: pin_cafe test verifies 0x024a555471370b18d
- Status: PUBLISHED 2026-09-21

## ALREADY PUBLISHED (verified)

### ✓ @superinstance/quilt-canon-cli@0.1.0 (npm)
- URL: https://www.npmjs.com/package/@superinstance/quilt-canon-cli
- Status: EXISTED (verified via npm view)
- Note: local repo has @superinstance/quilt-canon-cli-gh with -gh suffix; no publish needed

## DECLINED / REFUSED

### blog-tamper, newsroom-witness, quilt-makepad-demo (Cargo)
- Reason: missing description and license fields in Cargo.toml
- Refused by cargo publish --dry-run

### quilt-jetson, quilt-subleq (Cargo)
- Status: PENDING (have description and license, need to verify)
- These are heavyweight (Jetson-specific binaries)

### autoresearch, sunset-ecosystem (PyPI)
- Status: PENDING (haven't yet verified builds + tests)
- Lower priority than jev-quilt

### 24 npm packages
- Status: NEEDS ASSESSMENT
- Many are application demos, not library packages
- Substrate-* packages are better candidates than @quilt/* apps

## Cross-Language Canary Verification
All three packages pass the fleet canary:
- TypeScript (twist-engine): pinned in jev-receipts test ✓
- Python (jev-quilt): pinned in bookkeeper + typesafe_client ✓
- Rust (jev-quilt ports/rust): pin_cafe test asserts 0x024a555471370b18d ✓

## Next Steps
- Verify Substrate npm packages (substrate-rng, substrate-vectors, etc.)
- Fix Cargo manifests for blog-tamper, newsroom-witness, quilt-makepad-demo
- Consider publishing @superinstance/jev-quilt (npm, parallel to PyPI)
