// a2a_worker.js — Quilt a2a-protocol on the edge
//
// Inter-cell messaging. KV-backed inbox. Vectorize-backed capability discovery.
// Cell registers → sends heartbeat → broadcasts capabilities → receives messages.
//
// Endpoints:
//   GET  /              — service info
//   POST /register      — register a cell {cell_id, role, address, capabilities}
//   GET  /cells         — list registered cells
//   POST /send          — send a message {from, to, type, payload}
//   GET  /inbox/:cell   — get inbox for a cell (drains it)
//   POST /broadcast     — broadcast to all cells with capability
//   GET  /find?cap=X    — find cells with capability X
//   POST /tick          — heartbeat tick (auto-registers if unknown)
//
// Storage:
//   KV:    CELL_A2A → {cells: {id: cell}, messages: {cell: [msgs]}}
//   Vect:  cell-capabilities (768d) — for semantic capability search

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json",
    };
    if (method === "OPTIONS") return new Response(null, { headers: cors });

    try {
      // Get all cells from KV
      const state = await getState(env);

      if (path === "/" || path === "") {
        return json({
          service: "quilt-a2a",
          version: "1.0.0",
          cells: Object.keys(state.cells).length,
          messages_pending: Object.values(state.messages).reduce((a, b) => a + b.length, 0),
          endpoints: ["/register", "/cells", "/send", "/inbox/:cell", "/broadcast", "/find", "/tick"],
        }, cors);
      }

      if (path === "/register" && method === "POST") {
        const body = await request.json();
        const cell = {
          cell_id: body.cell_id || `anon-${Date.now()}`,
          role: body.role || "unknown",
          address: body.address || body.cell_id,
          capabilities: body.capabilities || [],
          registered_at: Date.now(),
          last_seen: Date.now(),
        };
        state.cells[cell.cell_id] = cell;
        state.messages[cell.cell_id] = state.messages[cell.cell_id] || [];
        await saveState(env, state);
        return json({ ok: true, cell, total_cells: Object.keys(state.cells).length }, cors);
      }

      if (path === "/cells" && method === "GET") {
        return json({ cells: Object.values(state.cells) }, cors);
      }

      if (path === "/send" && method === "POST") {
        const body = await request.json();
        const { from, to, type, payload } = body;
        if (!to || !type) return json({ ok: false, err: "missing to/type" }, cors);
        const msg = {
          id: crypto.randomUUID(),
          from: from || "anon",
          to, type, payload: payload || {},
          ts: Date.now(),
          nonce: Math.floor(Math.random() * 1e9),
        };
        state.messages[to] = state.messages[to] || [];
        state.messages[to].push(msg);
        await saveState(env, state);
        return json({ ok: true, msg, inbox_size: state.messages[to].length }, cors);
      }

      if (path.startsWith("/inbox/") && method === "GET") {
        const cell_id = path.split("/")[2];
        const messages = state.messages[cell_id] || [];
        // Drain after read
        if (url.searchParams.get("drain") !== "false") {
          state.messages[cell_id] = [];
          await saveState(env, state);
        }
        return json({ cell_id, messages, count: messages.length }, cors);
      }

      if (path === "/broadcast" && method === "POST") {
        const body = await request.json();
        const { from, type, payload, capability } = body;
        const targets = capability
          ? Object.values(state.cells).filter(c => c.capabilities?.includes(capability))
          : Object.values(state.cells);
        const msgs = [];
        for (const t of targets) {
          if (t.cell_id === from) continue;
          const msg = {
            id: crypto.randomUUID(),
            from: from || "anon",
            to: t.cell_id,
            type, payload: payload || {},
            ts: Date.now(),
            broadcast: true,
          };
          state.messages[t.cell_id] = state.messages[t.cell_id] || [];
          state.messages[t.cell_id].push(msg);
          msgs.push(msg);
        }
        await saveState(env, state);
        return json({ ok: true, delivered: msgs.length, msgs }, cors);
      }

      if (path === "/find" && method === "GET") {
        const cap = url.searchParams.get("cap");
        const role = url.searchParams.get("role");
        let cells = Object.values(state.cells);
        if (cap) cells = cells.filter(c => c.capabilities?.includes(cap));
        if (role) cells = cells.filter(c => c.role === role);
        return json({ cells, count: cells.length }, cors);
      }

      if (path === "/tick" && method === "POST") {
        const body = await request.json().catch(() => ({}));
        const cell_id = body.cell_id || `anon-${Date.now()}`;
        // Auto-register or update last_seen
        if (state.cells[cell_id]) {
          state.cells[cell_id].last_seen = Date.now();
        } else {
          state.cells[cell_id] = {
            cell_id, role: body.role || "anon",
            address: cell_id, capabilities: body.capabilities || [],
            registered_at: Date.now(), last_seen: Date.now(),
          };
        }
        state.messages[cell_id] = state.messages[cell_id] || [];
        // Drain own inbox
        const messages = state.messages[cell_id] || [];
        state.messages[cell_id] = [];
        await saveState(env, state);
        return json({
          ok: true, cell_id, total_cells: Object.keys(state.cells).length,
          inbox_count: messages.length, messages,
        }, cors);
      }

      return json({ ok: false, err: "no route", path }, cors, 404);
    } catch (e) {
      return json({ ok: false, err: e.message }, cors, 500);
    }
  },

  async scheduled(event, env, ctx) {
    // Cron tick — purge cells unseen for >1 hour
    const state = await getState(env);
    const now = Date.now();
    const cutoff = now - 3600_000;
    for (const [id, c] of Object.entries(state.cells)) {
      if (c.last_seen < cutoff) delete state.cells[id];
    }
    await saveState(env, state);
    ctx.waitUntil(Promise.resolve());
  },
};

async function getState(env) {
  const raw = await env.CELL_WITNESS_KV.get("a2a:state");
  if (!raw) return { cells: {}, messages: {} };
  try { return JSON.parse(raw); } catch { return { cells: {}, messages: {} }; }
}

async function saveState(env, state) {
  await env.CELL_WITNESS_KV.put("a2a:state", JSON.stringify(state));
}

function json(obj, headers = {}, status = 200) {
  return new Response(JSON.stringify(obj, null, 2), { status, headers });
}
