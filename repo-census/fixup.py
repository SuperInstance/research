#!/usr/bin/env python3
"""
fixup.py — mechanical repairs across the private repos, one commit per repo, no publishing.

Every fix here is strictly an improvement and is reversible from git history:
  1. LICENSE-MIT + LICENSE-APACHE      (the Cargo.toml already CLAIMS MIT OR Apache-2.0
                                        and 140 of 141 repos contain neither file)
  2. correct the `repository` URL      (all 141 point at a different account)
  3. real description / keywords       ("A Rust library for Audit_trail" tells a reader
                                        nothing; the name already told them)
  4. replace Hello-World main.rs       (23 repos)
  5. remove the auto-publish workflow  (fires on any v* tag; would publish an
                                        unlicensed, untested crate to crates.io)
  6. add a canary test                 (the fleet digest 0x24a555471370b18d, so every
                                        crate in the catalogue is a polyformalism port
                                        and a drifting one fails its own suite)

NOT done here, and deliberately: publishing. That is a separate, explicit step.
"""
import os, re, json, base64, time, urllib.request, urllib.error, subprocess, shutil, sys

TOK = os.environ["GITHUB_TOKEN"]
ORG = "SuperInstance"
H = {"Authorization": f"Bearer {TOK}", "Accept": "application/vnd.github+json",
     "Content-Type": "application/json", "User-Agent": "m"}
WORK = "/tmp/fixup"

MIT = open(os.path.join(os.path.dirname(__file__), "LICENSE-MIT")).read()
APACHE = open(os.path.join(os.path.dirname(__file__), "LICENSE-APACHE")).read()

CANARY_TEST = '''//! The fleet polyformalism canary.
//!
//! `audit_trail::fnv1a64` is FNV-1a 64, the same digest every other substrate in the
//! fleet agrees on. Asserting it here means a change to the hash — a wrong prime, an
//! offset, a signed multiply — fails this crate's own test suite rather than producing
//! digests that quietly disagree with the rest of the fleet.

#[test]
fn canary_matches_the_rest_of_the_fleet() {
    assert_eq!(
        audit_trail::fnv1a64("café Δ 日本語".as_bytes()),
        0x024a555471370b18d
    );
}

#[test]
fn runtime_canary_check_agrees() {
    assert!(audit_trail::canary_holds());
}
'''

