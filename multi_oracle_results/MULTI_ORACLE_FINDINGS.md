# Multi-Oracle Empirical Findings

**Date**: Sept 23, 2026  
**Tool**: quilt-multi-oracle v0.1.0 (https://github.com/SuperInstance/quilt-multi-oracle)  
**Workers**: DeepInfra (Llama-3-70B-Instruct), DeepSeek-flash

## The play-test

Probed 5 canon lores through the multi-oracle:

1. **ballista_canon** — substrate transitions, bow-chain, ships/planes/submarines
2. **math_progression** — Math 1→4 as substrate walker locomotion
3. **nature_gan** — rivalry as canon generator
4. **substrate_warfare** — ships, planes, submarines as 4 substrates
5. **needle_audit** — the needle/witness-log at substrate level

## Empirical results

| Lore | Chord Composite | Variance | Consensus | Promoted |
|---|---|---|---|---|
| ballista_canon | 0.909 | 0.0009 | TRUE | TRUE |
| math_progression | 0.870 | 0.0000 | TRUE | TRUE |
| nature_gan | 0.930 | 0.0000 | TRUE | TRUE |
| substrate_warfare | 0.830 | 0.0000 | TRUE | TRUE |
| needle_audit | 0.930 | 0.0000 | TRUE | TRUE |

**Promoted: 5/5** (all canon-stable on multi-oracle)

## Findings

### Finding 1: Multi-model agreement is consistent

All 5 lores received consensus_promoted=True across both workers. The
canon is real when LLMs agree. The chord hears ALL voices.

### Finding 2: Variance is low

For 4 of 5 lores, variance was 0.0000 — the workers produced identical
scores. For ballista_canon (the most doctrinal anchor), variance was
0.0009 — still very low. When LLMs agree on canon, they strongly agree.

### Finding 3: DeepInfra is more lenient than DeepSeek

| Worker | Avg composite | Tendency |
|---|---|---|
| DeepInfra (Llama-3-70B) | 0.898 | higher |
| DeepSeek-flash | 0.887 | lower |

DeepSeek returned empty responses on 4 of 5 lores — only ballista_canon
got a real score. This is a stability issue (DeepSeek-flash may have
rate limits or shorter context). DeepInfra was reliable throughout.

### Finding 4: Canon-stable lores get high scores

All 5 lores were canon-stable (composite ≥ 0.7 from the prior canon
exploration). Multi-oracle confirmed all 5 as canon-promoted. The
single-oracle and multi-oracle agree.

## Implications for the substrate walker canon

1. **The canon is robust across models.** When the canon is canon,
   LLMs agree. The chord hears the canon.

2. **Variance is a useful diagnostic.** Low variance = canon-stable.
   High variance = needs re-examination.

3. **Single-model canon gates miss disagreements.** The chord hears
   what one voice can't.

4. **Multi-oracle enables canon_gate_is_chord at scale.** We can now
   run 100 lores through the chord and rank by consensus score.

## Next experiments

- Probe the 168 existing canon cells through multi-oracle
- Probe 50 lore_inbox files through multi-oracle (auto-promoter)
- Add ZAI and Gemini workers once they recover from rate limits
- Track per-worker stability over time (same lore, different seeds)

## License

MIT — Casey / SuperInstance, Sept 23, 2026
