# The Quilt Polyformalism Fleet — Index

> All polyformalism ports and tooling for the Quilt substrate walker canon-discovery
> system. Every port agrees on the fleet canary
> `fnv1a-64('café Δ 日本語') = 0x024a555471370b18d` (verified byte-exact).

## The Fleet (7 ports)

| Port | Language | Repo | Description |
|---|---|---|---|
| 1 | Python | [SuperInstance/polyvocoder](https://github.com/SuperInstance/polyvocoder) | Reference implementation, ~22KB |
| 2 | TypeScript | [SuperInstance/polyvocoder-bindings](https://github.com/SuperInstance/polyvocoder-bindings) | Schema-parity client, browser/Node |
| 3 | Rust | [SuperInstance/polyvocoder-rust](https://github.com/SuperInstance/polyvocoder-rust) | No-std, WASM-compatible, ~5KB |
| 4 | Bash | `scripts/verify_canary.sh` | Cron-style, no native 64-bit |
| 5 | JS ESM | (inline in verify_canary.sh) | Browser-side |
| 6 | C#/.NET 9 | [SuperInstance/polyvocoder-csharp](https://github.com/SuperInstance/polyvocoder-csharp) | Cross-platform Windows/Linux/macOS |
| 7 | SQL | (planned) | SQLite byte-exact FNV-1a |

## Documentation by Port

### Python — `polyvocoder`
- `polyvocoder/README.md` (173 lines) — overview
- `polyvocoder/docs/WHITEPAPER.md` (183 lines) — abstract
- `polyvocoder/docs/A2A_GUIDE.md` (288 lines) — agent integration
- `polyvocoder/docs/ARCHITECTURE.md` (231 lines) — system design
- `polyvocoder/docs/EXAMPLES.md` (293 lines) — 10 examples
- `polyvocoder/docs/HEADS.md` (211 lines) — adding new modalities
- `polyvocoder/docs/POLYFORMALISM.md` (159 lines) — schema parity
- `polyvocoder/docs/FLEET_CANARY.md` (193 lines) — canary verification
- `polyvocoder/docs/TROUBLESHOOTING.md` (249 lines) — common issues

### TypeScript — `polyvocoder-bindings`
- `polyvocoder-bindings/README.md` — overview + examples
- `polyvocoder-bindings/docs/A2A_GUIDE.md` — TypeScript integration
- `polyvocoder-bindings/docs/TYPES.md` — type definitions
- `polyvocoder-bindings/docs/EXAMPLES.md` — 10 examples
- `polyvocoder-bindings/docs/POLYFORMALISM.md` — schema parity
- `polyvocoder-bindings/docs/DEPLOY.md` — backend deployment

### Rust — `polyvocoder-rust`
- `polyvocoder-rust/README.md` — Rust quickstart
- `polyvocoder-rust/src/lib.rs` — FNV-1a 64-bit + serde types
- 5 unit tests (canary, dials, fnv1a empty, fnv1a one byte, features serde)

### C#/.NET — `polyvocoder-csharp`
- `polyvocoder-csharp/README.md` — .NET 9 quickstart
- `polyvocoder-csharp/Program.cs` — canary + sample result

### Bash / Fleet Verifier
- `scripts/verify_canary.sh` — verifies all 6 ports byte-exact

## Cross-Port Documentation

- `substrate-walker/POLYFORMALISM_PORT.md` — port table for substrate walker
- `substrate-walker/DISCOVERY_LOOP.md` — A2A guide for canon discovery
- `substrate-walker/DOCTRINE_PAPER.md` — canonical reference
- `substrate-walker/lore_explorer.html` — interactive A2A-friendly browser

## Canonical References

- **Fleet Canary**: `0x024a555471370b18d` (decimal 2,640,610,520,279,855,501)
- **5 Bedrock Doctrines**: cells_are_scars, oracle_is_heard,
  witness_log_is_prediction, canon_gate_is_chord, substrate_quantum
- **Composite Score Threshold**: 0.7 (for canon promotion)
- **Stable Canon Count**: 9 cells (Sept 22)

## Verification

```bash
# Verify all 6 ports agree on the canary
bash /workspace/research/scripts/verify_canary.sh
```

Output:
```
Python     :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
TypeScript :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
Rust       :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
JS ESM     :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
C#/.NET    :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
Bash (py)  :        ✓ 0x24a555471370b18d (decimal 2640610520279855501)
✅ All ports pass the canary
```

## Philosophy

> **Polyformalism** is the principle that a canon should be reproducible across
> languages. The fleet canary is the witness of that principle: all ports compute
> the same hash byte-exact, proving the canon is portable.

A polyformalism port is a stress test. Each language is a medium, not a ranking.
Same lore, six languages, byte-exact.

