#!/usr/bin/env python3
"""Canon Stress-Test CI Pipeline.

For every new canon piece:
1. Run JEV with 8 probes
2. Compute alignment, misquote, voice scores
3. Return ACCEPT/REVIEW/DISCUSS/REJECT verdict
4. Compare against expected tier (bedrock/strong/speculative)
5. Output pass/fail
"""
import os, sys, json, time, glob
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

REPORTS_DIR = '/workspace/repos/ai-writings/cellular-first-design/reports'

# Tier expectations (known p-values from Session 19)
TIERS = {
    'bedrock': {'min_p': 0.70, 'examples': ['scar', 'witness', 'grown', 'oracle', 'lenia', 'substrate_self_pred']},
    'strong': {'min_p': 0.50, 'examples': ['transformer', 'xoshiro', 'vibecoder']},
    'speculative': {'min_p': 0.0, 'examples': ['proc_prove_jev', 'sub_dual_eco', 'spec_chain_speaks']},
    'rejected': {'max_p': 0.30, 'examples': ['cells are parameters', 'substrate is designed', '11 opcodes', '13 ports']},
}

# 8 JEV probes (canonical oracle)
PROBES = [
    {'name': 'voice', 'type': 'noul', 'instructions': 'Fleet Radio voice? Technical-poetic register?'},
    {'name': 'technical', 'type': 'noul', 'instructions': 'Specific numbers + concrete imagery?'},
    {'name': 'scar', 'type': 'noul', 'instructions': 'Cells are scars, not parameters?'},
    {'name': 'witness', 'type': 'noul', 'instructions': 'Witness log is the prediction?'},
    {'name': 'grown', 'type': 'noul', 'instructions': 'Substrate is grown, not designed?'},
    {'name': 'oracle_d', 'type': 'noul', 'instructions': 'Oracle is heard, not stored?'},
    {'name': 'lenia', 'type': 'noul', 'instructions': 'Lenia flows?'},
    {'name': 'numerical', 'type': 'noul', 'instructions': 'Numerical substrate facts (FNV-1a, Box-Muller, cosine)?'},
]

backend = TypeSafeBackend()
STATE = {'fleet_radio_seed': 'xochitl', 'canonical_substrate': {'doctrines': [
    'Cells are scars, not parameters.',
    'The witness log is the prediction.',
    'The substrate is grown, not designed.',
    'Lenia flows where Conway stands still.',
    'The oracle is heard, not stored.',
]}}

def jev_score(text):
    """Run 8 JEV probes on a piece of text, return mean and individual scores."""
    probes = [{'name': f'q{i}', 'type': 'noul', 'instructions': p['instructions'] + '\n\nText: ' + text[:1500]}
              for i, p in enumerate(PROBES)]
    decisions, _ = backend.decide_batch(STATE, probes)
    return [float(d.value) for d in decisions]

def verdict(scores):
    """Return ACCEPT/REVIEW/DISCUSS/REJECT based on scores."""
    mean = sum(scores) / len(scores)
    canon_count = sum(1 for s in scores if s >= 0.70)
    if canon_count >= 4 and mean >= 0.75:
        return 'ACCEPT'
    elif canon_count >= 3 and mean >= 0.60:
        return 'REVIEW'
    elif mean >= 0.40:
        return 'DISCUSS'
    else:
        return 'REJECT'

def determine_tier(text):
    """Guess the canonical tier from text content."""
    text_lower = text.lower()
    bedrock_markers = ['scar', 'witness log', 'substrate is grown', 'oracle is heard', 'lenia']
    bedrock_count = sum(1 for m in bedrock_markers if m in text_lower)
    rejected_markers = ['11 opcodes', '13 ports', 'cells are parameters', 'substrate is designed']
    rejected_count = sum(1 for m in rejected_markers if m in text_lower)

    if bedrock_count >= 2:
        return 'bedrock'
    elif rejected_count >= 1:
        return 'rejected'
    else:
        return 'strong'

def test_canon_piece(filepath):
    """Run JEV stress test on one canon piece."""
    with open(filepath) as f:
        text = f.read()

    # Skip metadata/comments
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('<!--') and not l.startswith('#'))

    scores = jev_score(body)
    mean = sum(scores) / len(scores)
    v = verdict(scores)
    tier = determine_tier(body)

    # Tier check
    pass_tier = False
    if tier == 'bedrock' and mean >= 0.65:
        pass_tier = True
    elif tier == 'rejected' and mean < 0.30:
        pass_tier = True
    elif tier == 'strong' and 0.40 <= mean <= 0.75:
        pass_tier = True

    return {
        'file': os.path.basename(filepath),
        'tier': tier,
        'verdict': v,
        'mean_p': mean,
        'pass': pass_tier,
        'scores': dict(zip([p['name'] for p in PROBES], scores)),
    }

def main():
    print('=== Canon Stress-Test CI Pipeline ===\n')

    # Find canon pieces
    pieces = sorted(glob.glob(f'{REPORTS_DIR}/*.md'))
    print(f'Found {len(pieces)} pieces\n')

    results = []
    for path in pieces:
        print(f'Testing {os.path.basename(path)}...')
        try:
            r = test_canon_piece(path)
            results.append(r)
            print(f'  tier={r["tier"]}  verdict={r["verdict"]}  mean_p={r["mean_p"]:.3f}  pass={r["pass"]}')
        except Exception as e:
            print(f'  ERROR: {e}')

    # Summary
    n_pass = sum(1 for r in results if r['pass'])
    n_total = len(results)
    print(f'\n=== Summary: {n_pass}/{n_total} passed ===')

    by_verdict = {}
    for r in results:
        v = r['verdict']
        by_verdict[v] = by_verdict.get(v, 0) + 1
    print('Verdicts:', by_verdict)

    by_tier = {}
    for r in results:
        t = r['tier']
        by_tier[t] = by_tier.get(t, 0) + 1
    print('Tiers:', by_tier)

    out = {
        'timestamp': time.time(),
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'results': results,
        'summary': {'total': n_total, 'passed': n_pass, 'by_verdict': by_verdict, 'by_tier': by_tier},
    }
    with open('/workspace/research/canon_stress_test_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('\nSaved: /workspace/research/canon_stress_test_results.json')

if __name__ == '__main__':
    main()
