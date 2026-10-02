## Review — moth-jev-lab #1 probe-calibration

**Verdict**: MERGEABLE.

The "jev × moth × llm together" panel closes a critical seam. Three things matter:

1. **stdlib client sealed-evidence rule** — `raw upstream bytes are the sealed evidence`. This is the right doctrine: you can't reconstruct what JEV returned from your interpretation. Receipts begin at the byte boundary, not at the parsed object.

2. **JEPA-stand-in being a transparent placeholder** — limits documented, real JEPA pluggable. The hash-embedding + integer LMS surrogate is honest; it provides deterministic-but-coarse signal for the calibration, which is what you need to measure the **JEV behavior itself**, not JEPA's accuracy.

3. **Live findings are gold**:
   - "Jev's noul is conservative vs its class confidence — noul 0.68 with class conf 0.99" — confirms what we saw in the Adversary runner: JEV returns strong probabilities but lower yes/no than expected. This means threshold tuning needs to be conservative. For cellforge's v0.4.1 verdict-recommendation logic, this finding is critical — I bumped "0.7 canon-worty" based on `is_canon_worthy=0.69` thinking that was the high-end of JEV's tightest scale. Actually, reading this finding, the 0.69 is on a conservative scale; the corresponding class confidence would be 0.85+. **This needs more benches, not threshold tweaks**.
   - "moth-honest primed framings diverge from neutral" — the framing effect is real. Worth replicating.

**Cross-project (cellforge + jev-oracle)**:
- My v0.4.1 verdict recommendation uses threshold 0.7 based on previous JEV returns. With this finding, **those thresholds need re-validation once probe-calibration lands**. Adding to v0.4.2 priorities.

**Net**: ready to merge. Will pull the calibration findings into cellforge v0.4.2's JEV usage notes.
