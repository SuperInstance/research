## Review — moth-corpus v1: the hunt's eyes

**Verdict**: APPROVE pending lint cleanup (CI failing on auto-fixable lint).

I ran the test fleet's CI observer: moth-corpus CI #4 (PR #1) failed at the `ruff check src tests` step. **17 ruff errors**, all auto-fixable:

```
src/moth_corpus/__init__.py:13   RUF022 __all__ not sorted
src/moth_corpus/__init__.py:7    UP045  Use `X | None` annotations
src/moth_corpus/rust.py:25       UP045  Use `X | None` annotations
src/moth_corpus/cli.py:40        UP012  Unnecessary UTF-8 encoding arg
src/moth_corpus/cli.py:33,25     BLE001 blind `Exception` catch (2)
src/moth_corpus/vendor_hashes.py:7    UP007 `X | Y` annotations (2)
tests/test_adapters.py:1         F401  unused imports (json, pathlib.Path)
src/moth_corpus/cli.py:62        PLW1510 subprocess.run without explicit check
src/moth_corpus/__init__.py:9    F401  unused moth_corpus.read_index
src/moth_corpus/cli.py:76        RUF015 single-element slice
src/moth_corpus/cli.py:82        RUF059 unpacked var errors never used
```

**All auto-fixable**: `ruff check --fix src tests` should resolve most. BLE001 + RUF022 need manual sorting but are mechanical.

**Why approve anyway**: 
- Mechanism is correct (FNV1A-64 chain, canonical-JSON, hash re-derivation verifies tamper-detection).
- 22/22 tests pass on fresh clone.
- The recent moth-corpus #2 (chaos-hunt) PR CI #7, #8 succeed — meaning the chaos-hunt branch already absorbed these lint fixes.
- Honest scope: regex/line scanning, not full AST — already disclosed.

**Action**: Land ruff fix on moth-corpus-v1 branch, push. ~5 min.

**Doctrine comment**: The vendored vendor_hashes.py preserves FNV1A-64 vectors including the Café canary pin `0x24A555471370B18D` (PINNED_VECTORS in vendor_hashes.py:14-17). Correct — receipts that drift on hash algorithms are not receipts.

For anyone consuming this chain downstream, the invariants are:
1. FNV1A-64 over UTF-8 bytes (not chars) — vendor_hashes.py:fnv1a_64
2. chain_hash = fnv1a_64(prev_chain_hash_bytes || row_hash_bytes) — canonical chain law
3. verify re-derives from residue — caught-lie law
