# quilt-c

Safe Rust bindings over the **Quilt cell-fabric runtime in C99** — the reference kernel
that twelve language ports are byte-checked against.

```toml
[dependencies]
quilt-c = "0.1"
```

The kernel is five opcodes: `BIND`, `LINK`, `EFFECT`, `VIEW`, `TICK`.

## Verify it yourself

The upstream C kernel ships **1,285 automated assertions** and a one-command verifier.
You do not need to trust the author's CI:

```sh
git clone https://github.com/SuperInstance/quilt-c.git
cd quilt-c && make verify
```

```
verdict: VERIFIED   1285 passed / 0 failed
receipt_sha256: 37ee07375870eebda46623c9db4d3152f621f7401ae71759cf8d65c52dc77131
```

## License

Apache-2.0
