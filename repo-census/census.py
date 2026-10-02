#!/usr/bin/env python3
"""
census.py — inventory every SuperInstance repo, private and public, with the facts
needed to decide what to do with each one.

Deliberately does NOT flip anything. It reports. Making a repo public is an
outward-facing act with a blast radius, so the census's job is to make the decision
informed rather than to make it.

Fields that matter for the publish decision:
  size_kb / empty      — an empty repo has nothing to polish
  secrets             — filename heuristic ONLY; must be confirmed by reading
  age_days            — stale repos need a different treatment than active ones
  has_readme          — the thing we are here to fix
  lang / commits      — what it actually is
"""
import os, json, time, urllib.request, urllib.error, re
from concurrent.futures import ThreadPoolExecutor

TOK = os.environ["GITHUB_TOKEN"]
ORG = "SuperInstance"
H = {"Authorization": f"Bearer {TOK}", "Accept": "application/vnd.github+json", "User-Agent": "m"}
S = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{16,}|(?:api[_-]?key|token|secret|password)\s*[:=]\s*['\"][^'\"]{8,}")
SECRET_NAMES = re.compile(r"(\.env$|\.env\.|secret|credential|keyring|\.pem$|\.key$|id_rsa|token$|\.netrc|htpasswd)", re.I)

def get(path, tries=4):
    for a in range(tries):
        try:
            req = urllib.request.Request("https://api.github.com" + path, headers=H)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(2.5 * (a + 1)); continue
            return {"__err": e.code}
        except Exception:
            if a == tries - 1: return {"__err": "net"}
            time.sleep(1.5 * (a + 1))
    return {"__err": "retries"}

def one(name):
    r = get(f"/repos/{ORG}/{name}")
    if "__err" in r:
        return {"name": name, "error": r["__err"]}
    d = {
        "name": name, "private": r.get("private"), "fork": r.get("fork"),
        "desc": (r.get("description") or "").strip(),
        "size_kb": r.get("size", 0), "lang": r.get("language"),
        "default": r.get("default_branch", "main"),
        "pushed": r.get("pushed_at"), "created": r.get("created_at"),
        "topics": r.get("topics") or [],
        "stars": r.get("stargazers_count", 0),
        "archived": r.get("archived"), "has_issues": r.get("has_issues"),
        "open_issues": r.get("open_issues_count", 0),
        "license": (r.get("license") or {}).get("spdx_id"),
        "homepage": r.get("homepage") or "",
    }
    d["age_days"] = round((time.time() - time.mktime(time.strptime(d["pushed"][:19], "%Y-%m-%dT%H:%M:%S"))) / 86400, 1)
    t = get(f"/repos/{ORG}/{name}/git/trees/{d['default']}?recursive=1")
    if isinstance(t, dict) and "tree" in t:
        paths = [x["path"] for x in t["tree"] if x["type"] == "blob"]
        d["files"] = len(paths)
        d["readme"] = next((p for p in paths if p.lower().startswith("readme")), None)
        d["secret_names"] = [p for p in paths if SECRET_NAMES.search(p)][:6]
        d["secretish"] = [p for p in paths if p.endswith((".env", ".pem", ".key", ".p12"))][:6]
    else:
        d["files"] = 0; d["readme"] = None; d["secret_names"] = []; d["secretish"] = []
    return d

if __name__ == "__main__":
    # NOTE: /orgs/<org>/repos returns 404 for this org; /users/<org>/repos works.
    # The first version of this script used the /orgs/ path and printed "0 repos" --
    # indistinguishable from an empty org. A census that cannot distinguish
    # "the listing failed" from "the org is empty" is worse than no census.
    names, page, listed = [], 1, 0
    while True:
        d = get(f"/users/{ORG}/repos?per_page=100&type=all&page={page}")
        if isinstance(d, dict):
            raise SystemExit(f"FATAL: repo listing returned {d} -- refusing to report a count "
                             f"from a failed read. (A 404/403 here is a read failure, not an empty org.)")
        if not isinstance(d, list):
            raise SystemExit(f"FATAL: unexpected listing type {type(d)}")
        if not d: break
        names += [x["name"] for x in d]; listed += len(d)
        if len(d) < 100: break
        page += 1
    if not names:
        raise SystemExit("FATAL: listing succeeded but returned zero repos. Aborting rather than "
                         "publishing a census built on an empty read.")
    print(f"  {len(names)} repos in {ORG} (listed across {page} page(s))", flush=True)
    out = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, row in enumerate(ex.map(one, names)):
            out.append(row)
            if (i + 1) % 25 == 0: print(f"    {i+1}/{len(names)}", flush=True)
    out.sort(key=lambda r: r["name"])
    json.dump(out, open("/workspace/research/repo-census/census.json", "w"), indent=1)
    priv = [r for r in out if r.get("private")]
    pub = [r for r in out if not r.get("private")]
    print(f"\n  public {len(pub)}   private {len(priv)}   errors {sum(1 for r in out if r.get('error'))}", flush=True)
    print(f"  private with 0 files: {sum(1 for r in priv if r.get('files')==0)}", flush=True)
    print(f"  private with a secret-shaped filename: {sum(1 for r in priv if r.get('secretish') or r.get('secret_names'))}", flush=True)
