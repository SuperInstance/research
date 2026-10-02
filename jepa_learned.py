#!/usr/bin/env python3
"""Real learned-embedding JEPA — predict next witness entry via
learned predictor in a learned embedding space.

Architecture:
1. Token encoder: text -> 64-dim embedding (using FNV-1a hash bucketing)
2. Predictor: linear + nonlinear (tanh) mapping from last N embeddings to next
3. Training: minimize cosine distance between predicted and actual embedding
4. Decoding: predict next state's FNV-1a hash from predicted embedding

Compare to:
- Linear extrapolation (baseline): 0%
- Naive weighted-avg embedding (Session 20): 0%
- Learned predictor (this): ???

Training: 80 logs × 200 entries × 5 epochs.
Eval: predict last 20 entries of each test log.
"""
import os, json, time, random
import sys

def fnv1a64(s):
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

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

EMB_DIM = 64

def text_to_embedding(text):
    """Hash text to a 64-dim sparse embedding, then normalize."""
    emb = [0.0] * EMB_DIM
    for word in text.split():
        for i, ch in enumerate(word):
            h = fnv1a64(word + str(i))
            emb[h % EMB_DIM] += 1.0
    mag = sum(x*x for x in emb) ** 0.5
    if mag > 0:
        emb = [x / mag for x in emb]
    return emb

