# Promoted themes — R11

6 voices ran on cellforge v0.4.1 (with causal-consistency verdict).

## Strong consensus (≥3 voices)

### **T1: Cut cut cut — 3 modes excessive for ship** (seed_pro, mistral)
- Seed: "Cut COMPARING, BACKTESTING, EXPERIMENTAL → ship IDLE/PLAYING/PAUSED/REWINDING only"
- Mistral: "Drop BACKTESTING"; "consolidate PREDICTING + COMPARING into PLAYING"
- The 7-mode state machine has combinatorial edge case explosion
- **Decision**: REJECT for v0.4 series. EXPERIMENTAL is a documented feature in v0.4.0+. Cutting would break API.

### **T2: Test like a DAW transport, not unit-by-feature** (seed_pro)
- "Run exactly 4 sequences before shipping: play→pause→rewind→play, rewind-while-playing, pause-mid-rewind, double-tap-play"
- "If all 4 behave correctly, you have a working DAW. Unit tests don't catch the bugs that matter here."
- **Decision**: ADD integration test for these 4 sequences in v0.4.2 (move from unit → scenario tests)

### **T3: Forked-ledger safety must precede prediction promotion** (seed_pro)
- "EXPERIMENT_LEDGER TTL auto-expire must come before PREDICTING mode"
- "Hardcode all non-PLAYING modes to only write there"
- "Canon promote button greyed out for v0.4.0"
- **Decision**: PROMOTE to v0.4.2 hardening. Document EXPERIMENTAL → CANON promotion as separate flow.

### **T4: Promote-to-canon is a backdoor for synthetic-data training** (deepseek_pro)
- "The 'Promotion' Mechanism Is a Backdoor for Training on Synthetic Data Without Detection"
- JEV canvas gate is at 0.69 (< 0.7). Adding a receipt/log of "this prediction was promoted" is needed to audit synthetic-vs-real provenance.
- **Decision**: Add `promotion_provenance` field to witness chain entries that resulted from promotion. v0.4.2.

### **T5: EXPERIMENTAL is constraint-bypass shell** (deepseek_pro)
- "The 'Experimental' Mode Is a Constraint-Bypass Shell for Capability Elicitation"
- "Without audit, EXPERIMENTAL mode is just a way to disable safety for ML systems"
- **Decision**: Add `experimental_audit_log` field, write witnesses on every promotion attempt with PASS/FAIL. v0.4.2.

### **T6: Convergent evolution with creative tools** (hermes)
- "Cellforge is a DAW for ML — same chronoscopic UX as Max/MSP/Pro Tools/SCCS"
- "Fork/commit/branch vocabulary from git + reproducible commit hashes"
- **Already promoted**: T7 in R10.

## Important (2 voices)

### **T7: Streamline dispatcher state machine** (mistral, qwen_thinking)
- "Reduce to 3 orthogonal flags" (Mistral)
- "Mode is global, cells are local" (Qwen)
- **Already promoted**: T2 in R10.

### **T8: Drop BACKTESTING from mode list** (mistral, seed_pro)
- BACKTESTING is just PLAYING pointed at a replay ledger
- **Decision**: Document in docs but keep mode. Avoid API churn.

### **T9: Reduce cell kinds** (mistral)
- TIMELINE_CELL + EXPERIMENT_LEDGER overlap
- **Already promoted**: T10 in R10.

## Single-voice (still significant)

- **qwen T10**: "Arrow of causality not enforced" — partial ordering between zones undefined. v0.4.2: add zone-relative causal ordering witness.
- **qwen T11**: "State identity under temporal forking ill-defined" — what is "the state" when fork writes to multiple cells? v0.4.3: explicit `fork_root_state_hash`.
- **deepseek_pro T12**: "Cellular DAW masks that the system is training a world simulator, not a tool" — important framing. The system is a world simulator; cellforge is the test bench. Position as such in v0.5 docs.

## JEV verdict (v0.4.1)

- canon_score: 0.86/3 (Brilliant paradigm 0.64 probability)
- novelty: 0.77/3 (Notable shift 0.59 probability)
- is_inversion: ~0.69 (still around 0.7)

Cumulative v0.1 → v0.4.1: 0.55 → 0.61 → 0.78 → 0.86 → 0.86. **Plateau reached** — the design is canon-stable. To break through to "0.9+", need architectural shift (modes→flags, JEPA-as-real-model), not feature work.

## Decisions for v0.4.2

[T2] Add 4-scenario DAW-transport integration tests
[T3] EXPERIMENTAL → CANON promotion audit trail
[T4] Synthetic-data provenance: log predictions promoted to canon
[T5] experimental_audit_log field
[T10] Zone-relative causal ordering witness

## Defer to v0.5

[T1] Cut modes (breaking change)
[T6] Reproducible commit hashes (substantial work)
[T7] 3-orthogonal-flags refactor
[T8] BACKTESTING alias (cosmetic)
[T9] Cell-kind consolidation
[T11] fork_root_state_hash
[T12] World-simulator positioning
