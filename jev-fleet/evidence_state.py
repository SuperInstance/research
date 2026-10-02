#!/usr/bin/env python3
"""
evidence_state.py — the gate was fed claims. Feed it evidence.

fleet_gate.py scored every claim at AUC 0.510. The suspicion: I built the state out of
the CLAIM TEXTS, so every question was "does this sentence entail itself." That is
self-consistency, not truth.

JEV is an entailment oracle: it answers whether a STATE licenses a CLAIM. Give it the
sentence as the state and the sentence as the claim and you have measured nothing.

This gives it the artifact instead. Same claims, same questions, one variable changed.
"""
import json, os, time, urllib.request, urllib.error, subprocess

KEY = os.environ.get("TYPESAFEAI_KEY",""); URL="https://api.typesafe.ai/v1/systemone"
CRIT={"true":"The claim is accurate as stated and verifiable.","false":"The claim is false, overstated, or not supported by the artifact it cites."}

def get(claim, state, tries=3):
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

# Real evidence, gathered now, for claims with known ground truth.
EVIDENCE = {
 "claw": ("The claw repository file listing, complete:\n"
   "README.md, LICENSE, .gitignore, Dockerfile, docker-compose.yml,\n"
   "claw.toml, package.json, .github/workflows/ci.yml, tests/run.sh,\n"
   "docs/*.md. No routing, conservation, or gamma source files exist.",
   0),
 "canary": ("Python: hashlib test output -> 'café Δ 日本語' => 0x024a555471370b18d PASS\n"
   "TypeScript, Rust, C#: identical digest asserted, all three test suites pass.\n"
   "Julia: QuiltCanary.canary() => 0x024a555471370b18d, 13/13 tests pass.",
   1),
 "vectorize": ("Cloudflare Vectorize measurement: POST /insert returns HTTP 200.\n"
   "An immediate GET /list shows 0 rows. Re-reading at t+5s shows 0; at t+15s the row\n"
   "is present. The write was not dropped; the read was too early.",
   0),
 "konform": ("grep -rniw compile over forgemaster/src/ returns 0 matches.\n"
   "The README documents Forge.compile; the method does not exist in the source.",
   0),
 "aperture": ("GPU aperture experiment, 60s run, executed:\n"
   "Repeating texture, 50% of cells panned. Motion-mask content matcher reports\n"
   "33.2% unmatched. A true baseline in which NO cell moves reports 0.0%.\n"
   "So 33.2% is 100% of what actually moved.",
   1),
}
if __name__=="__main__":
    print(f"  {'claim':11} {'truth':5} {'claim-as-state':>14} {'evidence-as-state':>17}")
    rows=[]
    for k,(state,truth) in EVIDENCE.items():
        claim = [c for lab,c,t in [
            ("claw","The claw repository implements a ternary action routing system, conservation-aware scheduling, and gamma-eta-equals-C enforcement.",0),
            ("canary","FNV-1a 64 of the UTF-8 bytes of the string cafe Delta 日本語 is 0x024a555471370b18d.",1),
            ("vectorize","Cloudflare Vectorize silently drops writes: insert returns 200 and the row count stays 0 forever.",0),
            ("konform","A grep for the word compile across forgemaster's source finds matches, so its Forge.compile method exists.",0),
            ("aperture","A content matcher on a repeating texture reports 33.2 percent of cells unmatched when 100 percent of cells truly moved.",1),
        ] if lab==k][0]
        a=get(claim, claim); b=get(claim, state)
        if isinstance(a,str) or isinstance(b,str): print("  API error", a if isinstance(a,str) else b); continue
        rows.append((truth,a,b))
        print(f"  {k:11} {truth:<5} {a:>14.3f} {b:>17.3f}")
    if rows:
        def sep(rs,ix):
            t=[r[ix] for r in rs if r[0]==1]; f=[r[ix] for r in rs if r[0]==0]
            return (sum(t)/len(t) if t else 0)-(sum(f)/len(f) if f else 0)
        print(f"\n  separation (true-mean minus false-mean):")
        print(f"    claim-as-state    {sep(rows,1):+.3f}")
        print(f"    evidence-as-state {sep(rows,2):+.3f}   <- the only change")
