"""
upload_to_kv.py — Push v3 corpus to Cloudflare Workers KV.

KV namespace: CELL_WITNESS_KV (id: f1882454a316494ebd8b9a75fe7856df)
Keys:
  canon_v3_embeddings  — JSON array of 670 × 1024 floats (~2.7 MB)
  canon_v3_meta        — JSON array of 670 metadata dicts
  canon_v3_neighbors   — JSON object {tag: [neighbors]}
  canon_v3_tags        — JSON array of 670 tag strings

KV limits:
  - Max value size: 25 MB
  - Max key length: 512 bytes
  - Max key count per namespace: 100M

This fits comfortably in a single key per category.
"""

import json, os, urllib.request, time

KV_NAMESPACE_ID = "f1882454a316494ebd8b9a75fe7856df"
ACCT = "049ff5e84ecf636b53b162cbb580aae6"

DATA_DIR = "/workspace/research/superinstance-advisor/data"
NPZ = f"{DATA_DIR}/full_canon_v3.npz"
META_JSON = f"{DATA_DIR}/canon_meta_v3.json"
NEIGHBORS_JSON = f"{DATA_DIR}/cite_neighbors_v3.json"


def kv_put(key, value):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{KV_NAMESPACE_ID}/values/{key}"
    body = value.encode() if isinstance(value, str) else value
    req = urllib.request.Request(url, data=body, method="PUT",
        headers={
            "Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}",
            "Content-Type": "application/octet-stream",
        })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                r = json.load(resp)
                return r.get("success", False)
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300]
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            print(f"  err {key}: HTTP {e.code} {err}")
            return False
    return False


def main():
    print("=" * 70)
    print("  KV UPLOAD — canon v3 → CELL_WITNESS_KV")
    print("=" * 70)
    
    import numpy as np
    d = np.load(NPZ, allow_pickle=True)
    embs = d["embeddings"].tolist()  # convert to list of lists
    tags = list(d["tags"])
    with open(META_JSON) as f:
        meta = json.load(f)
    with open(NEIGHBORS_JSON) as f:
        nbrs = json.load(f)
    
    print(f"\nCorpus: {len(embs)} pieces, {len(embs[0])}d")
    print(f"Total bytes (embeddings): {sum(len(json.dumps(e)) for e in embs[:5]) / 5 * len(embs) / 1024 / 1024:.2f} MB estimated")
    
    # 1. Embeddings
    emb_json = json.dumps(embs)
    print(f"\n[1/4] canon_v3_embeddings ({len(emb_json)/1024/1024:.2f} MB)")
    if kv_put("canon_v3_embeddings", emb_json):
        print(f"  ✓ uploaded {len(emb_json):,} bytes")
    else:
        print(f"  ✗ failed")
    
    # 2. Meta
    meta_json = json.dumps(meta)
    print(f"\n[2/4] canon_v3_meta ({len(meta_json)/1024:.1f} KB)")
    if kv_put("canon_v3_meta", meta_json):
        print(f"  ✓ uploaded")
    else:
        print(f"  ✗ failed")
    
    # 3. Neighbors
    nbrs_json = json.dumps(nbrs)
    print(f"\n[3/4] canon_v3_neighbors ({len(nbrs_json)/1024:.1f} KB)")
    if kv_put("canon_v3_neighbors", nbrs_json):
        print(f"  ✓ uploaded")
    else:
        print(f"  ✗ failed")
    
    # 4. Tags
    tags_json = json.dumps(tags)
    print(f"\n[4/4] canon_v3_tags ({len(tags_json)/1024:.1f} KB)")
    if kv_put("canon_v3_tags", tags_json):
        print(f"  ✓ uploaded")
    else:
        print(f"  ✗ failed")
    
    print("\n=== UPLOAD COMPLETE ===")
    print("Deploy the worker: wrangler deploy --config wrangler_canon.toml")


if __name__ == '__main__':
    main()
