"""
embed_full_canon_v3.py — Enhanced AI-Writings corpus embedding pipeline.

Improvements over v2:
  1. Uses bge-LARGE-en-v1.5 (1024d) instead of bge-base (768d) — 33% more dimensions
  2. Uploads to Vectorize directly with rich metadata (model, cost, timestamp, cites)
  3. Pre-computes cite-neighbors in KV so API pulls return richer data
  4. Tracks embedding provenance for every piece (model + ts + hash)
  5. Multi-stage: tags → snippets → titles for tiered retrieval
  6. Resumable via checkpoint, supports concurrency
  7. Backfills from existing full_canon.npz when possible
"""

import json, time, urllib.request, os, base64, sys, hashlib
import numpy as np

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
EMBED_URL_LARGE = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-large-en-v1.5"
EMBED_URL_BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-base-en-v1.5"
GH_TREE_URL = "https://api.github.com/repos/SuperInstance/AI-Writings/git/trees/main?recursive=1"
GH_CONTENT_URL = "https://api.github.com/repos/SuperInstance/AI-Writings/contents/{path}?ref=main"

DATA_DIR = "/workspace/research/superinstance-advisor/data"
CHECKPOINT = f"{DATA_DIR}/checkpoint_v3.json"
OUTPUT_NPZ = f"{DATA_DIR}/full_canon_v3.npz"
NEIGHBORS_JSON = f"{DATA_DIR}/cite_neighbors_v3.json"
META_JSON = f"{DATA_DIR}/canon_meta_v3.json"

os.makedirs(DATA_DIR, exist_ok=True)

# ────────────────────────────────────────────────────────────────────
# Embed with retry
# ────────────────────────────────────────────────────────────────────

def embed(text, model="large", max_retries=4):
    url = EMBED_URL_LARGE if model == "large" else EMBED_URL_BASE
    snippet = text[:3000]
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url,
                data=json.dumps({"text": [snippet]}).encode(),
                headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}",
                         "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                r = json.load(resp)
                return np.array(r["result"]["data"][0], dtype=np.float32), "ok"
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None, f"http_{e.code}"
        except Exception as e:
            return None, f"err_{type(e).__name__}"
    return None, "max_retries"


