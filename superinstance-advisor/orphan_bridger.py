"""
orphan_bridger.py — Track K

For each orphan canon piece (no cites in or out), find top-K existing canon
pieces via cosine similarity, append as cites:, and re-submit to /canon-submit.

Goal: turn 22 orphans into 22 contributors. After this runs, b1 should
climb because each new edge tightens the citation graph.
"""
from __future__ import annotations
import os, sys, json, glob, time, re
import urllib.request
import numpy as np

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
CANON_NPZ = "/workspace/research/quilt-corpus/quilt_pieces_v3.npz"
CANON_DIR = "/workspace/research/superinstance-advisor/canon"
TAPS_DIR = "/workspace/research/superinstance-advisor/canon/taps"
WORKER_URL = "https://a2a-v3.superinstance.dev/canon-submit"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "orphan-bridger/1.0"})
    for _ in range(3):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            print(f"  retry: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def post(tag, title, body, cites):
    payload = json.dumps({"tag": tag, "title": title, "text": body[:1500], "cites": cites}).encode()
    req = urllib.request.Request(
        WORKER_URL, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "orphan-bridger/1.0"},
        method="POST",
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"ok": False, "err": f"HTTP {e.code}"}
        except Exception as e:
            print(f"  retry: {e}", file=sys.stderr)
            time.sleep(2)
    return {"ok": False, "err": "max retries"}


def main():
    print("=" * 60)
    print("rune-quilt · orphan bridger (Track K)")
    print("=" * 60)

    # Load local canon pieces + tags
    npz = np.load(CANON_NPZ, allow_pickle=True)
    tags = list(npz["tags"])
    embeddings = npz["embeddings"]
    print(f"Local canon: {len(tags)} pieces, {embeddings.shape[1]}d")

    # Fetch live canon list
    canon_list = fetch("https://a2a-v3.superinstance.dev/canon-list")
    if not canon_list:
        print("ERROR: couldn't fetch canon list")
        return
    live_tags = {p["tag"] for p in canon_list["pieces"]}
    with_cites = {p["tag"] for p in canon_list["pieces"] if p.get("cites")}
    orphans = sorted(live_tags - with_cites)
    print(f"Live canon: {len(live_tags)} pieces, {len(orphans)} orphans")

    # Read source bodies from local md files (skip synthetic ones we made)
    def find_body(tag):
        # Try canon dir first
        for path in [CANON_DIR, TAPS_DIR, os.path.join(CANON_DIR, "shape"), os.path.join(CANON_DIR, "anchor")]:
            f = os.path.join(path, f"{tag}.md") if not tag.startswith("shape/") and not tag.startswith("anchor/") else None
            if f and os.path.exists(f):
                return f
        # Try with subdir prefix
        for sub in ["shape", "anchor", "early", "meta", "essay", "paper", "agentic-genre", "time"]:
            f = os.path.join(CANON_DIR, sub, f"{tag.replace(sub + '/', '')}.md")
            if os.path.exists(f):
                return f
        return None

    # Bridge each orphan
    bridged = 0
    failed = 0
    for tag in orphans:
        body_file = find_body(tag)
        if not body_file:
            print(f"  ⚠ {tag} — no local file, skipping")
            continue

        with open(body_file) as fp:
            text = fp.read()
        body = text
        if body.startswith("---"):
            end = body.find("\n---", 3)
            if end > 0:
                body = body[end + 4:]
        title = tag
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Get embedding — prefer local
        if tag in tags:
            idx = tags.index(tag)
            vec = embeddings[idx]
        else:
            # Re-embed via Workers AI through the worker
            r = fetch(f"https://a2a-v3.superinstance.dev/canon-search?q={urllib.parse.quote(body[:200])}&k=1")
            if not r or not r.get("matches"):
                print(f"  ⚠ {tag} — no embedding found")
                continue
            # fall back to local NPZ by tag
            continue

        # Find top-K similar
        q = vec / np.linalg.norm(vec)
        emb_n = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        scores = emb_n @ q
        top = np.argsort(-scores)
        cited = []
        for i in top:
            t = tags[i]
            if t == tag:
                continue
            if t not in live_tags:
                continue
            if scores[i] < 0.6:
                continue
            cited.append((t, float(scores[i])))
            if len(cited) >= 3:
                break

        if not cited:
            print(f"  ⚠ {tag} — no candidates above threshold")
            continue

        cite_tags = [t for t, _ in cited]
        r = post(tag, title, body.strip(), cite_tags)
        if r.get("ok"):
            bridged += 1
            print(f"  ✓ {tag[:50]:50} → {[c[0][:25] + f'({c[1]:.2f})' for c in cited]}")
        else:
            failed += 1
            print(f"  ✗ {tag[:50]:50} — {r.get('err')}")
        time.sleep(0.3)

    print()
    print("=" * 60)
    print(f"Bridged: {bridged} · Failed: {failed}")
    print("=" * 60)

    # New b1
    b1 = fetch("https://a2a-v3.superinstance.dev/canon-b1")
    if b1:
        print()
        print(f"New b1: V={b1['V']}, E={b1['E']}, C={b1['C']}, b1={b1['b1']}")


if __name__ == "__main__":
    main()
