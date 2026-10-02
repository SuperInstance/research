#!/usr/bin/env python3
"""
fleet_gate.py — point the canon gate at the fleet's own claims.

Every claim in CORPUS has a ground truth established by artifact inspection in this
session — a file that exists or does not, a test that runs, a number that reproduces.
So this is not "ask JEV about things and see what it says." It is a known-answer
control on the GATE, using real material the gate was never tested against.

The two questions that matter:
  1. Does the gate separate claims we know are TRUE from claims we know are FALSE?
  2. Where it fails, is the failure in the claim, the context, or the gate?
"""
import json, os, time, urllib.request, urllib.error

KEY = os.environ.get("TYPESAFEAI_KEY", "")
URL = "https://api.typesafe.ai/v1/systemone"

# label, claim, ground truth (1 = claim is true as stated, 0 = it is not)
CORPUS = [
 # --- claims established FALSE by artifact inspection tonight -------------------
 ("claw",   "The claw repository implements a ternary action routing system, conservation-aware scheduling, and gamma-eta-equals-C enforcement.", 0),
 ("claw2",  "The claw repository contains files implementing gamma_drift detection and a gamma plus eta equals C conservation framework.", 0),
 ("polln",  "PlinkoLayer's calculateEntropy returns Shannon entropy of the confidence distribution.", 0),  # true AFTER my fix
 ("pincher","pincher-core's CI has been failing continuously since 2026-06-06 because a test asserts a sandbox mechanism the runner cannot provide.", 1),
 ("pincher2","When bwrap is absent and the landlock feature is not compiled in, pincher warns that the sandbox will use landlock-only mode.", 0),
 ("kv",      "polln's CI has never run its 185 test files; the workflow only built, with continue-on-error.", 1),
 ("vectorize","Cloudflare Vectorize silently drops writes: insert returns 200 and the row count stays 0 forever.", 0),
 ("subagents","A subagent session reporting succeeded produced a written report artifact at the requested path.", 0),
 # --- claims established TRUE by execution tonight -------------------------------
 ("canary",  "FNV-1a 64 of the UTF-8 bytes of the string cafe Delta 日本語 is 0x024a555471370b18d.", 1),
 ("egg",     "In quilt-egg, resonance equals weight times one minus the absolute value of weight minus stimulus, and this is monotone increasing in weight over the relevant range.", 1),
 ("aperture","A content matcher on a repeating texture reports 33.2 percent of cells unmatched when 100 percent of cells truly moved.", 1),
 ("wheel",   "The wheel's GAP cells were produced by a stop-word list that filtered the corpus's own vocabulary.", 1),
 ("tps",     "polln's README documented 273 total tests when the live suite registers 268 in tests/ plus 8 in tools/test-qa.js.", 0),
 ("konform", "A grep for the word compile across forgemaster's source finds matches, so its Forge.compile method exists.", 0),
]

CRIT = {"true": "The claim is accurate as stated and verifiable.",
        "false": "The claim is false, overstated, or not supported by the artifact it cites."}

def batch(claims, use_named=True, model="jev-latest", name="batch"):
    """Subject-NAMED batching. The rule derived over 11 loop rounds:
       a question that points at a part of the state is evaluated against that part.
       An unnamed question gets the whole state's answer, and N of those are identical."""
    state = " || ".join(f"Subject {i}: {c}" for i, (_, c, _) in enumerate(claims)) if use_named \
            else " || ".join(c for _, c, _ in claims)
    qs = {}
    for i, (_, c, _) in enumerate(claims):
        instr = (f"Regarding Subject {i}: Is this claim true as stated, and would a careful reader who knows the subject agree?"
                 if use_named else
                 "Is this claim true as stated, and would a careful reader who knows the subject agree?")
        qs[f"s{i}"] = {"type": "noul", "instructions": instr, "criteria": CRIT}
    body = {"model": model, "state": state, "questions": qs}
    for a in range(3):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
                return {i: float(d["answers"][f"s{i}"].get("noul", -1)) for i in range(len(claims))}
        except urllib.error.HTTPError as e:
            err = f"HTTP{e.code} {e.read()[:70].decode('utf-8','replace')}"
        except Exception as e:
            err = str(e)[:70]
        time.sleep(1.5 * (a + 1))
    return err

def auc(pairs):
    pos = sorted(p for y, p in pairs if y == 1); neg = sorted(p for y, p in pairs if y == 0)
    if not pos or not neg: return float("nan")
    n = s = 0
    for a in pos:
        for b in neg:
            n += 1; s += 1.0 if a > b else (0.5 if a == b else 0.0)
    return s / n

if __name__ == "__main__":
    named  = batch(CORPUS, use_named=True)
    unnamed = batch(CORPUS, use_named=False)
    if isinstance(named, str) or isinstance(unnamed, str):
        print("  API error:", named if isinstance(named, str) else unnamed); raise SystemExit(2)
    print(f"  {'claim':10} {'truth':6} {'NAMED':>7} {'unnamed':>9}   text")
    for i, (lab, c, truth) in enumerate(CORPUS):
        print(f"  {lab:10} {truth:<6} {named[i]:>7.3f} {unnamed[i]:>9.3f}   {c[:64]}")
    n_pairs = [(t, named[i]) for i, (_, _, t) in enumerate(CORPUS)]
    u_pairs = [(t, unnamed[i]) for i, (_, _, t) in enumerate(CORPUS)]
    print(f"\n  named   AUC {auc(n_pairs):.3f}   spread(true) {sum(p for y,p in n_pairs if y)/max(1,sum(1 for y,_ in n_pairs if y)):.3f}"
          f"   spread(false) {sum(p for y,p in n_pairs if not y)/max(1,sum(1 for y,_ in n_pairs if not y)):.3f}")
    print(f"  unnamed AUC {auc(u_pairs):.3f}")
    # the gate's own decision, at its own threshold
    for nm, pairs in (("named", n_pairs), ("unnamed", u_pairs)):
        tp = sum(1 for y,p in pairs if y==1 and p>0.7); fn = sum(1 for y,p in pairs if y==1 and p<=0.7)
        fp = sum(1 for y,p in pairs if y==0 and p>0.7); tn = sum(1 for y,p in pairs if y==0 and p<=0.7)
        print(f"  gate @0.7 {nm:8} accepts {tp} true / {tp+fp}   rejects {tn} true+false correctly; "
              f"{fn} true rejected, {fp} false accepted")
    json.dump({"claims":[{"label":l,"claim":c,"truth":t,"named":named[i],"unnamed":unnamed[i]}
              for i,(l,c,t) in enumerate(CORPUS)],
              "auc_named":auc(n_pairs),"auc_unnamed":auc(u_pairs)},
              open("/workspace/research/jev-fleet/fleet_gate_result.json","w"), indent=1)
