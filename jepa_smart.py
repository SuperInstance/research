#!/usr/bin/env python3
"""
Smart JEPA — predict next witness entry via similarity-weighted
nearest neighbor in the embedding space.

Algorithm:
1. Embed each witness entry
2. To predict next: find K nearest neighbors in training set
3. Average their successors
4. Compare to actual next

This is what FAISS / Annoy do at industrial scale. We'll do a simple
python version. Much faster than gradient-based.
"""
import os, json, time, random

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
        phrase = DOCTRINES[i % len(DOCTRINES)] if doctrine_cycle else DOCTRINES[rng.randint(0, len(DOCTRINES) - 1)]
        state = fnv1a64(f"{seed}|{i}|{phrase[:20]}")
        emb = text_to_embedding(phrase)
        log.append({'idx': i, 'phrase': phrase, 'state_int': state, 'embedding': emb})
    return log

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = sum(x*x for x in a) ** 0.5
    nb = sum(x*x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

class SmartJEPAPredictor:
    """Predict next embedding via similarity-weighted average of
    observed successors in training set."""
    def __init__(self, ctx_window=4, k_neighbors=5):
        self.ctx_window = ctx_window
        self.k_neighbors = k_neighbors
        # Map from (ctx_tuple) -> list of successor embeddings
        self.successor_table = {}

    def train(self, logs):
        """Build the (ctx -> successors) lookup from training logs."""
        for log in logs:
            embs = [entry['embedding'] for entry in log]
            for i in range(self.ctx_window, len(embs)):
                ctx = tuple(tuple(emb) for emb in embs[i-self.ctx_window:i])
                successor = embs[i]
                if ctx not in self.successor_table:
                    self.successor_table[ctx] = []
                self.successor_table[ctx].append(successor)

    def find_approx_match(self, ctx_embs):
        """Find best matching ctx in training table by average cosine similarity."""
        best_sim = -1
        best_match = None
        for stored_ctx, successors in self.successor_table.items():
            sims = [cosine(c, ctx_embs[i]) for i, c in enumerate(stored_ctx)]
            mean_sim = sum(sims) / len(sims)
            if mean_sim > best_sim:
                best_sim = mean_sim
                best_match = successors
        return best_match, best_sim

    def predict_next(self, ctx_embs):
        """Predict next embedding as the average of the K best matches' successors."""
        # Find best matching context
        successors, sim = self.find_approx_match(ctx_embs)
        if not successors:
            return ctx_embs[-1], 0.0
        # Use top-K successors
        avg = [0.0] * EMB_DIM
        for s in successors[:self.k_neighbors]:
            for j in range(EMB_DIM):
                avg[j] += s[j]
        avg = [x / min(len(successors), self.k_neighbors) for x in avg]
        return avg, sim

def evaluate(predictor, test_logs, ctx_window):
    total_emb_cosine = 0
    total_ctx_sim = 0
    total_exact = 0
    n = 0
    for log in test_logs:
        embs = [entry['embedding'] for entry in log]
        state_ints = [entry['state_int'] for entry in log]
        for i in range(ctx_window, len(embs)):
            ctx = embs[i-ctx_window:i]
            pred, ctx_sim = predictor.predict_next(ctx)
            actual = embs[i]
            sim = cosine(pred, actual)
            total_emb_cosine += sim
            total_ctx_sim += ctx_sim
            pred_str = ''.join(f"{x:.2f}" for x in pred[:10])
            pred_hash = fnv1a64(pred_str)
            if pred_hash == state_ints[i]:
                total_exact += 1
            n += 1
    return {
        'mean_emb_cosine': total_emb_cosine / n if n > 0 else 0,
        'mean_ctx_sim': total_ctx_sim / n if n > 0 else 0,
        'exact_match_rate': total_exact / n if n > 0 else 0,
    }

print('=== Smart JEPA — similarity-based predictor ===\n')

print('Generating 100 logs (200 entries each)...')
t0 = time.time()
all_logs = []
for i in range(100):
    seed = f'session_{i}_witness'
    all_logs.append(gen_log(seed, n=200))
print(f'  Done in {time.time()-t0:.1f}s\n')

train = all_logs[:80]
test = all_logs[20:]  # 20 held out

# Train and evaluate
for ctx_window in [2, 4]:
    for k in [1, 5]:
        t0 = time.time()
        predictor = SmartJEPAPredictor(ctx_window=ctx_window, k_neighbors=k)
        predictor.train(train)
        eval_res = evaluate(predictor, test, ctx_window)
        print(f'ctx={ctx_window} k={k}: emb_cosine={eval_res["mean_emb_cosine"]:.4f}  ctx_sim={eval_res["mean_ctx_sim"]:.4f}  exact={eval_res["exact_match_rate"]:.4f}  ({time.time()-t0:.1f}s)')

# Linear baseline
print()
print('--- Baseline: linear extrapolation ---')
linear_correct = 0
linear_total = 0
for log in test:
    embs = [entry['embedding'] for entry in log]
    state_ints = [entry['state_int'] for entry in log]
    for i in range(2, len(state_ints)):
        prev = state_ints[i-1]
        prev2 = state_ints[i-2]
        delta = (prev - prev2) & 0xffffffffffffffff
        pred = (prev + delta) & 0xffffffffffffffff
        if pred == state_ints[i]:
            linear_correct += 1
        linear_total += 1
print(f'  Linear: {linear_correct}/{linear_total} = {linear_correct/linear_total:.4f}')
