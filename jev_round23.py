"""Round 23: JEV canon-gate 50 SuperInstance repos."""
import sys, json, os, glob
sys.path.insert(0, '/workspace/research')
from jev_client import ask, noul, choice

docs = sorted(glob.glob('/workspace/repos/*/README.md'))[:50]
results = []
for path in docs:
    text = open(path).read()
    if len(text) < 300:
        continue
    r = ask(text[:3000], {
        'canon': noul('Is this canon-worthy Quilt doctrine?'),
        'domain': choice('Domain?',
                          {"quilt": "quilt-cellular",
                           "agent": "agent / multi-agent",
                           "infra": "infrastructure / devops",
                           "data": "data / analytics",
                           "ai_research": "AI research",
                           "policy": "policy / governance",
                           "audio": "audio / sound",
                           "creative": "creative / generative"}),
    })
    name = os.path.basename(os.path.dirname(path))
    canon = r['answers']['canon']['noul']
    domain = r['answers']['domain']['choice']
    results.append((canon, domain, name))

results.sort(reverse=True)
print('=== JEV canon-gate (50 SuperInstance repos) ===\n')
print(f'{"":1s} {"canon-p":>7s}  {"domain":14s}  repo')
print('-' * 60)
for canon, domain, name in results:
    flag = '+' if canon >= 0.5 else ' '
    print(f'{flag} {canon:>6.2f}  {domain:14s}  {name}')
