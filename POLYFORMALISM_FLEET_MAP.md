# Polyformalism Fleet Map — 7 Ports, 1 Canon

## Status (Sept 22, 2026)

```
                    ┌──────────────────────┐
                    │  Quilt Canon         │
                    │  Fleet Canary:       │
                    │  0x024a555471370b18d │
                    └──────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Python   │   │ TypeScript│   │ Rust     │
        │ port 1   │   │ port 2   │   │ port 3   │
        └──────────┘   └──────────┘   └──────────┘
              │               │               │
              ▼               ▼               ▼
        polyvocoder     polyvocoder-     polyvocoder-
        (reference)     bindings        rust (WASM)
              │               │               │
              └───────┬───────┴───────┬───────┘
                      │               │
                      ▼               ▼
                ┌──────────┐   ┌──────────┐
                │ Bash     │   │ JS ESM   │
                │ port 4   │   │ port 5   │
                └──────────┘   └──────────┘
                      │               │
                      └───────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ C#/.NET  │   │ SQL      │   │ Swift    │
        │ port 6   │   │ port 7   │   │ port 8   │
        └──────────┘   └──────────┘   └──────────┘
        polyvocoder-   polyvocoder-    (planned)
        csharp         sql (SQLite)
```

## Per-Port Stats

| Port | Repo | Lang | Size | Tests |
|---|---|---|---|---|
| 1 | polyvocoder | Python | ~22KB | 7 |
| 2 | polyvocoder-bindings | TypeScript | ~5KB | 0 |
| 3 | polyvocoder-rust | Rust | ~5KB | 5 |
| 4 | scripts/verify_canary.sh | Bash | ~3KB | 0 |
| 5 | (inline) | JS | inline | 0 |
| 6 | polyvocoder-csharp | C#/.NET 9 | ~5KB | 0 |
| 7 | polyvocoder-sql | SQL | ~3KB | 0 |

## Use Cases by Port

| Port | Best for |
|---|---|
| Python | Reference, prototyping, JEV oracle calls |
| TypeScript | Browser UIs, Cloudflare Workers, Node services |
| Rust | WASM modules, embedded firmware, CLI tools |
| Bash | Cron jobs, server-side automation |
| JS ESM | In-page browser rendering |
| C#/.NET 9 | Windows-native apps, Unity, enterprise backend |
| SQL | In-database canon queries, archives |

## Verification

```bash
bash /workspace/research/scripts/verify_canary.sh
```

All 6 ports (excluding SQL due to SQLite unsigned limitations) verified byte-exact.

## Adding a New Port

1. Implement `fnv1a_64(s: str) -> int` in target language
2. Encode `"café Δ 日本語"` as UTF-8
3. Verify hash == 2,640,610,520,279,855,501
4. Add to verify_canary.sh
5. Update this map