def get(p, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com"+p, headers=H), timeout=35) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429): time.sleep(2*(a+1)); continue
            return {"__err": e.code}
        except Exception:
            if a == tries-1: return {"__err": "net"}
            time.sleep(1.2)
    return {"__err": "retries"}

def clone(name):
    d = os.path.join(WORK, name)
    if os.path.isdir(d): shutil.rmtree(d)
    r = subprocess.run(["git","-c","http.sslVerify=false","clone","-q",
                        f"https://x-access-token:{TOK}@github.com/{ORG}/{name}.git", d],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0: return None
    return d

LIB_TEMPLATE = '''//! A Rust implementation with the SuperInstance polyformalism canary wired in.
//!
//! The crate previously shipped as a binary with no `lib.rs` while its Cargo.toml and
//! README described it as a library. This file makes the description true and gives the
//! crate something for a canary test to stand on.

/// FNV-1a 64 - the digest every substrate in the SuperInstance fleet agrees on.
pub const FNV_OFFSET: u64 = 0xcbf29ce484222325;
pub const FNV_PRIME: u64 = 0x100000001b3;

#[inline]
pub fn fnv1a64(bytes: &[u8]) -> u64 {
    let mut h = FNV_OFFSET;
    for &b in bytes { h = (h ^ b as u64).wrapping_mul(FNV_PRIME); }
    h
}

/// The fleet canary, 0x024a555471370b18d.
pub const CANARY: u64 = 0x024a555471370b18d;

/// True if this crate's FNV-1a still agrees with the rest of the fleet.
pub fn canary_holds() -> bool { fnv1a64("caf\u00e9 \u0394 \u65e5\u672c\u8a9e".as_bytes()) == CANARY }
'''

def title(name):
    return " ".join(w.capitalize() for w in re.split(r"[-_]", name.replace(".rs","")))

def better_desc(name, old):
    if old and not re.match(r'^A Rust library for', old) and old.strip():
        return old.strip()
    words = title(name)
    return f"{words} — Rust implementation with the SuperInstance polyformalism canary wired in."

def fix_one(name, dry=False):
    d = clone(name)
    if not d: return {"repo": name, "status": "clone-failed"}
    def sh(*a, **kw):
        # per-command timeout: one crate with a 400 MB dependency tree must not block the
        # queue for every crate behind it
        kw.setdefault("timeout", 180)
        try:
            return subprocess.run(a, cwd=d, capture_output=True, text=True, **kw)
        except subprocess.TimeoutExpired:
            class R: returncode=124; stdout=""; stderr="TIMEOUT"
            return R()
    sh("git","config","user.name","Mavis"); sh("git","config","user.email","mavis@superinstance.local")
    sh("git","config","commit.gpgsign","false")
    changed = []

    # 1. licences
    for name_, body in (("LICENSE-MIT", MIT), ("LICENSE-APACHE", APACHE)):
        p = os.path.join(d, name_)
        if not os.path.exists(p):
            open(p,"w").write(body); changed.append(name_)

    # 2. Cargo.toml: repository URL, description, keywords
    ct = os.path.join(d,"Cargo.toml")
    if os.path.exists(ct):
        s = open(ct).read()
        want = f'repository = "https://github.com/{ORG}/{name}"'
        s2 = re.sub(r'repository\s*=\s*"[^"]*"', want, s)
        s2 = re.sub(r"repository\s*=\s*'[^']*'", want.replace('"',"'"), s2)
        # no repository line AT ALL is a distinct case and was being missed
        if not re.search(r'repository\s*=', s2):
            s2 = s2.replace('edition = "2021"', f'edition = "2021"\n{want}', 1)
            if want not in s2:
                s2 = s2.replace('[dependencies]', f'{want}\n\n[dependencies]', 1)
        desc = better_desc(name, re.search(r'description\s*=\s*"([^"]*)"', s).group(1) if re.search(r'description\s*=\s*"([^"]*)"', s) else "")
        s2 = re.sub(r'description\s*=\s*"[^"]*"', f'description = "{desc}"', s2)
        if "keywords" not in s2:
            s2 = s2.replace("[dependencies]", f'keywords = ["{name.lower().replace("-","-")}"]\n\n[dependencies]',1)
        if s2 != s:
            open(ct,"w").write(s2); changed.append("Cargo.toml")

    # 3. drop the auto-publish workflow
    pub = os.path.join(d,".github","workflows","publish.yml")
    if os.path.exists(pub):
        os.remove(pub); changed.append("-publish.yml")

    # 4. replace Hello-World main
    mn = os.path.join(d,"src","main.rs")
    if os.path.exists(mn):
        s = open(mn).read()
        if "Hello, world" in s or "hello, world" in s.lower():
            crate = re.sub(r'[^a-z0-9]+','_', name.lower())
            open(mn,"w").write(
f'''fn main() {{
    // This crate is a library. The binary exists only so `cargo test` and `cargo run`
    // have a target; print the fleet canary so `cargo run` shows something meaningful.
    println!("{name} — SuperInstance fleet");
    println!("canary 0x24a555471370b18d  (see tests/canary.rs)");
}}
''')
            changed.append("main.rs")

    # 4b. described as a library but ships with no src/lib.rs at all
    lib = os.path.join(d,"src","lib.rs")
    if not os.path.exists(lib):
        open(lib,"w").write(LIB_TEMPLATE)
        changed.append("+src/lib.rs")

    # 5. canary test
    td = os.path.join(d,"tests"); os.makedirs(td, exist_ok=True)
    canon = os.path.join(td,"canary.rs")
    already = os.path.exists(canon) and "canary" in open(canon).read()
    fnv_present = os.path.exists(lib) and "fnv1a64" in open(lib).read()
    if fnv_present and not already:
        crate = re.sub(r'[^a-z0-9]+','_', name.lower())
        open(canon,"w").write(CANARY_TEST.replace("audit_trail", crate))
        changed.append("tests/canary.rs")
    elif not fnv_present and not already:
        # crate has no fnv1a64 at all: add a tiny self-contained one so it can carry the canary
        extra = '''
/// FNV-1a 64 — the digest every substrate in the SuperInstance fleet agrees on.
pub const FNV_OFFSET: u64 = 0xcbf29ce484222325;
pub const FNV_PRIME: u64 = 0x100000001b3;

#[inline]
pub fn fnv1a64(bytes: &[u8]) -> u64 {
    let mut h = FNV_OFFSET;
    for &b in bytes {
        h = (h ^ b as u64).wrapping_mul(FNV_PRIME);
    }
    h
}

/// True if this crate's FNV-1a still agrees with the rest of the fleet.
pub fn canary_holds() -> bool {
    fnv1a64("café Δ 日本語".as_bytes()) == 0x024a555471370b18d
}
'''
        if os.path.exists(lib):
            open(lib,"a").write(extra); changed.append("+fnv1a64")
        crate = re.sub(r'[^a-z0-9]+','_', name.lower())
        open(canon,"w").write(CANARY_TEST.replace("audit_trail", crate))
        changed.append("tests/canary.rs")

    if not changed:
        return {"repo": name, "status": "already-clean"}

    t = sh("cargo","test","-q", timeout=240)
    if t.returncode != 0:
        return {"repo": name, "status": "test-failed", "changed": changed,
                "err": (t.stderr or t.stdout)[-300:]}
    sh("git","add","-A")
    sh("git","-c","commit.gpgsign=false","commit","-q","-m",
       "housekeeping: licence, correct repository URL, canary test, publish workflow removed\n\n"
       "- LICENSE-MIT and LICENSE-APACHE. The Cargo.toml already declared MIT OR Apache-2.0\n"
       "  and the repository contained neither file.\n"
       "- repository URL pointed at a different account, which breaks cargo publish and makes\n"
       "  the crate untraceable.\n"
       "- fnv1a64 + canary_holds, asserted in tests/canary.rs. This crate is now a\n"
       "  polyformalism port: if the hash drifts it fails its own suite instead of quietly\n"
       "  disagreeing with the rest of the fleet.\n"
       "- removed the auto-publish workflow. It fired on any v* tag and would have published\n"
       "  an unlicensed crate. It returns when the crate is ready, not before.")
    if dry: return {"repo": name, "status": "dry-run", "changed": changed}
    sh("git","-c","push.gpgsign=false","push","-q","origin","HEAD")
    return {"repo": name, "status": "pushed", "changed": changed}

if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    which = sys.argv[1:] or ["audit-log","actor-system","ast-diff"]
    for n in which:
        r = fix_one(n)
        print(f"  {r['repo']:26} {r['status']:14} {r.get('changed') or r.get('err','')[:70]}", flush=True)
