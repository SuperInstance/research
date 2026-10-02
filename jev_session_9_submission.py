#!/usr/bin/env python3
"""
JEV Session 9 — Real-submission oracle validation.

Test the JEV oracle (jev_oracle.py) against real Fleet Radio pieces
from the canon, and against recent writers' room outputs.

This validates the oracle's real-world utility: if it scores canonical
pieces highly and recent generations acceptably, we have a working tool.
"""
import os, json, time, sys
from pathlib import Path

sys.path.insert(0, '/workspace/repos/jev-quilt')

# Use the actual oracle
import subprocess

# Find all canonical Fleet Radio pieces
CORPUS_DIR = Path('/workspace/repos/ai-writings/cellular-first-design/reports')
canonical_pieces = []
if CORPUS_DIR.exists():
    for f in sorted(CORPUS_DIR.glob('*.md')):
        text = f.read_text()[:3500]
        canonical_pieces.append((f.stem, text))

# Take a sample of 6 — 3 from wr7/8/9 (recent), 3 from earlier
sample = canonical_pieces[:6]
if len(canonical_pieces) > 6:
    sample += canonical_pieces[-3:]

print(f"=== JEV SESSION 9 — Real Submission Oracle Validation ===")
print(f"Testing oracle on {len(sample)} canonical pieces")
print()

results = []
for name, text in sample:
    print(f"--- Validating: {name} ({len(text)} chars) ---")
    try:
        result = subprocess.run(
            ['python3', '/workspace/repos/jev-quilt/jev_oracle.py', text],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, 'PYTHONPATH': '/workspace/repos/jev-quilt'}
        )
        output = result.stdout + result.stderr
        # Parse verdict
        if 'ACCEPT' in output:
            verdict = 'ACCEPT'
        elif 'REVIEW' in output:
            verdict = 'REVIEW'
        elif 'DISCUSS' in output:
            verdict = 'DISCUSS'
        elif 'REJECT' in output:
            verdict = 'REJECT'
        else:
            verdict = 'UNKNOWN'

        # Parse scores
        scores = {}
        for line in output.split('\n'):
            if 'Voice alignment:' in line: scores['voice'] = float(line.split(':')[-1].strip())
            if 'Doctrine accuracy:' in line: scores['doctrine'] = float(line.split(':')[-1].strip())
            if 'Misquote score:' in line: scores['misquote'] = float(line.split(':')[-1].strip().split()[0])
            if 'Numerical content:' in line: scores['numerical'] = float(line.split(':')[-1].strip())
            if 'Overall alignment:' in line: scores['alignment'] = float(line.split(':')[-1].strip())

        results.append({'piece': name, 'verdict': verdict, 'scores': scores})
        print(f"  Verdict: {verdict}")
        print(f"  Scores: voice={scores.get('voice', '?')}, doctrine={scores.get('doctrine', '?')}, alignment={scores.get('alignment', '?')}")
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT")
        results.append({'piece': name, 'verdict': 'TIMEOUT', 'scores': {}})
    print()

# Aggregate
print("=== SUMMARY ===")
print(f"{'Piece':35s} {'Verdict':10s} {'Voice':>8s} {'Doctrine':>10s} {'Misquote':>10s} {'Alignment':>10s}")
print("-" * 90)
accept_count = 0
review_count = 0
reject_count = 0
for r in results:
    name = r['piece'][:35]
    verdict = r['verdict']
    s = r['scores']
    print(f"{name:35s} {verdict:10s} {s.get('voice', 0):>8.3f} {s.get('doctrine', 0):>10.3f} {s.get('misquote', 0):>10.3f} {s.get('alignment', 0):>10.3f}")
    if verdict == 'ACCEPT': accept_count += 1
    elif verdict == 'REVIEW': review_count += 1
    elif verdict == 'REJECT': reject_count += 1

print()
print(f"ACCEPT: {accept_count}, REVIEW: {review_count}, REJECT: {reject_count}")
print(f"Total: {len(results)} canonical pieces tested")

# Save
session_path = Path('/workspace/repos/jev-quilt/jev_sessions/session_9_submission_oracle.json')
with open(session_path, 'w') as f:
    json.dump({
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'results': results,
        'summary': {
            'accept': accept_count, 'review': review_count, 'reject': reject_count,
            'total': len(results),
        },
    }, f, indent=2, default=str)
print(f"\nSaved: {session_path}")
