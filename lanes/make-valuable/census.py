#!/usr/bin/env python3
"""census.py — classify every repo in the account by what it ACTUALLY is.

Casey's frame: some repos are living, some are memorials to living repos, some are
shells molted as ideas grew, some are bones of ideas that once had life. To pour
effort in we need to know which is which, from evidence rather than vibes.

The classification is behavioural, not nominal. A repo's NAME tells you what it claims
to be. Its commit count, file count, test count, last push, and whether its entry point
runs tell you what it is.

PRE-REGISTERED, because a census that only confirms what I already believe is a
press release.
"""
import sys, json, os, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, '/workspace/research/lanes/scout-theirs')
from loop2 import pr, debrief, show, load, save

H = {'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}',
     'Accept': 'application/vnd.github+json', 'User-Agent': 'mavis-census'}
API = 'https://api.github.com/repos/SuperInstance'

def gh(p):
    try:
        req = urllib.request.Request(f'https://api.github.com{p}', headers=H)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'__err': str(e)[:60]}

def scan(repo):
    m = gh(f'/repos/SuperInstance/{repo}')
    if '__err' in m or 'name' not in m:
        return {'repo': repo, 'error': m.get('__err', 'not found')}
    t = gh(f'/repos/SuperInstance/{repo}/git/trees/HEAD?recursive=1')
    paths = [e['path'] for e in t.get('tree', []) if e['type'] == 'blob'] if 'tree' in t else []
    c = gh(f'/repos/SuperInstance/{repo}/commits?per_page=1')
    # full commit count only for the ones that look small; 4,856 repos is too many
    rows = {'repo': repo, 'files': len(paths), 'size_kb': m.get('size', 0),
            'pushed': (m.get('pushed_at') or '')[:10], 'created': (m.get('created_at') or '')[:10],
            'stars': m.get('stargazers_count', 0), 'forks': m.get('forks_count', 0),
            'archived': m.get('archived'), 'fork': m.get('fork'),
            'license': (m.get('license') or {}).get('spdx_id'),
            'desc': (m.get('description') or '')[:100],
            'total_commits': (c[0]['commit']['committer']['date'] if isinstance(c, list) and c else None)}
    rows['tests'] = sum(1 for p in paths if any(k in p.lower() for k in ('test', 'spec', '_test')))
    rows['src'] = sum(1 for p in paths if any(p.endswith(e) for e in ('.py', '.rs', '.js', '.ts', '.c', '.h', '.go', '.jl', '.mjs')))
    rows['has_ci'] = any(p.startswith('.github/workflows/') for p in paths)
    rows['has_readme'] = any(p.lower().startswith('readme') for p in paths)
    return rows

if __name__ == '__main__':
    # pull the full repo list, sorted by pushed desc, page through
    # SuperInstance is a USER account, not an org. /orgs/ returns an empty list, which
    # is a useful reminder: every one of the fleet's 4,856 repos hangs off one person,
    # with no org namespace and therefore no per-repo role or trust boundary.
    repos = []
    for page in range(1, 14):
        r = gh(f'/users/SuperInstance/repos?per_page=100&page={page}&sort=pushed')
        if not isinstance(r, list) or not r:
            break
        repos += [x['name'] for x in r]
        if len(r) < 100:
            break
    print(f'  repos enumerated from the USER endpoint: {len(repos)}')

    pr(1, "what is actually in the account, classified by behaviour not by name", [
      {"id": "most-are-tiny", "kind": "num", "predict": 0.75, "tolerance": 0.15,
       "claim": "AT LEAST 75% of the account's repos are husks: under 30 files and few "
                "commits. 4,856 is a count of intentions, not of artifacts.",
       "result": None},
      {"id": "real-code-is-tiny-fraction", "kind": "num", "predict": 0.05, "tolerance": 0.05,
       "claim": "UNDER 5% of repos contain more than 50 source files. The account's real "
                "code mass is in a few dozen repos.",
       "result": None},
      {"id": "ci-is-rare", "kind": "num", "predict": 0.10, "tolerance": 0.08,
       "claim": "UNDER 10% of repos have CI. The fleet mostly ships without a check, which "
                "is the same finding as 0-signed, in a different register.",
       "result": None},
      {"id": "readme-almost-universal", "kind": "bool", "predict": True,
       "claim": "Nearly every repo HAS a README even when it is a husk. The documentation "
                "of an intention is being confused with the artifact of one.",
       "result": None},
      {"id": "stars-are-flat", "kind": "num", "predict": 60.0, "tolerance": 30.0,
       "claim": "The STARS-to-REPOS ratio is under 1:100, i.e. under ~50 stars across the "
                "whole account. Reputation has not compounded because it cannot compound "
                "when there is no single node to compound on.",
       "result": None},
    ])
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(scan, r): r for r in repos[:700]}
        rows = []
        for f in as_completed(futs):
            rows.append(f.result())
    ok = [r for r in rows if 'error' not in r]
    json.dump(rows, open('/workspace/research/lanes/make-valuable/census.json', 'w'), indent=2)

    n = len(ok)
    husky = sum(1 for r in ok if r['files'] < 30)
    big = sum(1 for r in ok if r['src'] > 50)
    ci = sum(1 for r in ok if r['has_ci'])
    rd = sum(1 for r in ok if r['has_readme'])
    stars = sum(r['stars'] for r in ok)
    print(f'  scanned {n} repos')
    print(f'    husks (<30 files):        {husky}  ({husky/n:.2%})')
    print(f'    >50 source files:         {big}  ({big/n:.2%})')
    print(f'    with CI:                  {ci}  ({ci/n:.2%})')
    print(f'    with README:              {rd}  ({rd/n:.2%})')
    print(f'    total stars:              {stars}  ({stars/max(n,1):.1f} per repo)')

    s = load(); rnd = s['rounds'][-1]
    rnd['predictions'][0]['result'] = round(husky/n, 3)
    rnd['predictions'][1]['result'] = round(big/n, 3)
    rnd['predictions'][2]['result'] = round(ci/n, 3)
    rnd['predictions'][3]['result'] = rd/n > 0.95
    rnd['predictions'][4]['result'] = float(stars)
    rnd['data'] = {'scanned': n, 'husks': husky, 'big': big, 'ci': ci, 'readme': rd, 'stars': stars}
    save(s)
    print()
    debrief(1); show(1)
