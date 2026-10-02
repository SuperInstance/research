// canon_api_worker.js — Enhanced API pulls for the Quilt canon v3
//
// Loads canon from KV, embeds query via Workers AI, returns enriched bundle.
// "Enhanced API pulls" — query returns top-k pieces WITH neighbors, 
// incoming-cites, cluster, model attribution.

const CANON_VERSION = "v3";
const EMBED_MODEL = "@cf/baai/bge-large-en-v1.5";  // 1024d

// Load canon from KV (cached on first request)
let canonCache = null;

async function loadCanon(env) {
  if (canonCache) return canonCache;
  const [embKey, metaKey, nbrKey, tagsKey] = await Promise.all([
    env.CELL_WITNESS_KV.get(`canon_${CANON_VERSION}_embeddings`),
    env.CELL_WITNESS_KV.get(`canon_${CANON_VERSION}_meta`),
    env.CELL_WITNESS_KV.get(`canon_${CANON_VERSION}_neighbors`),
    env.CELL_WITNESS_KV.get(`canon_${CANON_VERSION}_tags`),
  ]);
  if (!embKey || !metaKey || !nbrKey || !tagsKey) {
    return null;  // not populated yet
  }
  canonCache = {
    embeddings: JSON.parse(embKey),
    meta: JSON.parse(metaKey),
    neighbors: JSON.parse(nbrKey),
    tags: JSON.parse(tagsKey),
  };
  return canonCache;
}

function cosineSim(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-12);
}

async function queryCanon(env, queryText, k = 10) {
  const canon = await loadCanon(env);
  if (!canon) {
    return { error: "canon_not_populated", hint: "Run upload_to_kv.py first" };
  }
  
  // Embed query
  const resp = await env.AI.run(EMBED_MODEL, { text: [queryText] });
  if (!resp?.data?.[0]) {
    return { error: "embed_failed" };
  }
  const qVec = resp.data[0];
  
  // Compute cosine with all
  const sims = canon.embeddings.map((v, i) => ({
    tag: canon.tags[i],
    idx: i,
    score: cosineSim(qVec, v),
  }));
  sims.sort((a, b) => b.score - a.score);
  const top = sims.slice(0, k);
  
  // Build enriched response
  const incomingCounts = {};
  for (const [src, nbrs] of Object.entries(canon.neighbors)) {
    for (const n of nbrs) {
      incomingCounts[n.tag] = (incomingCounts[n.tag] || 0) + 1;
    }
  }
  
  const results = top.map(({ tag, score, idx }) => {
    const meta = canon.meta[idx] || {};
    return {
      tag,
      title: meta.title || tag,
      path: meta.path || "",
      size: meta.size || 0,
      embedding_model: meta.embedding_model || "bge-large-en-v1.5",
      embedding_dim: meta.embedding_dim || 1024,
      cosine: score,
      tags: meta.tags || [],
      incoming_cites: incomingCounts[tag] || 0,
      outgoing_neighbors: (canon.neighbors[tag] || []).slice(0, 10),
      cluster: tag.split(".")[0] || "root",
    };
  });
  
  return {
    query: queryText,
    model: "bge-large-en-v1.5",
    dimension: 1024,
    corpus_size: canon.tags.length,
    k,
    results,
  };
}

async function handleApi(env, path, params) {
  if (path === "/api/canon-v3/query") {
    const q = params.get("q");
    const k = parseInt(params.get("k") || "10", 10);
    if (!q) return { error: "missing_q" };
    return await queryCanon(env, q, k);
  }
  if (path === "/api/canon-v3/neighbors") {
    const tag = params.get("tag");
    const canon = await loadCanon(env);
    if (!canon) return { error: "canon_not_populated" };
    return {
      tag,
      neighbors: (canon.neighbors[tag] || []).slice(0, 20),
      incoming_cites: Object.entries(canon.neighbors)
        .filter(([src, nbrs]) => nbrs.some(n => n.tag === tag))
        .length,
    };
  }
  if (path === "/api/canon-v3/info") {
    const canon = await loadCanon(env);
    if (!canon) return { error: "canon_not_populated" };
    return {
      version: CANON_VERSION,
      corpus_size: canon.tags.length,
      embedding_model: "bge-large-en-v1.5",
      dimension: 1024,
      top_clusters: getTopClusters(canon),
    };
  }
  return { error: "not_found" };
}

function getTopClusters(canon) {
  const counts = {};
  for (const tag of canon.tags) {
    const c = tag.split(".")[0];
    counts[c] = (counts[c] || 0) + 1;
  }
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([cluster, count]) => ({ cluster, count }));
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    try {
      const result = await handleApi(env, url.pathname, url.searchParams);
      return new Response(JSON.stringify(result, null, 2), {
        headers: { ...cors, "Content-Type": "application/json" },
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }
  },
  
  // Scheduled cron: every 6 hours, log canon stats
  async scheduled(event, env, ctx) {
    const canon = await loadCanon(env);
    if (canon) {
      console.log(`[canon-v3] corpus: ${canon.tags.length} pieces, dim=1024, model=bge-large-en-v1.5`);
    } else {
      console.log(`[canon-v3] corpus: not populated`);
    }
  },
};
