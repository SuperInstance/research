# Promoted themes — R10

8 voices ran sequentially on cellforge v0.4.0 design (CELLFORGE_PLAYHEAD.md).
Critical ≥2 voices hit the same theme.

## Strong consensus (≥4 voices)

### **T1: Tick abstraction is a lie** (groq_qwen, qwen_thinking, hermes [T1=time], deepseek_pro)
"The design conflates logical state transitions with physical time."
"Zones A=100Hz, B=1Hz imply global tick sync but it's heterogeneous."
Treatment: `SnapshotStore` separating logical tick index from execution step.
**Promote v0.4.1**: distinguish `logical_tick` from `execution_tick`. A `PLAYING` mode advances logical_tick at zone rate; the dispatcher uses logical_tick + zone for ordering.

### **T2: 7 modes over-engineered; collapse to 3 orthogonal flags** (groq_qwen, seed_pro, mistral, gemma [mode collapse], deepseek_pro [dispatcher=DAW])
"COMPARING is just PAUSED with two timelines. BACKTESTING is just PLAYING at a replay ledger."
"7 modes combinatorial nightmare."
Treatment: 3 flags — `is_playing`, `is_experimental`, `playhead_position ∈ ℤ` (can be past/present/future).
**Promote v0.4.1**: refactor dispatcher state to (is_playing, is_experimental, playhead_position). Drop the Mode enum entirely. PAUSED = (False, _, current), REWINDING = (False, _, tick-N), PREDICTING = (False, True, tick+N), EXPERIMENTAL = (_, True, _).

### **T3: TTL on EXPERIMENT_LEDGER is a mistake** (groq_qwen, seed_pro)
"Auto-expiring predictions will get screamed at when users lose overnight predictions."
Treatment: Manual delete + 3 weeks observation before TTL default.
**Decision**: KEEP manual delete only for v0.4.0; add TTL in v0.5+ with opt-in.

### **T4: Chronoscopic UX is cockpit-grade, novice-hostile** (gemma, mistral)
"10-year-old wants Cmd+Z, gets 12 cell kinds × 3 dimensions."
"DAW metaphor brilliant for pros, terrifying for novices."
Treatment: Layered UI — Beginner (just Play/Pause/Rewind), Power (3D timeline), God (full cell inspection).
**Promote v0.4.1**: design 3-level UI hierarchy. Don't ship God view in v0.4.

## Important (3 voices)

### **T5: Causality not enforced by witness chain** (qwen_thinking, gemma [butterfly effect], deepseek_pro [counterfactual])
"Witnessing state at tick t that isn't deterministic function of t-1 breaks rewind causality."
"Flip a tiny change → entire predicted timeline garbage without warning."
Treatment: Causality invariant check on REWIND — if rewind target breaks micro-reversibility, surface this to user explicitly.
**Promote v0.4.1**: `rewind_to(tick)` returns causal-consistency verdict. If violated, show "rewind will not reproduce witness at t-1" warning.

### **T6: Variable zone tick rates add complexity with no v0.4 win** (groq_qwen, seed_pro, mistral)
"Cross-zone drift/witness clock skew kills 90% of prod bugs in 60 days."
"Hardcode 10Hz uniform for v0.4.0; add variable rates after 14 days stable."
Treatment: Uniform tick rate for v0.4.0.
**Promote v0.4.0**: drop the 100Hz/1Hz split. Single 10Hz zone rate for v0.4.

### **T7: Prometheus/Pushkin: dispatcher = git for cells with temporal branching** (hermes, deepseek_pro)
"This is git for cellular automata with temporal branching."
"It's a time-travel debugger for reality, not a model trainer."
Treatment: Use git vocabulary in docs — fork, commit, branch, merge, checkout. Reproducible commit hashes from witness chain.
**Promote cellforge docs v0.5**: rename dispatcher concepts to match git semantics.

### **T8: JEPA + JEV = prediction marketplace, not prediction engine** (deepseek_pro, hermes [forkable realities], qwen_thinking)
"5 JEPA instances run in parallel, 4 die, 1 promoted to canon."
Treatment: support parallel prediction forks with voting/promotion. JEPA + JEV already do this — document it.
**Already supported**: `compare_scenarios()` in EXPERIMENTAL mode.

### **T9: Promotion = truth-claim problem** (gemma, qwen_thinking, deepseek_pro [consensus])
"User sees prediction succeed, JEV rejects it = 'system lied to me'."
Treatment: pedagogical layer explaining WHY JEV rejected; predicted-success ≠ witnessed-success.
**Promote v0.4.1**: rejection messages include failed-criteria + alternative (try predicting longer horizon / different scenario).

### **T10: Redundant cell kinds** (mistral, hermes [TIMELINE implicit])
"TIMELINE_CELL + EXPERIMENT_LEDGER overlap."
Treatment: Don't add new cell kinds in v0.4.0.
**Already promoted** (seed_pro R4): keep adding cell kinds slow.

## Single-voice (still significant — file for v0.5+)

- **groq_qwen T11**: "SnapshotStore decouples logical from computational — file for v0.5"
- **mistral T12**: "Drop chronoscopic UX to past+present+future-toggle, simpler"
- **deepseek_pro T13**: "Cellforge is for *performative* intelligence, not batch"
- **seed_pro T14**: "Cut experimental ledgers in UI — ship core 6 modes only"

## JEV verdict (v0.4.0)

- canon_score: 0.86/3 (Brilliant paradigm 0.63 probability)
- novelty: 0.76/3 (Notable shift 0.59 probability)
- is_inversion: 0.69 (vs 0.71 in v0.1.2)
- Confidence: ~0.58

**Cross-round trend**:
- v0.1.0: canon_score ~0.55
- v0.1.2: canon_score ~0.61
- v0.3.0: canon_score ~0.78
- v0.4.0: canon_score **0.86** (cumulative rising)

JEV shows v0.4.0 is canon-worthy. The inversion number holding around 0.7 is interesting — suggests the inversion is real but proportional (not "complete" inversion).

## Decisions to ship in v0.4.1

[T1] Distinguish logical_tick vs execution_tick (zone rate)
[T2] Replace 7 modes with 3 orthogonal flags (is_playing, is_experimental, playhead_position)
[T4] 3-level UI hierarchy (Beginner/Power/God)
[T5] Causal-consistency verdict on rewind
[T6] Drop variable zone rates; uniform 10Hz

## Decisions to defer

[T3] TTL default → after 3 weeks observation in v0.5
[T7] git vocabulary → docs only, v0.5
[T9] Pedagogical rejection messages → after core stabilized
[T10] Cell kind reduction → after more users
[T11] SnapshotStore → v0.5
[T12] Reduce UX to 2 dims → after UX testing
[T13] "Performative intelligence" positioning → doc, v0.5
[T14] Cut experimental UI → only if v0.4.1 metrics say so
