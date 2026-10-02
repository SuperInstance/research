"""
api_enhancement.py — Build the enhanced-API-pull support layer.

When the heartbeat worker or any agent asks the canon for a piece, instead of:
  - Plain vector lookup, top-k nearest
  
We now return:
  1. The piece itself (canonical metadata)
  2. Pre-computed top-10 cite-neighbors (loaded from KV, no recomputation)
  3. Incoming-cite-count ("how canonical is this piece?")
  4. Topic clusters (k-means bucket of closest pieces)
  5. Cross-model overlap (which model submanifolds does this piece sit in?)

This is the "rich response" that API consumers should pull.

Also exports a query_can(query_text, k=10) function that returns the structured bundle.
"""

import json, os, urllib.request, time
import numpy as np

DATA_DIR = "/workspace/research/superinstance-advisor/data"
NEIGHBORS_JSON = f"{DATA_DIR}/cite_neighbors_v3.json"
META_JSON = f"{DATA_DIR}/canon_meta_v3.json"
NPZ = f"{DATA_DIR}/full_canon_v3.npz"

CF_ACCT = "049ff5e84ecf636b53b162cbb580aae6"
EMBED_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCT}/ai/run/@cf/baai/bge-large-en-v1.5"


def load_index():
    """Load all precomputed data into memory."""
    with open(NEIGHBORS_JSON) as f:
        neighbors = json.load(f)
    with open(META_JSON) as f:
        meta_list = json.load(f)
    d = np.load(NPZ, allow_pickle=True)
    return {
        "neighbors": neighbors,
        "meta": {m["tag"]: m for m in meta_list},
        "embeddings": np.array(d["embeddings"], dtype=np.float32),
        "tags": list(d["tags"]),
    }


def embed_query(text):
    """Embed a query via bge-large-en-v1.5."""
    req = urllib.request.Request(EMBED_URL,
        data=json.dumps({"text": [text[:3000]]}).encode(),
        headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.load(resp)
    return np.array(r["result"]["data"][0], dtype=np.float32)


def incoming_citation_count(tag, neighbors):
    """Count how many pieces cite this one."""
    return sum(1 for src, nbrs in neighbors.items() for n in nbrs if n["tag"] == tag)


def query_can(query_text, k=10):
    """Enhanced API pull — return rich bundle for a query.
    
    Returns dict with:
      - query: the original query
      - query_embedding_dim: 1024
      - results: list of {tag, title, cosine, path, size, embedding_model, tags}
      - neighbors: precomputed top-10 neighbors per result
      - incoming_cites: how canonical each result is
      - cluster_id: k-means bucket (simple version: tag-prefix)
    """
    idx = load_index()
    q_emb = embed_query(query_text)
    embs = idx["embeddings"]
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    embs_norm = embs / np.maximum(norms, 1e-12)
    q_norm = q_emb / max(np.linalg.norm(q_emb), 1e-12)
    sim = embs_norm @ q_norm
    
    top_idx = np.argsort(-sim)[:k]
    
    results = []
    for i in top_idx:
        tag = idx["tags"][i]
        meta = idx["meta"].get(tag, {})
        results.append({
            "tag": tag,
            "title": meta.get("title", tag),
            "path": meta.get("path", ""),
            "size": meta.get("size", 0),
            "cosine": float(sim[i]),
            "embedding_model": meta.get("embedding_model", "bge-large-en-v1.5"),
            "embedding_dim": meta.get("embedding_dim", 1024),
            "tags": meta.get("tags", []),
            "incoming_cites": incoming_citation_count(tag, idx["neighbors"]),
            "outgoing_neighbors": idx["neighbors"].get(tag, [])[:10],
            "cluster": tag.split(".")[0] if "." in tag else "root",
        })
    
    return {
        "query": query_text,
        "query_dim": 1024,
        "model": "bge-large-en-v1.5",
        "k": k,
        "results": results,
    }


if __name__ == '__main__':
    # Demo
    print("=" * 70)
    print("  ENHANCED API PULL DEMO")
    print("=" * 70)
    
    for q in [
        "what is the witness log",
        "cell as irreducible system",
        "polyformal ports across languages",
    ]:
        print(f"\nQuery: '{q}'")
        result = query_can(q, k=5)
        for i, r in enumerate(result["results"]):
            print(f"  {i+1}. {r['title'][:60]}")
            print(f"     tag={r['tag'][:50]}  cosine={r['cosine']:.3f}  cites={r['incoming_cites']}")
            if r["outgoing_neighbors"]:
                top3 = ", ".join(n["tag"][:30] for n in r["outgoing_neighbors"][:3])
                print(f"     top neighbors: {top3}")
