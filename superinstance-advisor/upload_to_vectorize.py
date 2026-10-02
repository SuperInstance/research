"""
upload_to_vectorize.py — Push v3 corpus embeddings to Cloudflare Vectorize index.

Steps:
  1. Load full_canon_v3.npz + canon_meta_v3.json
  2. Create Vectorize index "quilt-canon-v3" (1024d, cosine) if not exists
  3. Upsert all vectors with rich metadata (model, ts, content_hash, tags)
  4. Build cite-neighbor pre-computation: for each piece, find top-10 cosine neighbors
  5. Save neighbors to JSON + push to KV for fast API pull

Usage: 
  python3 upload_to_vectorize.py            # full upload
  python3 upload_to_vectorize.py --neighbors-only   # skip upload, only rebuild neighbors
"""

import json, time, urllib.request, os, sys
import numpy as np

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
VEC_INDEX_NAME = "quilt-canon-v3"
VEC_INDEX_DIM = 1024
VEC_METRIC = "cosine"
KV_NAMESPACE_ID = os.environ.get("CELL_WITNESS_KV_ID", "f1882454a316494ebd8b9a75fe7856df")

DATA_DIR = "/workspace/research/superinstance-advisor/data"
OUTPUT_NPZ = f"{DATA_DIR}/full_canon_v3.npz"
META_JSON = f"{DATA_DIR}/canon_meta_v3.json"
NEIGHBORS_JSON = f"{DATA_DIR}/cite_neighbors_v3.json"


