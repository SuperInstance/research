"""LANE C: license + hygiene sweep. Census found only 12/33 repos have a detectable license.
Determines WHICH are GitHub detection misses (fixable) vs genuine gaps (legal choice)."""
import urllib.request, json, os, re
from concurrent.futures import ThreadPoolExecutor, as_completed

H = {'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}',
     'Accept': 'application/vnd.github+json', 'User-Agent': 'mavis-license'}

REPOS = ['fleet-seeds','MicroMoth-quilt','AI-Writings','quilt-jepa','PersonalLog','jev-garden',
 'SmartCRDT','polln','exoj','quilt-gpu-lab','pong-quilt','quilt-research-canons','Syzygy',
 'quilt','breakthrough-prospector','mavis-pincher','mavis-pincher-pages','mavis-essay-scout',
 'chiaroscuro','PuddnHead','qthe-verify','quilt-c','quilt-fleet','quilt-elf','quilt-rag',
 'quilt-swarm','webgpu-profiler','CognitiveEngine','edge-native-paper','glyphcast',
 'quilt-canary','quilt-canary-port','superinstance-polyformalism-harness']

SIGNS = {
 'Apache-2.0':  r'Apache License',
 'MIT':         r'Permission is hereby granted, free of charge',
 'GPL-3.0':     r'GNU GENERAL PUBLIC LICENSE',
 'AGPL-3.0':    r'GNU AFFERO GENERAL PUBLIC LICENSE',
 'BSD-3-Clause':r'Redistribution and use in source and binary forms',
 'Unlicense':   r'This is free and unencumbered software',
 'CC0-1.0':     r'CC0 1.0 Universal',
 'MPL-2.0':     r'Mozilla Public License',
 'ISC':         r'Permission to use, copy, modify, and/or distribute',
}
VALID = tuple(SIGNS.keys())

def gh(p):
    try:
        req = urllib.request.Request(f'https://api.github.com{p}', headers=H)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'__err': str(e)[:60]}

def raw(repo, path, ref):
    for b in (ref, 'main', 'master'):
        try:
            req = urllib.request.Request(
                f'https://raw.githubusercontent.com/SuperInstance/{repo}/{b}/{path}',
                headers={'User-Agent': 'mavis-license'})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            continue
    return None

def scan(repo):
    m = gh(f'/repos/SuperInstance/{repo}')
    if '__err' in m: return {'repo': repo, 'error': m['__err']}
    out = {'repo': repo,
           'gh_license': (m.get('license') or {}).get('spdx_id'),
           'archived': m.get('archived'),
           'default_branch': m.get('default_branch'),
           'pushed': (m.get('pushed_at') or '')[:10],
           'stars': m.get('stargazers_count', 0),
           'found_file': None, 'detected_spdx': None, 'detect_bytes': 0}
    tree = gh(f'/repos/SuperInstance/{repo}/git/trees/HEAD?recursive=1')
    paths = [t['path'] for t in tree.get('tree', []) if t['type'] == 'blob'] if 'tree' in tree else []
    lic = [p for p in paths if re.match(r'(?i)^(licen[sc]e|copying)(\.\w+)?$', p)]
    if not lic:
        lic = [p for p in paths if re.search(r'(?i)(^|/)licen[sc]e', p) and p.count('/') == 0]
    out['license_paths'] = lic[:3]
    for p in lic[:1]:
        txt = raw(repo, p, m.get('default_branch', 'main'))
        if txt:
            out['found_file'] = p; out['detect_bytes'] = len(txt)
            for spdx, pat in SIGNS.items():
                if re.search(pat, txt[:4000], re.I):
                    out['detected_spdx'] = spdx; break
    out['has_readme'] = any(p.lower().startswith('readme') for p in paths)
    out['has_contributing'] = any(re.search(r'(?i)contributing', p) for p in paths)
    out['has_ci'] = any(p.startswith('.github/workflows/') for p in paths)
    out['file_count'] = len(paths)
    return out

res = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(scan, r): r for r in REPOS}
    for f in as_completed(futs):
        try: res[futs[f]] = f.result()
        except Exception as e: res[futs[f]] = {'repo': futs[f], 'error': str(e)[:60]}

json.dump(res, open('license.json', 'w'), indent=2)
ok = [r for r in res.values() if 'error' not in r]
MISS, GAP, CLEAN = [], [], []
for r in ok:
    if r['gh_license'] in VALID: CLEAN.append(r)
    elif r['detected_spdx']: MISS.append(r)
    else: GAP.append(r)

print('='*86)
print('LANE C — LICENSE + HYGIENE SWEEP')
print('='*86)
print(f'scanned {len(ok)}   clean:{len(CLEAN)}   detection-miss:{len(MISS)}   genuine-gap:{len(GAP)}')
print()
print('--- A. GITHUB DETECTION MISS (LICENSE file exists, GH says NOASSERTION/None) ---')
print('    Fixable by editing the file. NOT a legal decision.')
for r in sorted(MISS, key=lambda x: -x['stars']):
    print(f"    {r['repo']:30} gh={str(r['gh_license']):12} ACTUAL={r['detected_spdx']:12} {r['found_file']:14} {r['detect_bytes']:6}B")
print()
print('--- B. GENUINE GAP (no LICENSE file) — needs a legal choice from Casey ---')
for r in sorted(GAP, key=lambda x: -x['file_count']):
    print(f"    {r['repo']:30} files={r['file_count']:5} CI={str(r['has_ci']):5} README={str(r['has_readme']):5} pushed={r['pushed']}")
print()
print('--- C. HYGIENE ---')
print(f"    README:       {sum(1 for r in ok if r['has_readme'])}/{len(ok)}")
print(f"    CI:           {sum(1 for r in ok if r['has_ci'])}/{len(ok)}")
print(f"    CONTRIBUTING: {sum(1 for r in ok if r['has_contributing'])}/{len(ok)}")
print(f"    archived:     {sum(1 for r in ok if r['archived'])}")
print(f"    stale >30d:   {sum(1 for r in ok if r['pushed'] and r['pushed'] < '2026-08-30')}")
