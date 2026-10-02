"""Round 21: JEV + ZAI agreement on canon candidates."""
import sys, json
sys.path.insert(0, '/workspace/research')
from jev_client import ask, noul, score
from concurrent.futures import ThreadPoolExecutor
import urllib.request, os, re

candidates = [
    'The cell is a SEED, not a system.',
    'Apoptosis is organ failure.',
    'The pipeline IS the agent body.',
    'Substrates are agnostic.',
    'Death is recorded, not erased.',
    'Fractal: cells, quilts, qults, same shape at every scale.',
    'Engine is energy, not instruction.',
    'Combination > intensification.',
    'Cells form communities that grow and die.',
    'A receipt is not documentation, it is substrate.',
]

def jev_score(c):
    r = ask(c, {'canon': noul('Is this canon-worthy doctrine?')})
    return r['answers']['canon']['noul']

def zai_score(c):
    try:
        data = json.dumps({'model':'glm-5.3-flash','messages':[{'role':'user','content':f'Rate this doctrine on a 0.0-1.0 canon scale. Output ONLY the number.\n\nDoctrine: "{c}"'}],'max_tokens':40,'thinking':{'type':'disabled'}}).encode()
        req = urllib.request.Request('https://api.z.ai/api/coding/paas/v4/chat/completions', data=data, method='POST', headers={'Authorization':f'Bearer {os.environ["ZAI_TOKEN"]}','Content-Type':'application/json','User-Agent':'mavis/1.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            body = json.loads(r.read().decode())
            text = body['choices'][0]['message']['content'].strip()
            nums = re.findall(r'0\.[0-9]+|[01]', text)
            return float(nums[0]) if nums else None
    except Exception as e:
        return None

with ThreadPoolExecutor(max_workers=15) as ex:
    jev_results = list(ex.map(jev_score, candidates))
    zai_results = list(ex.map(zai_score, candidates))

print('=== JEV + ZAI agreement on canon ===\n')
print(f'{"canon":55s} {"JEV":>6s} {"ZAI":>6s} {"diff":>5s}')
print('-' * 80)
for c, j, z in zip(candidates, jev_results, zai_results):
    jstr = f'{j:.2f}'
    zstr = f'{z:.2f}' if isinstance(z, float) else str(z)[:6]
    diff = abs(j - z) if isinstance(z, float) else 'n/a'
    diffstr = f'{diff:.2f}' if isinstance(diff, float) else str(diff)
    print(f'{c[:53]:55s} {jstr:>6s} {zstr:>6s} {diffstr:>5s}')

# Correlation
import numpy as np
valid_pairs = [(j, z) for j, z in zip(jev_results, zai_results) if isinstance(z, float)]
if len(valid_pairs) > 2:
    js, zs = zip(*valid_pairs)
    corr = np.corrcoef(js, zs)[0,1]
    print(f'\nPearson correlation (JEV vs ZAI): {corr:.3f}')