def cf_request(path, method="GET", body=None):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}{path}"
    headers = {
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 409 and "exists" in str(e):
                return {"result": {"name": VEC_INDEX_NAME, "already_exists": True}}
            if e.code in (429, 503) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            try:
                err_body = e.read().decode()
            except: err_body = ""
            return {"errors": [{"code": e.code, "message": err_body[:200]}]}
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return {"errors": [{"code": "exc", "message": str(e)}]}


def create_index_if_needed():
    print(f"=== Creating/checking Vectorize index '{VEC_INDEX_NAME}' ===")
    res = cf_request("/vectorize/indexes")
    if isinstance(res, dict) and "result" in res:
        existing = res.get("result", [])
        if any(idx["name"] == VEC_INDEX_NAME for idx in existing):
            print(f"  ✓ Index already exists")
            return True
    body = {
        "name": VEC_INDEX_NAME,
        "config": {"dimensions": VEC_INDEX_DIM, "metric": VEC_METRIC},
        "description": "Quilt canon v3 — bge-large-en-v1.5 (1024d), with rich metadata for enhanced API pulls",
    }
    res = cf_request("/vectorize/indexes", method="POST", body=body)
    if res.get("errors"):
        print(f"  err: {res['errors']}")
        return False
    if res.get("result", {}).get("already_exists"):
        print(f"  ✓ Index already exists (409 race)")
        return True
    print(f"  ✓ Index created: {res.get('result', {}).get('name')}")
    return True


def upload_vectors(vectors):
    """vectors = list of {id, values, metadata}"""
    print(f"=== Upserting {len(vectors)} vectors to {VEC_INDEX_NAME} ===")
    BATCH = 100
    n_ok, n_err = 0, 0
    for i in range(0, len(vectors), BATCH):
        batch = vectors[i:i+BATCH]
        body = {"vectors": batch}
        for attempt in range(3):
            res = cf_request(f"/vectorize/indexes/{VEC_INDEX_NAME}/upsert", method="POST", body=body)
            if not res.get("errors"):
                n_ok += len(batch)
                break
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            n_err += len(batch)
            print(f"  batch {i//BATCH}: err {res.get('errors', [{}])[0].get('message', '?')[:80]}")
        if (i // BATCH) % 10 == 0:
            print(f"  ... {n_ok}/{len(vectors)} uploaded")
    print(f"  ✓ {n_ok}/{len(vectors)} upserted, {n_err} errors")


def compute_neighbors(embs, tags, top_k=10):
    """For each embedding, compute top-k cosine neighbors."""
    print(f"=== Computing top-{top_k} cosine neighbors for {len(embs)} pieces ===")
    embs = np.array(embs, dtype=np.float32)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs_norm = embs / np.maximum(norms, 1e-12)
    # Batch matrix multiply for cosine similarity
    sim = embs_norm @ embs_norm.T
    # Top-k + 1 (since self-similarity = 1)
    idx = np.argpartition(-sim, kth=top_k + 1, axis=1)[:, :top_k + 1]
    
    neighbors = {}
    for i, tag in enumerate(tags):
        nbrs = []
        for j in idx[i]:
            if j == i:
                continue
            nbrs.append({
                "tag": tags[j],
                "cosine": float(sim[i, j]),
            })
        nbrs.sort(key=lambda x: -x["cosine"])
        neighbors[tag] = nbrs[:top_k]
    return neighbors


def main():
    print("=" * 70)
    print(f"  VECTORIZE UPLOAD + CITE-NEIGHBORS — {VEC_INDEX_NAME} ({VEC_INDEX_DIM}d)")
    print("=" * 70)

    # 1. Load
    if not os.path.exists(OUTPUT_NPZ) or not os.path.exists(META_JSON):
        print("ERROR: full_canon_v3.npz or canon_meta_v3.json missing")
        sys.exit(1)
    
    d = np.load(OUTPUT_NPZ, allow_pickle=True)
    embs = list(d["embeddings"])
    tags = list(d["tags"])
    paths = list(d["paths"])
    with open(META_JSON) as f:
        meta_list = json.load(f)
    print(f"\nLoaded {len(embs)} embeddings, dim={embs[0].shape if embs else 'empty'}")

    # 2. Create index
    if "--neighbors-only" not in sys.argv:
        if not create_index_if_needed():
            print("FATAL: could not create index")
            sys.exit(2)
    
    # 3. Build vectors with rich metadata
    if "--neighbors-only" not in sys.argv:
        vectors = []
        for i, (emb, tag, path, meta) in enumerate(zip(embs, tags, paths, meta_list)):
            vec_id = tag.replace(".", "_")[:48]  # vectorize id limits
            metadata = {
                "tag": tag[:256],
                "title": (meta.get("title", tag))[:256],
                "path": path[:256],
                "size": meta.get("size", 0),
                "embedding_model": meta.get("embedding_model", "unknown"),
                "embedding_dim": int(meta.get("embedding_dim", VEC_INDEX_DIM)),
                "embedded_at": float(meta.get("embedded_at", 0)),
                "content_hash": meta.get("content_hash", "")[:32],
                "tags_csv": ",".join(meta.get("tags", []))[:256],
            }
            # Vectorize expects flat values list
            vectors.append({
                "id": vec_id + (f"_{i}" if i > 0 else ""),
                "values": [float(x) for x in emb],
                "metadata": metadata,
            })
        upload_vectors(vectors)

    # 4. Compute neighbors
    neighbors = compute_neighbors(embs, tags)
    with open(NEIGHBORS_JSON, "w") as f:
        json.dump(neighbors, f, indent=2)
    print(f"  ✓ saved {len(neighbors)} neighbor entries to {NEIGHBORS_JSON}")
    
    # 5. Print top 5 most-cited (pieces with most incoming neighbors)
    incoming = {}
    for src, nbrs in neighbors.items():
        for n in nbrs:
            incoming[n["tag"]] = incoming.get(n["tag"], 0) + 1
    top5 = sorted(incoming.items(), key=lambda x: -x[1])[:5]
    print("\nTop 5 most-cited pieces (incoming neighbor count):")
    for tag, cnt in top5:
        print(f"  {cnt:3d} ← {tag}")


if __name__ == '__main__':
    main()