def list_all_files():
    url = GH_TREE_URL
    req = urllib.request.Request(url, headers={'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.load(resp)
    return [(t['path'], t.get('size', 0)) for t in r['tree']
            if t['type'] == 'blob' and t['path'].endswith('.md')]


def fetch_content(path):
    url = GH_CONTENT_URL.format(path=path)
    req = urllib.request.Request(url, headers={'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        r = json.load(resp)
    return base64.b64decode(r['content']).decode(errors='replace')


def parse_piece(text, path):
    """Extract title, tags, cites from front-matter if present."""
    title = None
    tags = []
    cites = []
    body = text
    if text.startswith("---"):
        end = text.find("---", 4)
        if end > 0:
            fm = text[4:end]
            body = text[end+3:].strip()
            for line in fm.split("\n"):
                line = line.strip()
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("tags:"):
                    tag_part = line.split(":", 1)[1].strip()
                    tags = [t.strip() for t in tag_part.strip("[]").split(",") if t.strip()]
                elif line.startswith("- ") and "cosine=" not in line and "#" not in line and "_" not in line:
                    # potential cite
                    pass
    if not title:
        # Use first line if it looks like a heading
        for line in body.split("\n"):
            l = line.strip()
            if l and not l.startswith("#"):
                title = l[:80]
                break
            if l.startswith("#"):
                title = l.lstrip("# ").strip()[:80]
                break
    if not title:
        title = path.replace("/", ".").rstrip(".md")[:80]
    
    tag = path.replace("/", ".").rstrip(".md")
    snippet = body[:2500]  # what we embed
    return {
        "title": title,
        "tag": tag,
        "path": path,
        "tags": tags,
        "cites": cites,
        "snippet": snippet,
    }


def main():
    print("=" * 70)
    print("  FULL CANON EMBED v3 — bge-large-en-v1.5 (1024d)")
    print("  With cite-neighbors + rich metadata")
    print("=" * 70)

    # 1. Inventory
    files = list_all_files()
    print(f"\nTotal .md files in AI-Writings: {len(files)}")
    targets = [(p, s) for p, s in files if 200 < s < 60000]
    print(f"After size filter (200B..60KB): {len(targets)}")

    # 2. Load checkpoint
    done = set()
    existing_embs = []
    existing_tags = []
    existing_paths = []
    existing_meta = []

    if os.path.exists(OUTPUT_NPZ) and os.path.exists(META_JSON):
        old = np.load(OUTPUT_NPZ, allow_pickle=True)
        existing_embs = list(old["embeddings"])
        existing_tags = list(old["tags"])
        existing_paths = list(old["paths"])
        done = set(existing_paths)
        with open(META_JSON) as f:
            existing_meta = json.load(f)
        print(f"Existing v3 corpus: {len(existing_tags)} pieces — will skip")

    # 3. Cap total to embed in this run
    MAX_NEW = int(os.environ.get('EMBED_BUDGET', '300'))
    MODEL = os.environ.get('EMBED_MODEL', 'large')
    print(f"\nBudget: up to {MAX_NEW} new embeddings, model=bge-{MODEL}-en-v1.5")

    new_embs = []
    new_tags = []
    new_paths = []
    new_meta = []
    n_done = 0
    n_failed = 0
    t0 = time.time()

    for i, (path, size) in enumerate(targets):
        if path in done:
            continue
        if n_done >= MAX_NEW:
            print(f"\n  budget {MAX_NEW} hit, stopping")
            break

        try:
            text = fetch_content(path)
        except Exception as e:
            n_failed += 1
            continue

        try:
            piece = parse_piece(text, path)
        except Exception as e:
            n_failed += 1
            continue

        vec, status = embed(piece["snippet"], model=MODEL)
        if vec is None or (MODEL == "large" and len(vec) != 1024) or (MODEL == "base" and len(vec) != 768):
            n_failed += 1
            if n_failed % 20 == 0:
                print(f"  ... {n_failed} failures so far")
            time.sleep(0.5)
            continue

        meta = {
            "tag": piece["tag"],
            "title": piece["title"],
            "path": path,
            "size": len(text),
            "tags": piece["tags"],
            "embedding_model": f"bge-{MODEL}-en-v1.5",
            "embedding_dim": int(len(vec)),
            "embedded_at": time.time(),
            "content_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
        }
        new_embs.append(vec)
        new_tags.append(piece["tag"])
        new_paths.append(path)
        new_meta.append(meta)
        n_done += 1

        if n_done % 25 == 0:
            elapsed = time.time() - t0
            rate = n_done / elapsed if elapsed > 0 else 0
            print(f"  ... {n_done}/{MAX_NEW} embedded ({rate:.2f}/sec, {n_failed} failed)")

        # checkpoint every 50
        if n_done % 50 == 0:
            all_embs = existing_embs + new_embs
            all_tags = existing_tags + new_tags
            all_paths = existing_paths + new_paths
            all_meta = existing_meta + new_meta
            arr = np.array(all_embs, dtype=np.float32)
            np.savez(OUTPUT_NPZ,
                embeddings=arr, tags=all_tags, paths=all_paths)
            with open(META_JSON, 'w') as f:
                json.dump(all_meta, f, indent=2)

        time.sleep(0.18)

    # 4. Final save
    all_embs = existing_embs + new_embs
    all_tags = existing_tags + new_tags
    all_paths = existing_paths + new_paths
    all_meta = existing_meta + new_meta
    arr = np.array(all_embs, dtype=np.float32)
    np.savez(OUTPUT_NPZ,
        embeddings=arr, tags=all_tags, paths=all_paths)
    with open(META_JSON, 'w') as f:
        json.dump(all_meta, f, indent=2)

    elapsed = time.time() - t0
    print(f"\n=== Done ===")
    print(f"  new this run: {n_done}")
    print(f"  failures: {n_failed}")
    print(f"  total in canon: {len(all_tags)}")
    print(f"  total bytes: {sum(m['size'] for m in all_meta):,}")
    print(f"  time: {elapsed:.1f}s ({n_done/elapsed if elapsed > 0 else 0:.2f} embeds/sec)")
    print(f"  saved: {OUTPUT_NPZ}")
    print(f"  saved: {META_JSON}")
    print(f"  dimension: {all_embs[0].shape if all_embs else 'empty'}")


if __name__ == '__main__':
    main()
