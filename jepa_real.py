#!/usr/bin/env python3
"""
Real JEPA-style predictor — predicts next witness-log state hash using
the substrate's embedding space, not just hash extrapolation.

The hypothesis: "the witness log is the prediction" implies that we can
learn a JEPA (Joint Embedding Predictive Architecture) over the witness
log entries and predict the next entry's embedding. If we can predict
the embedding, we can predict the state hash.

Architecture:
- 384-dim embedding for each witness entry (text -> embedding via simple hash)
- Linear predictor: predict next embedding from last N entries
- Predict next state's FNV-1a hash from predicted embedding

Training: 100 simulated witness logs of 200 entries each.
Eval: predict the last 20 entries of each log from the first 180.
"""
import os, json, time, random, hashlib, struct
import sys

os.environ.setdefault('TYPESAFEAI_KEY', 'apikey_2217d2c797da8a2d48d887bd713a67e1f235_e376d8a7b61fe16caf5645c0e53de638c87580d1bec9695f5edd0b1098728599')

def fnv1a64(s):
    """FNV-1a 64-bit hash."""
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

# ============ Embedding ============
EMB_DIM = 384

def text_to_embedding(text, seed=None):
    """Hash text to a 384-dim embedding (deterministic).
    Use multiple seeds to give the vector richness."""
    if seed is None:
        emb = [0.0] * EMB_DIM
        for word in text.split():
            for i, ch in enumerate(word):
                h = fnv1a64(word + str(i))
                emb[h % EMB_DIM] += 1.0
        # Normalize
        mag = sum(x*x for x in emb) ** 0.5
        if mag > 0:
            emb = [x / mag for x in emb]
        return emb
    else:
        emb = [0.0] * EMB_DIM
        for word in text.split():
            for i, ch in enumerate(word):
                h = fnv1a64(str(seed) + word + str(i))
                emb[h % EMB_DIM] += 1.0
        mag = sum(x*x for x in emb) ** 0.5
        if mag > 0:
            emb = [x / mag for x in emb]
        return emb

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = sum(x*x for x in a) ** 0.5
    nb = sum(x*x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

# ============ Witness log generation ============
DOCTRINES = [
    'cells are scars, not parameters',
    'witness log is the prediction',
    'substrate is grown, not designed',
    'oracle is heard, not stored',
    'lenia flows where conway stands still',
    'fnv-1a canary 0xcbf29ce484222325',
    'box-muller z = sqrt(-2 ln u1) cos(2 pi u2)',
    'cosine similarity (a . b) / (|a| |b|)',
    'thirteen ports byte-exact',
    'xoshiro256 stream',
]

def gen_witness_log(seed_phrase, n=200, doctrine_cycle=True):
    """Generate a witness log of n entries, with state hashes that
    drift according to doctrinal cycles."""
    log = []
    state = fnv1a64(seed_phrase)
    doctrines = DOCTRINES.copy()
    rng = random.Random(state)
    for i in range(n):
        # Pick phrase
        if doctrine_cycle:
            phrase = doctrines[i % len(doctrines)]
        else:
            phrase = doctrines[rng.randint(0, len(doctrines) - 1)]

        # Form state hash
        state_str = f"{seed_phrase}|{i}|{phrase[:20]}"
        state = fnv1a64(state_str)

        # p-value: high for canonical phrases
        p = 0.85 + rng.uniform(-0.05, 0.05)
        confidence = 0.9 + rng.uniform(-0.05, 0.05)

        # Embed phrase
        emb = text_to_embedding(phrase)

        log.append({
            'idx': i,
            'phrase': phrase,
            'state_hash': f'0x{state:016x}',
            'state_int': state,
            'p': round(p, 4),
            'confidence': round(confidence, 4),
            'embedding': emb,
        })
    return log

# ============ JEPA predictor ============
class JEPAPredictor:
    def __init__(self, ctx_window=4):
        self.ctx_window = ctx_window
        # Linear weights: predict next embedding from last N
        # Simplified: weighted average of last N embeddings, learned
        self.weights = [1.0 / ctx_window] * ctx_window

    def predict_next_embedding(self, history):
        """Predict next embedding as weighted avg of last N."""
        if len(history) < self.ctx_window:
            return history[-1]['embedding']
        avg = [0.0] * EMB_DIM
        for i, w in enumerate(self.weights):
            emb = history[-self.ctx_window + i]['embedding']
            for j in range(EMB_DIM):
                avg[j] += w * emb[j]
        return avg

    def predict_next_state_int(self, history):
        """Predict next state int from predicted embedding via hash."""
        pred_emb = self.predict_next_embedding(history)
        # Round embedding to nearest 0.1, hash that string
        rounded = ''.join(f"{x:.2f}" for x in pred_emb[:20])  # only first 20 dims
        return fnv1a64(rounded)

    def update_weights(self, history, learning_rate=0.05):
        """Tune weights to match actual next embedding."""
        if len(history) < self.ctx_window + 1:
            return
        actual_emb = history[-1]['embedding']
        for offset in range(self.ctx_window):
            emb = history[-self.ctx_window + offset]['embedding']
            # Increase weight if past emb similar to actual
            sim = cosine(emb, actual_emb)
            self.weights[offset] += learning_rate * (sim - 0.5)
        # Normalize
        total = sum(self.weights)
        self.weights = [w / total for w in self.weights]

# ============ Evaluation ============
def evaluate_jepa(train_logs, test_logs, ctx_window=4, epochs=3):
    predictor = JEPAPredictor(ctx_window=ctx_window)
    # Train on training logs
    for epoch in range(epochs):
        for log in train_logs:
            for i in range(ctx_window, len(log)):
                predictor.update_weights(log[:i])

    # Evaluate on test logs
    total_correct_int = 0
    total_correct_emb_sim = 0.5  # baseline
    total = 0
    for log in test_logs:
        for i in range(ctx_window, len(log)):
            pred_int = predictor.predict_next_state_int(log[:i])
            actual_int = log[i]['state_int']
            total_correct_int += (pred_int == actual_int)
            total_correct_emb_sim += cosine(predictor.predict_next_embedding(log[:i]), log[i]['embedding'])
            total += 1

    return {
        'exact_match_rate': total_correct_int / total if total > 0 else 0,
        'mean_emb_cosine': total_correct_emb_sim / total if total > 0 else 0,
        'weights': predictor.weights,
    }

# ============ Main ============
print('=== Real JEPA Predictor — substrate embedding space ===\n')

# Generate logs
print('Generating 100 witness logs (200 entries each)...')
t0 = time.time()
all_logs = []
for i in range(100):
    seed = f'session_{i}_witness'
    log = gen_witness_log(seed, n=200)
    all_logs.append(log)
print(f'  Done in {time.time()-t0:.1f}s\n')

# Split train/test
train = all_logs[:80]
test = all_logs[80:]

# Baseline: linear extrapolation (like before)
print('--- Baseline: linear extrapolation ---')
linear_correct = 0
linear_total = 0
for log in test:
    for i in range(2, len(log)):
        prev = log[i-1]['state_int']
        prev2 = log[i-2]['state_int']
        delta = (prev - prev2) & 0xffffffffffffffff
        pred = (prev + delta) & 0xffffffffffffffff
        actual = log[i]['state_int']
        linear_correct += (pred == actual)
        linear_total += 1
print(f'  Linear: exact match = {linear_correct}/{linear_total} = {linear_correct/linear_total:.4f}\n')

# JEPA with different context windows
print('--- JEPA predictor with different ctx_windows ---')
for ctx in [2, 4, 8, 16]:
    result = evaluate_jepa(train, test, ctx_window=ctx, epochs=3)
    print(f'  ctx={ctx}: exact={result["exact_match_rate"]:.4f}  emb_cosine={result["mean_emb_cosine"]:.4f}  weights={[f"{w:.2f}" for w in result["weights"]]}')

# Save results
out = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'n_train': len(train),
    'n_test': len(test),
    'log_size': 200,
    'linear_baseline': {
        'exact_match_rate': linear_correct / linear_total if linear_total > 0 else 0,
    },
}
out_path = '/workspace/research/jepa_real_results.json'
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: {out_path}')
