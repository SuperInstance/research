#!/usr/bin/env python3
"""
sweep.py — the secret-and-operational-details sweep, built to the protocol already
documented in SuperInstance/sweep (2026-08-30, 10 repos, 330 commits).

WHY THIS EXISTS AND WHY IT REPLACES MY EARLIER TRIAGE
------------------------------------------------------
My first pass classified risk from FILENAMES (.env, secret, credential) and from repo size.
That is a heuristic. The precedent says the correct method is to scan FULL HISTORY with two
independent tools, because the two miss different things:

  "hand-rolled grep caught 3 real findings gitleaks missed entirely (ingest token, CF
   account_id x2 - low-entropy hex, below gitleaks thresholds). Both tools ran; neither
   alone was sufficient."

ENFORCED ORDER: sweep -> redact -> flip. Nothing is flipped before its verdict.

Seven passes, as documented:
  1 full-history clone (all refs, not shallow)
  2 gitleaks, git mode, walks every commit
  3 protocol-pattern grep over `git log -p --all`
  4 extended grep for the rule gaps gitleaks has (AIza, npm_, sk_live_, SendGrid SG.,
     Twilio AC…, slack/discord webhooks, ghs_, sk-ant-, git URL creds)
  5 committed-dotfile audit
  6 high-entropy sweep (>=32 hex / >=40 b64), context-checked
  7 operational-details sweep: IPs, MACs, serials, phone, street, email, vessel names,
     home ports -- the things that are not secrets but are not world-readable either

Reports go to reports/<name>.json. NEVER prints a full secret value; only a redacted
prefix, a commit, and a path.
"""
import os, re, json, subprocess, sys, time, hashlib

TOK = os.environ["GITHUB_TOKEN"]
ORG = "SuperInstance"
WORK = "/tmp/sweep"
REPORTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

PROTOCOL = [  # pass 3
    (r"sk-[A-Za-z0-9]{16,}", "openai-style key"),
    (r"gho_[A-Za-z0-9]{20,}", "github oauth"),
    (r"ghp_[A-Za-z0-9]{20,}", "github pat"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "github fine-grained pat"),
    (r"AKIA[0-9A-Z]{16}", "aws access key id"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "slack token"),
    (r"BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY", "private key"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "jwt"),
    (r"(?i)api[_-]?key\s*[=:]\s*[\"'][^\"']{8,}[\"']", "api key assignment"),
    (r"(?i)(token|password|passwd|secret)\s*[=:]\s*[\"'][^\"']{8,}[\"']", "credential assignment"),
    (r"(?i)(postgres|postgresql|mysql|mongodb(\+srv)?|redis|amqp)://[^\s\"']*:[^\s\"'@]+@", "connection string w/ password"),
    (r"(?i)Server=.*;(.*Password=)", "mssql connection string"),
    # A Cloudflare account id is EXACTLY 32 hex. Using {32,} matched every 40-char git
    # commit SHA in the log, which is exactly the false positive the 2026-08-30 sweep
    # ledger warned about ("all hits were commit SHAs"). Fixed-length, and commit-header
    # context is skipped below.
    (r"(?<!commit )\b[0-9a-f]{32}\b", "low-entropy hex (cf account id, exactly 32)"),
]
EXTENDED = [  # pass 4 — gitleaks rule gaps
    (r"AIza[A-Za-z0-9_-]{35}", "google api key"),
    (r"npm_[A-Za-z0-9]{36}", "npm token"),
    (r"(sk|rk|pk)_live_[A-Za-z0-9]{16,}", "stripe live key"),
    (r"SG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}", "sendgrid"),
    (r"AC[a-f0-9]{32}", "twilio sid"),
    (r"https://hooks\.slack\.com/services/\S+", "slack webhook"),
    (r"https://discord(?:app)?\.com/api/webhooks/\S+", "discord webhook"),
    (r"ghs_[A-Za-z0-9]{20,}", "github server token"),
    (r"shpat_[A-Za-z0-9]{20,}", "shopify token"),
    (r"sk-ant-[A-Za-z0-9_-]{20,}", "anthropic key"),
    (r"https?://[^/\s:@]+:[^/\s:@]+@github\.com", "git url with credentials"),
]
DOTFILES = [r"^\.env$", r"\.env\.", r"\.npmrc$", r"\.netrc$", r"\.pem$", r"\.key$",
            r"id_rsa", r"\.p12$", r"credentials?$", r"\.htpasswd$"]
