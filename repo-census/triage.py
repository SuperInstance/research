#!/usr/bin/env python3
"""
triage.py — risk + synergy triage over the 201 private repos, BEFORE any of them are
made public. Making a repo public is outward-facing and effectively irreversible in
practice; the cost of the list being wrong is not symmetric with the cost of waiting.

Three things this computes:
  RISK   what must not be published as-is (secrets, backups, bulk content, empty)
  SHAPE  what the repo actually is (the 141-Rust cluster is almost certainly a family)
  SYNERGY what it could become in the fleet, judged on description + language + size
"""
import json, re, os, time, urllib.request, urllib.error
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

TOK=os.environ["GITHUB_TOKEN"]
H={"Authorization":f"Bearer {TOK}","Accept":"application/vnd.github+json","User-Agent":"m"}
SECRET_FILE=re.compile(r"(\.env$|\.env\.|secret|credential|keyring|\.pem$|\.key$|id_rsa|\.netrc|htpasswd|\.p12$|service-account)",re.I)
BULK=re.compile(r"(backup|dump|archive|corpus|dataset|scrape|crawl|mirror)",re.I)

def get(p, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com"+p,headers=H),timeout=35) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (403,429): time.sleep(2*(a+1)); continue
            return {"__err":e.code}
        except Exception:
            if a==tries-1: return {"__err":"net"}
            time.sleep(1.2)
    return {"__err":"retries"}

def scan(r):
    n=r["name"]; out={"name":n,"lang":r.get("language"),"size_kb":r.get("size",0),
        "desc":(r.get("description") or "").strip(),
        "pushed":(r.get("pushed_at") or "")[:10],
        "topics":r.get("topics") or []}
    d=get(f"/repos/SuperInstance/{n}")
    if "__err" in d: out["error"]=d["__err"]; return out
    out["default"]=d.get("default_branch","main"); out["license"]=(d.get("license") or {}).get("spdx_id")
    t=get(f"/repos/SuperInstance/{n}/git/trees/{out['default']}?recursive=1")
    if isinstance(t,dict) and "tree" in t:
        paths=[x["path"] for x in t["tree"] if x["type"]=="blob"]
        out["files"]=len(paths)
        out["readme"]=next((p for p in paths if p.lower().startswith("readme")),None)
        out["secret_files"]=[p for p in paths if SECRET_FILE.search(p)][:8]
        out["bulk_files"]=[p for p in paths if BULK.search(p)][:5]
        out["ext"]=Counter(os.path.splitext(p)[1] for p in paths if "." in p).most_common(5)
    else:
        out["files"]=0; out["readme"]=None; out["secret_files"]=[]; out["bulk_files"]=[]; out["ext"]=[]
    out["RISK"]=("EMPTY" if out.get("size_kb",0)==0 else
                 "SECRETS" if out.get("secret_files") else
                 "BULK" if out.get("bulk_files") or out.get("size_kb",0)>50000 else
                 "OK")
    return out

if __name__=="__main__":
    repos=json.load(open("private.json"))
    rows=[]
    with ThreadPoolExecutor(max_workers=10) as ex:
        for i,x in enumerate(ex.map(scan,repos)):
            rows.append(x)
            if (i+1)%25==0: print(f"    {i+1}/{len(repos)}",flush=True)
    json.dump(rows,open("triage.json","w"),indent=1)
    print(f"\n  triaged {len(rows)}",flush=True)
    print("  RISK:",dict(Counter(r.get("RISK","ERR") for r in rows)),flush=True)
    print("  with a README:",sum(1 for r in rows if r.get("readme")),"/",len(rows),flush=True)
    print("  without a README:",[r["name"] for r in rows if not r.get("readme") and not r.get("error")][:20],flush=True)
    print("\n  RISK != OK:",flush=True)
    for r in rows:
        if r.get("RISK") not in (None,"OK"):
            print(f"    {r.get('RISK'):7} {r['name'][:34]:36} {r.get('size_kb',0):>7}KB  {str(r.get('secret_files') or r.get('bulk_files'))[:60]}",flush=True)
