"""LANE W1 — wide frontier sweep. Not a repeat of the earlier read: that one ran at 05:00Z
against a frontier that has had ~8 hours and a full day of fleet movement since."""
import urllib.request, json, os
from concurrent.futures import ThreadPoolExecutor, as_completed

def ds(prompt, mt=4200, temp=0.9):
    req = urllib.request.Request('https://api.deepseek.com/v1/chat/completions',
        data=json.dumps({'model':'deepseek-flash','messages':[{'role':'user','content':prompt}],
                         'max_tokens':mt,'temperature':temp}).encode(),
        headers={'Authorization':f'Bearer {os.environ["DEEPSEEK_TOKEN"]}',
                 'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req,timeout=180) as r:
            return (json.loads(r.read())['choices'][0]['message'].get('content') or '').strip()
    except Exception as e:
        return f'ERR {e}'

G = """CONTEXT. "SuperInstance" is one person's 4,856-repo, multi-agent substrate. Slogans: "the model doesn't get bigger, the exocortex gets richer"; "intelligence should accrue in an external auditable substrate". Shipped in the last day: a C99 reference port (quilt-c) with 1,285 automated assertions, a one-command `make verify`, a sha256 receipt, a signed git tag v0.1.0, and a third-party release verifier; an A2A "cell API" where the addressable cell is the one resource and BIND/LINK/EFFECT/VIEW/TICK are the methods; a known-answer control that found the fleet's own JEV oracle's `score` question type returns a near-constant 2.6 regardless of input (an empty shell scores the same as numpy); an externalisability gate that found 0 of 10 sealed predictions are decidable by a stranger; and a resolution of the fleet's first live foreign-party forecast.

The stated problem: 4,856 repos, 33 stars, 4 forks, 86 followers. The account's only compounding signal is per-repo trust and it is diluted 240x. The verification discipline is rigorous but INTERNAL — the second reader shares the substrate, the model lineage, and the incentives of the first.

A wide read concluded the deepest problem is IDENTIFIABILITY: the fleet can measure itself precisely and cannot yet measure whether anyone outside cares."""

P = {
'frontier_delta': f"""{G}

What moved in self-improving-agent and agent-fleet research in roughly the last 72 hours that would change this plan? Be concrete: paper titles, authors, claims, and which of them is falsifiable. If you do not know of specific recent work, say so plainly rather than inventing citations — a fabricated citation is worse than an empty answer. Under 300 words.""",

'external_adoption': f"""{G}

The artifact now EXISTS and is verifiable in under 3 seconds by anyone with a clone. It has never been run by anyone outside. What is the single most likely reason, and what is the one concrete distribution move that would actually work for a 4,856-repo account with 33 stars? Do not give generic 'write a blog post' advice. Name the specific venue, the specific framing, and why that venue's audience would care. Under 350 words.""",

'verification_without_trust': f"""{G}

Name every mechanism by which an outside party can verify a claim produced by this fleet WITHOUT running fleet code and WITHOUT trusting any fleet identity. Not just "hashes" and not just "signatures" — enumerate the space, say which ones are actually available given the constraints (no outside org, no funded team, no institutional backing, one person). Rank by what is achievable this week. Under 350 words.""",

'what_to_kill': f"""{G}

The substrate has 4,836 dead repos, a doctrine of receipts and pre-registrations, several autonomous writer identities, a research portfolio, an essay corpus, an art renderer, and now four verification artifacts in one day. Be unsparing. What is the highest-value thing to STOP doing, and what specifically should replace it? Argue the opposite if you think stopping is wrong. Under 300 words.""",

'multi_agent_failure': f"""{G}

Multiple autonomous agents (keeper, Claude, Mavis, CCC) write into ONE GitHub user account. What failure modes does that structurally create that a normal team with named accounts would not have? Name the mechanisms, not the vibe. Then: what is the minimum governance change that would fix the top two without slowing throughput? Under 350 words.""",

'what_would_change_my_mind': f"""{G}

This plan is built on the claim that trust must be externalized. Write the strongest possible case AGAINST that — that externalization is a distraction, that internal rigor is sufficient, that the fleet should just go deeper instead of wider. Make it as persuasive as you can. Then say what evidence would settle it. Under 350 words.""",
}

out = {}
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(ds, p): k for k, p in P.items()}
    for f in as_completed(futs):
        out[futs[f]] = f.result()

json.dump(out, open('wide_scout.json','w'), indent=2)
for k in sorted(out):
    print('='*74); print(k); print('='*74)
    print(out[k][:2000]); print()