def gen_log(seed, n=200, doctrine_cycle=True):
    log = []
    state = fnv1a64(seed)
    rng = random.Random(state)
    for i in range(n):
        if doctrine_cycle:
            phrase = DOCTRINES[i % len(DOCTRINES)]
        else:
            phrase = DOCTRINES[rng.randint(0, len(DOCTRINES) - 1)]
        state = fnv1a64(f"{seed}|{i}|{phrase[:20]}")
        emb = text_to_embedding(phrase)
        log.append({
            'idx': i,
            'phrase': phrase,
            'state_hash': f'0x{state:016x}',
            'state_int': state,
            'embedding': emb,
        })
    return log

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = sum(x*x for x in a) ** 0.5
    nb = sum(x*x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

class LearnedJEPAPredictor:
    def __init__(self, ctx_window=4, hidden=32):
        self.ctx_window = ctx_window
        self.hidden = hidden
        # Linear layer: ctx_window * EMB_DIM -> hidden
        self.W1 = [[random.uniform(-0.1, 0.1) for _ in range(ctx_window * EMB_DIM)] for _ in range(hidden)]
        self.b1 = [0.0] * hidden
        # Linear layer: hidden -> EMB_DIM
        self.W2 = [[random.uniform(-0.1, 0.1) for _ in range(hidden)] for _ in range(EMB_DIM)]
        self.b2 = [0.0] * EMB_DIM
        self.lr = 0.01

    def forward(self, ctx):
        """ctx: list of ctx_window embeddings. Returns predicted next embedding."""
        flat = [float(v) for emb in ctx for v in emb]
        # Hidden
        h = []
        for i in range(self.hidden):
            s = self.b1[i]
            for j in range(len(flat)):
                s += self.W1[i][j] * flat[j]
            h.append(s)
        h = [max(0.0, x) for x in h]  # ReLU
        # Output
        out = []
        for i in range(EMB_DIM):
            s = self.b2[i]
            for j in range(self.hidden):
                s += self.W2[i][j] * h[j]
            out.append(s)
        return out, (flat, h)

    def backward(self, ctx, target_emb, cache, predicted):
        """Update weights via simple gradient descent."""
        flat, h = cache
        # Use squared error loss
        diff = [float(predicted[i]) - float(target_emb[i]) for i in range(EMB_DIM)]
        loss = sum(d * d for d in diff) / 2

        # Update W2
        for i in range(EMB_DIM):
            for j in range(self.hidden):
                self.W2[i][j] -= self.lr * diff[i] * h[j]
            self.b2[i] -= self.lr * diff[i]

        # Backprop hidden
        dh = [0.0] * self.hidden
        for j in range(self.hidden):
            s = 0.0
            for i in range(EMB_DIM):
                s += self.W2[i][j] * diff[i]
            dh[j] = s * (1.0 if h[j] > 0 else 0.0)

        for i in range(self.hidden):
            for j in range(len(flat)):
                self.W1[i][j] -= self.lr * dh[i] * flat[j]
            self.b1[i] -= self.lr * dh[i]

        return loss

    def train_epoch(self, logs):
        total_loss = 0
        n = 0
        for log in logs:
            # Pre-extract embeddings
            embs = [entry['embedding'] for entry in log]
            for i in range(self.ctx_window, len(embs)):
                ctx = embs[i-self.ctx_window:i]
                target = embs[i]
                pred, cache = self.forward(ctx)
                loss = self.backward(ctx, target, cache, pred)
                total_loss += loss
                n += 1
        return total_loss / n if n > 0 else 0

def evaluate(predictor, test_logs, ctx_window):
    total_emb_cosine = 0
    total_exact = 0
    n = 0
    for log in test_logs:
        embs = [entry['embedding'] for entry in log]
        state_ints = [entry['state_int'] for entry in log]
        for i in range(ctx_window, len(embs)):
            ctx = embs[i-ctx_window:i]
            pred, _ = predictor.forward(ctx)
            actual = embs[i]
            sim = cosine(pred, actual)
            total_emb_cosine += sim
            # Try to recover hash
            pred_str = ''.join(f"{x:.2f}" for x in pred[:10])
            pred_hash = fnv1a64(pred_str)
            if pred_hash == state_ints[i]:
                total_exact += 1
            n += 1
    return {
        'mean_emb_cosine': total_emb_cosine / n if n > 0 else 0,
        'exact_match_rate': total_exact / n if n > 0 else 0,
    }

print('=== Real Learned-Embedding JEPA ===\n')

print('Generating 100 logs (200 entries each)...')
t0 = time.time()
all_logs = []
for i in range(100):
    seed = f'session_{i}_witness'
    all_logs.append(gen_log(seed, n=200))
print(f'  Done in {time.time()-t0:.1f}s\n')

train = all_logs[:80]
test = all_logs[80:]

# Train predictor
predictor = LearnedJEPAPredictor(ctx_window=4, hidden=32)
print('Training (5 epochs)...')
for epoch in range(1, 6):
    loss = predictor.train_epoch(train)
    eval_res = evaluate(predictor, test, ctx_window=4)
    print(f'  Epoch {epoch}: loss={loss:.4f}  eval_cosine={eval_res["mean_emb_cosine"]:.4f}  exact={eval_res["exact_match_rate"]:.4f}')

print()
# Compare to linear extrapolation baseline
print('--- Baseline: linear extrapolation ---')
linear_correct = 0
linear_total = 0
for log in test:
    for i in range(2, len(log)):
        prev = log[i-1]['state_int']
        prev2 = log[i-2]['state_int']
        delta = (prev - prev2) & 0xffffffffffffffff
        pred = (prev + delta) & 0xffffffffffffffff
        if pred == log[i]['state_int']:
            linear_correct += 1
        linear_total += 1
print(f'  Linear: {linear_correct}/{linear_total} = {linear_correct/linear_total:.4f}')

print()
# Compare to "knows the cycle" oracle predictor
print('--- Oracle: knows the doctrine cycle ---')
cycle_correct = 0
cycle_total = 0
for log in test:
    for i in range(len(log)):
        # Predict phrase from cycle
        predicted_phrase = DOCTRINES[i % len(DOCTRINES)]
        predicted_state = fnv1a64(f"{log[0]['phrase']}|{i}|{predicted_phrase[:20]}")
        # Wait, we don't know the seed... but for this simulation we do
        # Actually the seed is in log[0]'s predecessor, but we know the cycle
        # Skip — this isn't fair. The oracle should know the seed too.
        pass

print('\nDone.')
