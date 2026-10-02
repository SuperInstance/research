"""LANE D+E — the two JEV question types never used.

noul  (used 25+ times): calibrated yes/no
choice (0 times):       pick one of N criteria, returns probabilities per choice
score  (0 times):       rate against an ordered rubric, returns per-level probabilities

Two novel uses:
  CHOICE  — triage competing FRAMINGS of the same finding. Same evidence, different
            explanation. The probability distribution says which framing the model
            actually finds most probable, not just which one I asserted.
  SCORE   — a portfolio-health rubric over the active repos. Returns a per-level
            probability distribution, so a score of 1.4 is legible as "mostly
            level 1, partly level 2" rather than a bare number.
"""
import urllib.request, json, os
from concurrent.futures import ThreadPoolExecutor, as_completed

def jev(state, questions, model='jev-latest'):
    req = urllib.request.Request('https://api.typesafe.ai/v1/systemone',
        data=json.dumps({'model': model, 'state': state, 'questions': questions}).encode(),
        headers={'Authorization': f'Bearer {os.environ["TYPESAFEAI_KEY"]}',
                 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())

# ── LANE D: CHOICE — which framing of the falsifiability finding is most probable? ──
FRAMING_STATE = """Ten research pre-registrations were sealed with sha256 hashes, then stripped
to their prediction text alone and given to an independent verifier with no repository
access. Results: 0 of 10 could be determined PASS/FAIL from the text alone; 0 of 10
could be decided by a stranger; 10 of 10 could be satisfied by bookkeeping without the
substance. All 10 stated an explicit failure condition, and all 10 hashes verified.
Two of the ten passed a stricter four-check gate. The authors are the same group that
wrote them, operating in good faith, and the loop is working (one honest FAIL of record
at -0.0825)."""

FRAMING_Q = {'dominant_explanation': {
    'type': 'choice',
    'instructions': 'Which explanation best accounts for this result?',
    'criteria': {
        'falsifiers_without_substance': 'The registrations specify failure conditions but their PASS conditions are satisfiable by bookkeeping, so they are receipts rather than tests.',
        'unanchored_to_outsiders': 'The predictions are sound but reference only internal artifacts, so no outsider can adjudicate them regardless of their quality.',
        'predictions_are_dishonest': 'The authors registered claims they did not believe, and the audit exposed bad faith.',
        'insufficient_scale': 'Ten predictions is too few to conclude anything, and the result is sampling noise.'
    }}}

# ── LANE E: SCORE — portfolio health rubric over the active repos ──
REPOS = [
 ('quilt-c', 'C99 reference port of the 5-opcode cell model. 1,285 automated assertions, one-command verify entry point, sha256 receipt, CI green on a fresh runner, Apache-2.0 detected. Referenced by no other repo.'),
 ('quilt', 'Spreadsheet product. Cells are live addressable capabilities on a 4D cell graph. Monorepo with 5 workspace packages, CI, Apache-2.0 (just fixed). 34 dependabot PRs, several majors still open.'),
 ('fleet-seeds', 'The keeper. 465 files, receipted playtest loop at Round 58+, lode discovery loop with sha256-sealed predictions and Elo triage. No license. No tests. Not runnable as an artifact.'),
 ('MicroMoth-quilt', 'Experiment tracker. 104 receipt files, 21 test files, CI, Apache-2.0, 10MB. Strong receipt discipline, but receipts are internal and there is no entry point a stranger can run.'),
 ('quilt-gpu-lab', 'GPU research lab running a self-improvement arc with watt-receipts. 237 files, 132MB, NO CI, NO license, 2 test files. Highest ambition, weakest external surface.'),
 ('mavis-pincher', 'Knowledge surface serving 6 endpoints over a 49-repo static dataset. 7 files, no CI, no license, no tests. Small but genuinely composable by an outside agent.'),
 ('AI-Writings', 'Essay corpus. 3.6GB, 60 receipts, 31 test files, CI, GPL-3.0. Large public surface with real licensing, but the artifacts are prose, not composable capabilities.'),
 ('quilt-jepa', 'Continual-learning research. 25 receipts, 0 test files, NO CI, NO license, 277KB. Peer-reviewed shape (dose-response brackets) with no runnable artifact.'),
]
QUESTIONS = {}
for name, desc in REPOS:
    QUESTIONS[name] = {'type': 'score', 'instructions': 'How usable is this to a stranger who has no context?',
        'criteria': [
            '0 — invisible: no README, or the README does not explain what it is.',
            '1 — described: a README explains it, but there is nothing to run.',
            '2 — runnable: a stranger can execute something in under 10 minutes.',
            '3 — verifiable: runnable, with a machine-checkable receipt or test suite a stranger can independently confirm.',
            '4 — composable: an outside agent can depend on it through a stable interface and get a receipt back.',
        ]}

out = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    f1 = ex.submit(jev, FRAMING_STATE, FRAMING_Q)
    f2 = ex.submit(jev, '; '.join(f'{n}: {d}' for n, d in REPOS), QUESTIONS)
    out['choice'] = f1.result()
    out['score'] = f2.result()

json.dump(out, open('jev_untouched.json', 'w'), indent=2)

print('='*80)
print('LANE D — CHOICE: which framing best explains the 0/10 externalisability result?')
print('='*80)
a = out['choice']['answers']['dominant_explanation']
print(f"  selected: {a['choice']}   confidence: {a['confidence']}")
print('  probability distribution:')
for k, v in sorted(a['probabilities'].items(), key=lambda x: -x[1]):
    bar = '█' * int(v*34)
    print(f'    {v:.3f}  {k:34} {bar}')

print()
print('='*80)
print('LANE E — SCORE: stranger-usability rubric over the active fleet')
print('='*80)
print('  0 invisible | 1 described | 2 runnable | 3 verifiable | 4 composable')
print()
rows = []
for name, desc in REPOS:
    ans = out['score']['answers'].get(name)
    if not ans: continue
    rows.append((ans['score'], ans['confidence'], name, ans.get('probabilities', {})))
for sc, conf, name, probs in sorted(rows):
    pstr = ' '.join(f'{int(k)}:{v:.2f}' for k, v in sorted(probs.items()) if v > 0.02)
    print(f'  {sc:>4.1f}  conf={conf:<5}  {name:22}  [{pstr}]')
print()
vals = [r[0] for r in rows]
print(f'  mean: {sum(vals)/len(vals):.2f}   min: {min(vals):.1f}   max: {max(vals):.1f}')
print(f'  repos scoring >=2 (runnable by a stranger): {sum(1 for v in vals if v>=2)}/{len(vals)}')
print(f'  repos scoring >=3 (verifiable):             {sum(1 for v in vals if v>=3)}/{len(vals)}')
print(f'  repos scoring >=4 (composable):             {sum(1 for v in vals if v>=4)}/{len(vals)}')