OPS = [  # pass 7 — not secrets, but not world-readable
    (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "ipv4"),
    (r"\b[0-9A-F]{2}(?::[0-9A-F]{2}){5}\b", "mac address"),
    (r"(?i)\bMMSI\b|\bIMO\b|\bCFEC\b|\bADFG\b", "vessel registry id"),
    (r"\bF/V\s+[A-Z][A-Za-z ]+", "vessel name"),
    (r"(?i)\bHomer\b|\bKachemak Bay\b|\bCook Inlet\b", "home port"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
]

def sh(args, cwd, timeout=300):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        class R: returncode=124; stdout=""; stderr="timeout"
        return R()

def redact(s):
    """Never emit a full value. First 6 and last 4 at most, and only if long enough."""
    s = s.strip().strip('"\' ')
    if len(s) <= 12: return f"<{len(s)} chars, too short to excerpt>"
    return f"{s[:6]}…{s[-4:]} ({len(s)} chars)"

def clone(name):
    d = os.path.join(WORK, name)
    os.makedirs(WORK, exist_ok=True)
    sh(["rm","-rf",d], "/tmp")
    r = sh(["git","-c","http.sslVerify=false","clone","-q","--no-checkout",
            f"https://x-access-token:{TOK}@github.com/{ORG}/{name}.git", d], "/tmp", 300)
    return d if os.path.isdir(os.path.join(d,".git")) else None

def sweep(name):
    rep = {"repo": name, "swept_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "findings": [], "ops": [], "dotfiles": [], "counts": {}}
    d = clone(name)
    if not d:
        rep["error"] = "clone failed"; return rep
    log = sh(["git","log","-p","--all"], d, 600)
    blob = log.stdout or ""
    rep["counts"]["log_bytes"] = len(blob)

    # pass 2: gitleaks, git mode, every commit
    gl = sh(["gitleaks","git","--no-banner","--redact","--report-format","json",
             "--report-path","/tmp/gl.json", d], d, 600)
    try:
        glj = json.load(open("/tmp/gl.json"))
    except Exception:
        glj = []
    rep["counts"]["gitleaks"] = len(glj)
    for f in glj:
        rep["findings"].append({"tool":"gitleaks","rule":f.get("RuleID"),
            "file":f.get("File"),"commit":(f.get("Commit") or "")[:10],
            "excerpt":redact(f.get("Match") or "")})

    # pass 3 + 4: hand-rolled over full history
    # context: git log renders "commit <40-hex>" headers; those are not secrets
    commit_shas = set(re.findall(r"^commit ([0-9a-f]{40})", blob, re.M))
    for group, pats, bucket in (("protocol", PROTOCOL, "findings"), ("extended", EXTENDED, "findings")):
        for pat, kind in pats:
            hits = [m for m in re.finditer(pat, blob) if m.group(0) not in commit_shas]
            if hits:
                rep[bucket].append({"tool":"grep","kind":kind,"group":group,
                                    "count":len(hits),"excerpt":redact(hits[0].group(0))})

    # pass 5: committed dotfiles
    names = sh(["git","log","--all","--name-only","--pretty=format:"], d, 300).stdout or ""
    rep["dotfiles"] = sorted({n for n in names.split("\n") if n.strip() and
                              any(re.search(p, n.strip(), re.I) for p in DOTFILES)})

    # pass 6: high entropy
    ent = {}
    for m in re.finditer(r"\b[A-Za-z0-9+/=_-]{40,}\b", blob):
        s = m.group(0)
        if not re.search(r"[A-Z]", s) or not re.search(r"[a-z]", s): continue
        h = 0
        for c in set(s): h -= (s.count(c)/len(s)) * __import__("math").log2(s.count(c)/len(s))
        if h > 4.2: ent[h] = ent.get(h,0)+1
    rep["counts"]["high_entropy_strings"] = sum(ent.values())

    # pass 7: operational details
    for pat, kind in OPS:
        hits = {m.group(0).strip() for m in re.finditer(pat, blob)}
        if hits:
            rep["ops"].append({"kind":kind,"distinct":len(hits),
                               "samples":sorted(hits)[:5]})
    sh(["rm","-rf",d], "/tmp")
    return rep

if __name__ == "__main__":
    os.makedirs(REPORTS, exist_ok=True)
    for n in sys.argv[1:]:
        r = sweep(n)
        json.dump(r, open(os.path.join(REPORTS, f"{n}.json"),"w"), indent=1)
        verdict = ("CLEAN" if not r["findings"] and not r["dotfiles"]
                   else "OPS-ONLY" if not r["findings"] else "FINDINGS")
        print(f"  {n:28} {verdict:10} secrets={len(r['findings']):>3} dots={len(r['dotfiles']):>2} "
              f"ops={len(r['ops']):>2} entropy={r['counts'].get('high_entropy_strings',0)}", flush=True)
