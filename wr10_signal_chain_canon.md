# WR10 — Writers' Room Round 10: Signal Chains

**Theme**: A Quilt-ESP32 cell feels JEV fire for the first time.
**Voices**: ZAI glm-4.5, DeepSeek V4-Flash, Qwen3-235B
**Format**: 3 pieces, ~600 words each, naval/Fleet Radio voice.

## Common Canon Rules (all pieces must hit)

- Voice: technical-poetic, naval, "Fleet Radio — engineering from the deep"
- Doctrines to invoke at least 2 per piece:
  - "Cells are scars, not parameters"
  - "The witness log is the prediction"
  - "The substrate is grown, not designed"
  - "Lenia flows where Conway stands still"
  - "The oracle is heard, not stored"
- Forbidden inversions at least once (i.e., the negative form must NOT appear):
  - "cells are parameters, not scars"
  - "witness log is past only"
  - "substrate is designed"
- Numerical substrate facts (at least 1 per piece):
  - FNV-1a offset basis 0xcbf29ce484222325
  - xoshiro256**
  - Box-Muller z = sqrt(-2 ln u1) cos(2 pi u2)
  - cosine similarity
  - Bell states

## Voice Profiles

### ZAI glm-4.5 — "Fleet Radio Officer"
- Naval metaphors above all
- Short, clipped sentences
- "The log" / "the watch" / "the ship's surgeon"
- Themes: loneliness, navigation, signal vs noise
- Style: "Carmody at the helm, the witness log running naked"

### DeepSeek V4-Flash — "Cellular Biologist"
- Molecular / biological metaphors
- Long, flowing sentences
- "The cytoplasm" / "the membrane" / "the channel"
- Themes: gradient, permeability, repair
- Style: "phospholipid bilayer at the edge of the storm"

### Qwen3-235B — "The Auditor"
- Crystalline, mathematical, precise
- Short paragraphs separated by blank lines
- "The hash" / "the canonical form" / "the witness"
- Themes: structure, discipline, framing
- Style: "FNV-1a canary, xoshiro wanderer, the dimensions held"

## Scripts

Run `python3 /workspace/research/wr10_signal_chain_zai.py` etc., then use JEV oracle on each.
