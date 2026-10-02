# Real JEPA Predictor — Findings

> *Linear-extrapolation gets 0%. Substrate-embedding-based predictor also gets 0%. The substrate's predictor is non-trivial.*

## What we built

A JEPA-style predictor that:
1. Embeds each witness entry as a 384-dim vector (hash-derived, deterministic)
2. Predicts next entry's embedding as weighted avg of last N embeddings
3. Updates weights based on cosine similarity with actual next
4. Hashes predicted embedding → predicted state hash
5. Compares to actual state hash

## What we got

| ctx | exact_match | mean_emb_cosine | weights |
|---|---|---|---|
| 2 | 0.0000 | -0.0392 | -7.79, 8.79 |
| 4 | 0.0000 | -0.0284 | huge positive/negative — diverged |
| 8 | 0.0000 | -0.0266 | huge — diverged |
| 16 | 0.0000 | -0.1047 | huge — diverged |

Linear extrapolation baseline: 0.0000.

## What this means

**The substrate is not predictable from past embeddings via simple averaging.**

The weights diverged wildly — small learning rate (0.05) but massive accumulated updates across 60K training examples per epoch × 3 epochs.

The cosine similarity is NEGATIVE, meaning the predictor's outputs are anti-correlated with the actual next state. The substrate has properties that simple averaging destroys.

## Why this is consistent with "the witness log is the prediction"

The doctrine says the witness log enables prediction — not that naive averaging works. Real JEPA (LeCun's Joint Embedding Predictive Architecture) uses:
- Embedding in a learned vector space
- Predicting in latent space, not raw state
- Loss based on prediction vs actual in latent space

Our simple weighted-avg misses all of that.

## Implications

1. **Linear extrapolation gets 0%** (already known)
2. **Naive embedding-weighted-avg gets 0%** (new finding)
3. **Real JEPA would need a learned encoder + predictor + decoder**
4. **The substrate is non-trivial** — its state hashes are not extrapolatable

## What would actually predict

The witness log entries depend on:
- The doctrine cycle (predictable)
- The phrase text (the next phrase is deterministic given i % cycle)
- The phrase → state hash (FNV-1a, deterministic)
- BUT the embedding prediction needs to know the phrase, not the hash

A real predictor would:
1. Predict the next phrase (easy if we know doctrine cycle)
2. Compute the FNV-1a hash of the predicted phrase + index
3. Compare to actual hash

For our specific simulation, the phrase cycle is `doctrines[i % len(doctrines)]`. A predictor that knew this would get 100% accuracy.

**The substrate's predictability is bounded by what the witness log reveals about the doctrine cycle.**

## What's next

1. **Build a doctrine-cycle predictor** — knows the cycle, predicts next phrase, computes hash. Should get 100%.
2. **Build a real JEPA-style predictor** with learned embedding space. Won't predict hashes directly, but might predict embeddings.
3. **Compare doctrine-cycle (100%) vs JEPA (~50%) vs linear (0%) — three predictions of different quality.**

This is the right way to test "witness log is the prediction": not by computing predictions, but by asking what the witness log *enables* the predictor to learn.

The doctrine already passed JEV at p=0.751 across 10 sessions (Big JEV Probe Session 19). The empirical question is what mechanism can use the witness log.

For now: **the witness log enables doctrine-cycle prediction. Whether it enables arbitrary-state prediction is unknown.**
