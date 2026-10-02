"""
cite_discoverer.py
===================

For each new canon piece, find the top-K existing canon papers it should cite
based on semantic similarity. Add the citations to front-matter.

This makes the canon self-citing: every new piece strengthens the graph
by citing its neighbors.
"""

from __future__ import annotations
import os, sys, json, argparse, glob, time
import urllib.request
import numpy as np


ACCT = "049ff5e84ecf636b53b162cbb580aae6"


def embed(text: str, token: str) -> list[float]:
    """Call Cloudflare AI to embed one string."""
    body = json.dumps({"text": [text[:2000]]}).encode()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-base-en-v1.5",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())["result"]["data"][0]
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    raise RuntimeError("embed failed")


def load_canon(path: str):
    data = np.load(path, allow_pickle=True)
    return list(data["tags"]), data["embeddings"]


def cosine_topk(q_vec: np.ndarray, emb: np.ndarray, k: int):
    q_n = q_vec / np.linalg.norm(q_vec)
    emb_n = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    scores = emb_n @ q_n
    top = np.argsort(-scores)[:k]
    return [(int(top[i]), float(scores[i])) for i in range(len(top))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--canon", default="/workspace/research/quilt-corpus/quilt_pieces_v3.npz")
    parser.add_argument("--dir", default="/workspace/research/superinstance-advisor/canon")
    parser.add_argument("--k", type=int, default=3, help="Top-K citations per piece")
    parser.add_argument("--threshold", type=float, default=0.70,
                        help="Min cosine to count as a citation")
    parser.add_argument("--new-prefix", default="auto-",
                        help="Only cite-discover pieces starting with this prefix")
    parser.add_argument("--token", default=os.environ.get("CLOUDFLARE_TOKEN"))
    args = parser.parse_args()

    if not args.token:
        print("ERROR: CLOUDFLARE_TOKEN required")
        sys.exit(1)

    print("=" * 60)
    print("rune-quilt · cite discoverer")
    print("=" * 60)

    tags, embeddings = load_canon(args.canon)
    print(f"Canon: {len(tags)} pieces")
    print(f"Threshold: {args.threshold}")
    print(f"K: {args.k}")
    print()

    # Find new pieces (in dir but not yet in canon)
    existing_tags = set(tags)
    new_files = sorted(glob.glob(f"{args.dir}/*.md"))
    to_cite = []
    for f in new_files:
        tag = os.path.basename(f)[:-3]
        if tag in existing_tags and not tag.startswith(args.new_prefix):
            continue
        to_cite.append((tag, f))

    print(f"Pieces to discover citations for: {len(to_cite)}")
    print()

    # Skip pieces that already have citations in front-matter
    citations_added = 0
    citations_skipped = 0

    for tag, f in to_cite:
        with open(f) as fp:
            text = fp.read()

        # Check existing front-matter
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end > 0:
                fm = text[:end]
                if "cites:" in fm:
                    citations_skipped += 1
                    continue

        # Extract body (after front-matter)
        body_start = text.find("\n# ")
        if body_start == -1:
            body_start = 0
        body = text[body_start:]
        title = tag

        # Embed body
        print(f"  embedding {tag[:50]}...")
        try:
            vec = np.array(embed(body[:1500], args.token))
        except Exception as e:
            print(f"    embed failed: {e}")
            continue

        # Find top-K
        hits = cosine_topk(vec, embeddings, args.k + 10)  # extra for self-filter

        # Filter: exclude self, exclude below threshold
        cited = []
        for idx, score in hits:
            if tags[idx] == tag:
                continue
            if score < args.threshold:
                continue
            cited.append((tags[idx], score))
            if len(cited) >= args.k:
                break

        if not cited:
            print(f"    no citations found (threshold={args.threshold})")
            continue

        # Add cites: front-matter
        cite_lines = "\n".join([f"  - {t}  # cosine={s:.3f}" for t, s in cited])

        if text.startswith("---"):
            end = text.find("\n---", 3)
            new_fm = text[:end] + "\ncites:\n" + cite_lines + text[end:]
        else:
            new_fm = "---\ntitle: " + title + "\ncites:\n" + cite_lines + "\n---\n\n" + text

        with open(f, "w") as fp:
            fp.write(new_fm)

        print(f"    +{len(cited)} citations")
        for t, s in cited:
            print(f"      {s:.3f}  {t[:50]}")
        citations_added += 1

    print()
    print("=" * 60)
    print(f"Pieces cited: {citations_added}")
    print(f"Pieces skipped (already cited): {citations_skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()
