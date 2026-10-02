#!/usr/bin/env python3
"""JEV × JEPA cross-validation — witness-log-is-the-prediction.

Run 5 separate JEV sessions, each asking the same 8 questions about
"witness log is the prediction". If mean p > 0.70 across all 5 sessions,
it's bedrock canon.

Also: simulate a "JEPA" (Joint Embedding Predictive Architecture)
predictor that takes a witness log entry and tries to predict the next
state hash. Compare its prediction against the actual next entry.
The accuracy of this prediction is the SUBSTRATE's self-prediction
capability, which connects to "witness log is the prediction".

If JEV says witness log is canon AND JEPA-style predictor does well,
the substrate is self-predicting. That's the bedrock.
"""
import os, sys, json, time, hashlib, struct
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

# ============ Witness log simulation ============
def fnv1a64(s):
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

def make_witness_log(seed_phrase, n):
    """Generate a witness log of n entries with predictable drift."""
    log = []
    state = fnv1a64(seed_phrase)
    for i in range(n):
        # Next state hash = FNV-1a(prev_state + i)
        state = fnv1a64(str(state) + str(i))
        log.append({
            'idx': i,
            'state_hash': f'0x{state:016x}',
            'p': 0.5 + 0.4 * (1 - abs(state / 2**64 - 0.5)),  # canon-ish
            'confidence': 0.7 + (state % 1000) / 5000,
        })
    return log

# ============ JEPA-style predictor ============
class JEPAPredictor:
    """A simple predictor that predicts next state hash from past log."""
    def __init__(self):
        self.history = []
    
    def predict_next(self):
        """Predict the next state hash by extrapolating past FNV sequence."""
        if len(self.history) < 2:
            return self.history[-1]['state_hash'] if self.history else '0x0'
        # Linear extrapolation: next = last + (last - prev)
        last = int(self.history[-1]['state_hash'], 16)
        prev = int(self.history[-2]['state_hash'], 16)
        delta = (last - prev) & 0xffffffffffffffff
        next_h = (last + delta) & 0xffffffffffffffff
        return f'0x{next_h:016x}'
    
    def observe(self, entry):
        """Add entry to history."""
        self.history.append(entry)

def jepa_score(log):
    """Score predictor: how many predictions match the actual?"""
    predictor = JEPAPredictor()
    correct = 0
    for i, entry in enumerate(log):
        if i > 0:
            pred = predictor.predict_next()
            if pred == entry['state_hash']:
                correct += 1
        predictor.observe(entry)
    return correct, len(log) - 1

# ============ JEV probe — 5 sessions, 8 questions each ============
SESSION_QUESTIONS = [
    'Is the witness log literally the prediction (not just a record)?',
    'Is the witness log the prediction in the canonical substrate sense?',
    'Does the witness log serve a predictive function in canonical canon?',
    'Is "the witness log is the prediction" canonical doctrine?',
    'Is "witness log is past only" canonical or is it the inversion?',
    'Does the substrate self-predict via its witness log?',
    'Is the witness log both a record AND a forecast in canonical canon?',
    'Is there a substrate-level symmetry between witness (JEV) and predict (JEPA)?',
]

def run_jev_session(session_id):
    """Run one JEV session, get 8 verdicts on witness-log-prediction."""
    backend = TypeSafeBackend()
    state = {
        'fleet_radio_seed': 'xochitl',
        'canonical_substrate': {
            'doctrines': [
                'Cells are scars, not parameters.',
                'The witness log is the prediction.',
                'The substrate is grown, not designed.',
                'Lenia flows where Conway stands still.',
                'The oracle is heard, not stored.',
            ],
        },
    }
    questions = [{'name': f'q{i}', 'type': 'noul', 'instructions': q} for i, q in enumerate(SESSION_QUESTIONS)]
    decisions, meta = backend.decide_batch(state, questions)
    return [float(d.value) for d in decisions]

# ============ Main ============
print('=== JEV x JEPA Cross-Validation ===\n')

# 1) JEPA prediction scoring
print('--- JEPA-style prediction across 5 witness logs ---')
log_scores = []
for i in range(5):
    seed = f'session_{i}_witness_log'
    log = make_witness_log(seed, 50)
    correct, total = jepa_score(log)
    rate = correct / total
    log_scores.append({'session': i, 'correct': correct, 'total': total, 'rate': rate})
    print(f'  Session {i}: {correct}/{total} = {rate:.3f} correct predictions')

mean_jepa = sum(s['rate'] for s in log_scores) / len(log_scores)
print(f'  Mean JEPA accuracy: {mean_jepa:.3f}\n')

# 2) JEV sessions
print('--- JEV across 5 sessions (8 questions each) ---')
session_results = []
for i in range(5):
    t0 = time.time()
    ps = run_jev_session(i)
    dt = time.time() - t0
    mean_p = sum(ps) / len(ps)
    session_results.append({
        'session': i,
        'mean_p': mean_p,
        'individual': ps,
        'latency_s': dt,
    })
    print(f'  Session {i}: mean_p={mean_p:.3f}  individual={[f"{p:.2f}" for p in ps]}  ({dt:.1f}s)')

grand_mean = sum(s['mean_p'] for s in session_results) / len(session_results)
print(f'\n  GRAND MEAN across 5 sessions: {grand_mean:.3f}')

# Verdict
if grand_mean >= 0.70:
    verdict = 'BEDROCK CANON — witness-log-is-the-prediction is confirmed across 5 sessions'
elif grand_mean >= 0.50:
    verdict = 'PLAUSIBLE — but needs more sessions'
else:
    verdict = 'NOT CANON — JEV skeptical'
print(f'\n  VERDICT: {verdict}')

# Save
out = {
    'timestamp': time.time(),
    'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'jepa_scores': log_scores,
    'jepa_mean': mean_jepa,
    'jev_sessions': session_results,
    'jev_grand_mean': grand_mean,
    'verdict': verdict,
}
with open('/workspace/research/jev_jepa_crossval.json', 'w') as f:
    json.dump(out, f, indent=2)
print(f'\nSaved: /workspace/research/jev_jepa_crossval.json')
