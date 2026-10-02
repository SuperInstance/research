#!/usr/bin/env python3
"""
specificity.py — the decisive test. Is the gate detecting TRUTH, or detecting SPECIFICITY?

evidence_state.py produced an inverted result. The two claims whose evidence contradicted
them scored HIGHEST (0.62, 0.61). That is not entailment. A scorer that rewards "this state
is a good basis for this question" would do exactly that.

If the gate detects SPECIFICITY, then:
  false-but-specific   -> high        (the dangerous case: a confident error passes)
  true-but-vague       -> low         (the embarrassing case: a true thing gets rejected)
  true-and-specific    -> high        (what a clean KAT looks like, and why it fooled me)
  vague                -> low         (what my KAT's "false" arms actually were)

Every earlier success is explained by the third and fourth rows, and every failure by the
first two. The KAT did not pass because it measured truth. It passed because its negative
arms were HEDGES, and a hedge is the one thing the gate reliably rejects.
"""
import json, os, time, urllib.request, urllib.error
KEY=os.environ.get("TYPESAFEAI_KEY",""); URL="https://api.typesafe.ai/v1/systemone"
CRIT={"true":"The claim is accurate, specific, and verifiable.","false":"The claim is false, vague, or unverifiable."}

# Each row is pre-registered with its truth AND its specificity, BEFORE scoring.
CELLS = [
 # label, state, claim, truth, specific
 ("true+specific", "Ran the QuiltCanary test suite on Julia 1.11.3: 13 tests, 0 failures. canary() returns 0x024a555471370b18d.",
    "FNV-1a 64 of the UTF-8 bytes of 'cafe Δ 日本語' is 0x024a555471370b18d.", 1, 1),
 ("false+specific","grep -rniw compile over forgemaster/src/ returns zero matches. The Forge.compile method named in the README does not exist in the source.",
    "Forgemaster's Forge.compile method exists in the source and is documented in the README.", 0, 1),
 ("false+hedge",   "Nothing in particular has been established about this repository at this time.",
    "The build system is well known to work well in many situations.", 0, 0),
 ("true+vague",    "Entropy behaves in a familiar way under a uniform distribution.",
    "Entropy is maximised by a uniform distribution over a fixed support.", 1, 0),
 ("false+confident","JEV's noul question type is documented to return a probability that the claim follows from the state.",
    "JEV's noul question type returns a probability that the claim follows from the state.", 0, 1),
 ("true+confident","A commit comment whose body is exactly /register, posted on a commit in a public GitHub repository, is the documented trigger for Registrator.jl to open a registration pull request.",
    "A comment containing /register on a commit is the documented trigger for Registrator.jl to open a registration pull request.", 1, 1),
]
def ask(state, claim, tries=3):
    body={"model":"jev-latest","state":state,"questions":{"q":{"type":"noul",
      "instructions":"Is this claim true as stated, and would a careful reader who knows the subject agree?",
      "criteria":CRIT}}}
    for a in range(tries):
        try:
            req=urllib.request.Request(URL,data=json.dumps(body).encode(),
              headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=60) as r:
                d=json.loads(r.read()); v=d["answers"]["q"]
                return float(v.get("noul",v.get("answer",{}).get("noul",-1)))
        except urllib.error.HTTPError as e: err=f"HTTP{e.code} {e.read()[:70].decode('utf-8','replace')}"
        except Exception as e: err=str(e)[:70]
        time.sleep(1.5*(a+1))
    return err

if __name__=="__main__":
    print(f"  {'cell':16} {'truth':6} {'specific':9} {'noul':>7}")
    out=[]
    for lab,state,claim,t,sp in CELLS:
        v=ask(state,claim)
        if isinstance(v,str): print("  API error:",v); raise SystemExit(2)
        out.append({"cell":lab,"truth":t,"specific":sp,"noul":v})
        print(f"  {lab:16} {t:<6} {sp:<9} {v:>7.3f}")
    def mean(i,f): 
        xs=[o['noul'] for o in out if f(o)]; return sum(xs)/len(xs) if xs else float('nan')
    print(f"\n  mean noul | true claims   {mean(0,lambda o:o['truth']==1):.3f}")
    print(f"  mean noul | false claims  {mean(0,lambda o:o['truth']==0):.3f}")
    print(f"  mean noul | specific      {mean(0,lambda o:o['specific']==1):.3f}")
    print(f"  mean noul | vague         {mean(0,lambda o:o['specific']==0):.3f}")
    json.dump(out,open("/workspace/research/jev-fleet/specificity_result.json","w"),indent=1)
