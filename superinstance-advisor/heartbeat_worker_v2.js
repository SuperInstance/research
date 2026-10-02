// a2a_worker.js — Quilt a2a-protocol on the edge
export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        if (url.pathname === "/") {
            return new Response("quilt-a2a worker. POST /register, GET /cells\n", { status: 200 });
        }
        return new Response("ok\n", { status: 200 });
    },
};
