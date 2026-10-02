"""
REST API for the Countroller Quilt substrate.

Exposes the cell-graph as HTTP endpoints. The same endpoint shape works
against real Pico firmware (via a Pico-side server), against the Python
simulator (this implementation), and against any polyformal port that
implements the cell-graph.

Endpoints:
- GET  /cells                  — list all cells
- GET  /cells/<addr>           — view a single cell
- POST /cells/<addr>/effect    — apply an effect (bump counter, set color, etc.)
- GET  /witness                — read the witness chain
- GET  /graph                  — read the typed LINK graph
- POST /pattern                — activate a pattern (heart/if/pi/clear)

This API is what the subagent-managed REST layer exposes. Cloudflare
Workers is the recommended deployment; Python/Flask or FastAPI works
locally.

A real Pico implementation would replace the in-process simulator with
serial-over-USB reads + GPIO writes, but the endpoint contract stays
identical. That's the polyformalism payoff: clients don't care which
runtime backs the API.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from .patterns import HeartPattern, IfPattern, PiPattern

PATTERNS = {"heart": HeartPattern, "if": IfPattern, "pi": PiPattern}


class CountrollerAPI:
    """REST API wrapper around a CountrollerSimulator."""

    def __init__(self, simulator):
        self.sim = simulator

    def cells(self):
        """List all cells, indexed by address."""
        return {
            addr: {
                "value": cell.value,
                "axes": cell.axes,
                "confidence": cell.confidence,
            }
            for addr, cell in self.sim.substrate.cells.items()
        }

    def cell(self, addr: str):
        """Get one cell by address."""
        cell = self.sim.substrate.cells.get(addr)
        if cell is None:
            return None
        return {
            "value": cell.value,
            "axes": cell.axes,
            "confidence": cell.confidence,
        }

    def effect(self, addr: str, fn_str: str):
        """Apply a named effect to a cell.

        Supported fn_str values (safe subset — never eval arbitrary code):
        - "incr"   — increment by 1 (for counters)
        - "dec"    — for buttons: 0 → 1 (press)
        - "zero"   — clear value
        - "clear"  — LED off (0, 0, 0)
        """
        cell = self.sim.substrate.cells.get(addr)
        if cell is None:
            return None
        if fn_str == "incr":
            return self.sim.substrate.effect(addr, lambda v: v + 1)
        elif fn_str == "dec":
            return self.sim.substrate.effect(addr, lambda v: v + 1)
        elif fn_str == "zero":
            return self.sim.substrate.effect(addr, lambda v: 0)
        elif fn_str == "clear":
            return self.sim.substrate.effect(addr, lambda v: (0, 0, 0))
        return None

    def witness(self):
        return list(self.sim.substrate.witness)

    def graph(self):
        """Return the typed LINK graph."""
        return [
            {
                "source": link.source,
                "target": link.target,
                "edge_type": link.edge_type,
            }
            for link in self.sim.substrate.links
        ]

    def activate_pattern(self, name: str):
        if name == "clear":
            self.sim.clear_pattern()
            return {"cleared": True}
        pattern = PATTERNS.get(name.lower())
        if pattern is None:
            return None
        self.sim.activate_pattern(pattern)
        return {"pattern": pattern.name, "cells_lit": len(pattern.cells_with_color())}


# ---------------------------------------------------------------------------
# HTTP handler (stdlib only — no flask/fastapi dep)
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    api: CountrollerAPI = None  # set per-server

    def _send(self, code: int, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")
        if path == "/cells":
            return self._send(200, self.api.cells())
        if path.startswith("/cells/"):
            addr = path[len("/cells/"):]
            result = self.api.cell(addr)
            return self._send(200, result) if result else self._send(404, {"error": "not found"})
        if path == "/witness":
            return self._send(200, self.api.witness())
        if path == "/graph":
            return self._send(200, self.api.graph())
        self._send(404, {"error": "unknown endpoint"})

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/")
        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length).decode() if content_length else "{}"
        try:
            body = json.loads(body_raw)
        except json.JSONDecodeError:
            body = {}
        if path.startswith("/cells/") and path.endswith("/effect"):
            addr = path[len("/cells/"):-len("/effect")]
            fn = body.get("fn", "incr")
            result = self.api.effect(addr, fn)
            return self._send(200, {"result": result}) if result is not None else self._send(404, {"error": "not found"})
        if path == "/pattern":
            name = body.get("name", "clear")
            result = self.api.activate_pattern(name)
            return self._send(200, result) if result else self._send(404, {"error": "unknown pattern"})
        self._send(404, {"error": "unknown endpoint"})

    def log_message(self, format, *args):
        """Silence the default stderr log; the substrate's witness chain is the log."""
        pass


def serve(simulator, host: str = "127.0.0.1", port: int = 8765):
    """Start the API server with a bound simulator."""
    Handler.api = CountrollerAPI(simulator)
    server = HTTPServer((host, port), Handler)
    print(f"Quilt Countroller API on http://{host}:{port}")
    print(f"  GET  /cells, /cells/<addr>, /witness, /graph")
    print(f"  POST /cells/<addr>/effect, /pattern")
    server.serve_forever()


if __name__ == "__main__":
    from .simulator import CountrollerSimulator
    sim = CountrollerSimulator()
    serve(sim)
