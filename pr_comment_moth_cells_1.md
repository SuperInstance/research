## Review — moth-cells #1 kernel 1 — cellular predation over corpus terrain

**Verdict**: MERGEABLE.

The architecture choices are right and aligned with the family doctrine:

1. **Genome is FNV-1a-64 deterministic** — hunter identity is content-bound, not assigned. Replayable from byte residue.
2. **dice = splitmix64(genome.seed, tick)** — no floats. Integer rollouts make every walk reproducible bit-for-bit. This is the receiptable execution doctrine: stochastic in shape, deterministic in residue.
3. **Q16 energy saturated at 1.0** — bounded. Never blows up. Good for receipted scoring.
4. **Death books a REFUSAL row** — load-bearing. Death isn't a silent exit; it's a receipt with `polarity=negative`. Same principle as cellforge's causal-consistency verdict: failing honestly > silently exiting.
5. **terrain_hash binds content** — terrain is content-addressed. Walk target is reproducible.

**Cross-project sync (cellforge ↔ moth-cells)**:
- cellforge's `WITNESS_CELL` + `FORK_VERSION_VECTOR` is the **ledger** side of this kernel
- moth-cells's `Genome` + walks-on-terrain is the **kernel** side
- Together they make a full predator system: a hunter (moth-cells kernel) walks the lattice (CorpusIndex), each step sealed as a receipt (in cellforge's witness chain), and the cells (cellforge Workbook) hold the (live + replay) state

**Suggestion for next kernel (kernel 2)**:
- The energy `gain on taint-rich, cost per move, saturated at 1.0` is a single objective. Consider multi-objective (gain + restraint + entry-count) so moths can specialize. Each specialty becomes its own Genome.

**Net**: ready. This is the right dependency root for Experiments #2/#4/#5/#9/#10.
