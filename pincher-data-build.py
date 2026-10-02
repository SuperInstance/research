#!/usr/bin/env python3
"""Generate the pincher dataset (50 most-active repos with family classification)."""
import json
from pathlib import Path

# Family classification by name prefix (precedence: jev > latent > moth > qthe > quilt > fleet)
def classify(name: str) -> str:
    n = name.lower()
    if n.startswith('jev-') or n == 'jev-quilt' or n == 'jev-garden' or n == 'jeviter':
        return 'jev'
    if n.startswith('latent-') or 'jepa' in n:
        return 'latent'
    if n.startswith('moth-') or 'moth' in n or 'micro' in n:
        return 'moth'
    if n.startswith('qthe') or 'ternary' in n or 'tw' in n:
        return 'qthe'
    if n.startswith('quilt'):
        return 'quilt'
    if n.startswith('fleet') or n.startswith('superinstance-'):
        return 'fleet'
    return 'other'

def make_keywords(name: str, desc: str) -> list:
    text = (name + ' ' + (desc or '')).lower()
    stopwords = {'the','a','an','and','or','but','of','to','in','on','for','with','as','by','at','from','is','are','be','this','that','it','its','into','via','per','not'}
    words = []
    for w in text.replace('-', ' ').replace('_', ' ').replace('/', ' ').replace('.', ' ').split():
        w = w.strip("\"'`()[]{},;:!?")
        if 3 <= len(w) <= 25 and w not in stopwords and not w.isdigit():
            words.append(w)
    seen = set()
    out = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
            if len(out) >= 12:
                break
    return out

raw = json.load(open('/tmp/repos-50.json'))

records = []
for r in raw:
    family = classify(r['name'])
    keywords = make_keywords(r['name'], r.get('description',''))
    rec = dict(r)
    rec['family'] = family
    rec['keywords'] = keywords
    records.append(rec)

out_path = Path('/tmp/pincher-repos.json')
out_path.write_text(json.dumps({
    'generated': '2026-09-28T19:00:00Z',
    'generator': 'mavis-pincher data build',
    'count': len(records),
    'families': {fam: sum(1 for r in records if r['family'] == fam) for fam in set(r['family'] for r in records)},
    'records': records,
}, indent=2))
print(f'Wrote {out_path} ({out_path.stat().st_size} bytes, {len(records)} records)')
families = {}
for r in records:
    families[r['family']] = families.get(r['family'], 0) + 1
print(f'Family counts: {families}')
