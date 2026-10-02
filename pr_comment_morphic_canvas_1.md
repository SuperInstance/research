## Review — morphic-canvas #1 substrate-v0

**Verdict**: **MERGEABLE** (state=clean, CI #12 green).

This is a beautiful execution. The architecture:

> "one WebGPU storage buffer is model + memory + world + render target"

Maps directly to Quilt's cell substrate:

| morphic-canvas | cellforge-equivalent |
|----------------|----------------------|
| One shared storage buffer | Workbook (full state grid) |
| Single compute pass fusing forward+gradient+EMA+Lamport | dispatcher.tick() (all in one pass) |
| Fragment shader reads same addresses | Projection/Viewer cell reads from canon |
| Stop-gradient EMA shadow | WITNESS_CELL (forks write to prediction, canon reads from witness) |
| Per-cell Lamport clock | Workbook.vector_clock |

**Doctrine sync**:
- "The gradient is the prediction error" because the target is a stop-gradient EMA shadow — no backward graph. This is JEPA-as-racehorse made literal. JEPA = predictive embedding, gradient = prediction error = the canonical learnable signal.
- 5 law tests (`test_substrate.js`) bound the invariant surface — same pattern as cellforge's 42 tests.

**Suggested naming alignment** (optional for next rev):
- Call the stop-gradient shadow a `WITNESS_CELL` instead of "EMA shadow" — would make the substrate/witness correspondence obvious to Quilt readers.
- Call the per-cell Lamport clock a `vector_clock` (cellforge already uses this term).

**Cross-project insight (cellforge ↔ morphic-canvas)**:
The dispatcher-as-play-head architecture generalizes. morphic-canvas is essentially cellforge-on-GPU where:
- workbook = one shared buffer
- dispatcher tick = one fused pass
- worker = GPU thread/wave
- witness = stop-gradient shadow
- rewind = re-bind buffer to early address range
- predicting = second shadow buffer

The **same** state/execution inversion principle. Different substrate.

**Net**: ready to merge.
