"""
canon_seeder.py — Seed the a2a-v3 worker with all canon pieces

Reads the local quilt_pieces_v3.npz file (tags + embeddings) and the corresponding
markdown files, then POSTs each to /canon-submit. The worker embeds via Workers AI
on its side (using bge-base-en-v1.5) and stores under canon:embed:<tag>.

We can also POST the local embedding directly (set "vector" field) if it's the same
768d shape. Otherwise let the worker re-embed.
"""
import os, sys, json, glob, time
import urllib.request
import numpy as np

CANON_NPZ = "/workspace/research/quilt-corpus/quilt_pieces_v3.npz"
CANON_DIR = "/workspace/research/superinstance-advisor/canon"
WORKER_URL = "https://a2a-v3.superinstance.dev/canon-submit"


def post_piece(tag: str, title: str, text: str):
    body = json.dumps({
        "tag": tag,
        "title": title,
        "text": text[:1500],
    }).encode()
    req = urllib.request.Request(
        WORKER_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "canon-seeder/1.0",
        },
        method="POST",
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"ok": False, "err": f"HTTP {e.code}: {e.read().decode()[:200]}"}
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return {"ok": False, "err": "max retries"}


def main():
    if not os.path.exists(CANON_NPZ):
        print(f"ERROR: {CANON_NPZ} not found")
        sys.exit(1)

    data = np.load(CANON_NPZ, allow_pickle=True)
    tags = list(data["tags"])
    print(f"Loaded {len(tags)} pieces from {CANON_NPZ}")

    seeded = 0
    failed = 0
    for tag in tags:
        # Skip if no markdown body
        md = os.path.join(CANON_DIR, f"{tag}.md")
        if not os.path.exists(md):
            # Try alternative paths
            alt = os.path.join(CANON_DIR, "shape", f"{tag.replace('shape/','')}.md")
            if os.path.exists(alt):
                md = alt
            else:
                print(f"  SKIP {tag}: no markdown file")
                continue

        with open(md) as f:
            text = f.read()
        # Strip front-matter for embedding
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end > 0:
                text = text[end + 4:]

        # Title from first # heading
        title = tag
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Skip meta/citation pieces without body text
        body = text.strip()
        if len(body) < 50:
            continue

        result = post_piece(tag, title, body)
        if result.get("ok"):
            seeded += 1
            print(f"  ✓ {tag[:50]:50}  dim={result.get('dim')}")
        else:
            failed += 1
            print(f"  ✗ {tag[:50]:50}  {result.get('err')}")

        time.sleep(0.3)  # rate-limit

    print()
    print(f"Done: {seeded} seeded, {failed} failed")


if __name__ == "__main__":
    main()
