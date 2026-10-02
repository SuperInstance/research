"""
fleet_visualizer.py
===================

Pulls the live a2a fleet state and renders an interactive HTML
visualization of the cell graph.

Shows:
- Each cell as a node
- Capabilities as tags
- Lineage as parent → child edges
- Role as color
- Load as size

Output: data/fleet_graph.html
"""

from __future__ import annotations
import sys, os, json, urllib.request, urllib.error
import base64

A2A = os.environ.get("A2A_URL", "https://quilt-a2a-v2.casey-digennaro.workers.dev")


def a2a_call(method: str, path: str, body: dict = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "fleet-visualizer/1.0",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{A2A}{path}",
        data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"err": str(e)[:80]}


def main():
    print("=" * 70)
    print("  FLEET VISUALIZER — pulling live a2a state")
    print("=" * 70)

    # Pull cells
    cells_data = a2a_call("GET", "/cells")
    cells = cells_data.get("cells", [])
    print(f"\n  cells: {len(cells)}")

    # Pull pending messages
    info = a2a_call("GET", "/")
    print(f"  messages_pending: {info.get('messages_pending', 0)}")

    # Count roles
    roles = {}
    for c in cells:
        r = c.get("role", "?")
        roles[r] = roles.get(r, 0) + 1
    print(f"  by role: {roles}")

    # Find lineage roots (cells with parent_id or children)
    children = {}
    for c in cells:
        pid = c.get("parent_id")
        if pid:
            children.setdefault(pid, []).append(c["cell_id"])

    # Build graph
    nodes = []
    edges = []
    for c in cells:
        nodes.append({
            "id": c["cell_id"],
            "role": c.get("role", "?"),
            "caps": c.get("capabilities", []),
            "load": c.get("load", 0),
            "last_seen": c.get("last_seen", 0),
            "parent_id": c.get("parent_id"),
            "children": children.get(c["cell_id"], []),
        })
        if c.get("parent_id"):
            edges.append({"from": c["parent_id"], "to": c["cell_id"], "type": "parent"})

    # Output HTML
    html = build_html(nodes, edges, info.get("messages_pending", 0))
    out_path = os.path.join(os.path.dirname(__file__), "data", "fleet_graph.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"\n  ✓ wrote {out_path} ({len(html):,} bytes)")


def build_html(nodes, edges, messages_pending):
    """Build interactive fleet graph HTML."""
    # Stats
    roles_count = {}
    for n in nodes:
        roles_count[n["role"]] = roles_count.get(n["role"], 0) + 1

    # Use D3 for force-directed graph (inline, no external deps)
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    roles_json = json.dumps(roles_count)
    messages = messages_pending

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Quilt Fleet — Live Cell Graph</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    margin: 0; padding: 0; background: #0a0e14; color: #c9d1d9;
  }}
  .header {{
    padding: 20px 30px; background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-bottom: 1px solid #30363d;
  }}
  .header h1 {{
    margin: 0 0 8px; font-size: 24px; font-weight: 600;
    color: #f0f6fc; letter-spacing: -0.02em;
  }}
  .header .meta {{ color: #8b949e; font-size: 13px; }}
  .stats {{
    display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap;
  }}
  .stat {{
    background: rgba(177,186,196,0.1); border: 1px solid #30363d;
    padding: 6px 14px; border-radius: 20px; font-size: 13px;
  }}
  .stat strong {{ color: #58a6ff; font-weight: 600; }}
  .legend {{
    padding: 16px 30px; background: #161b22; border-bottom: 1px solid #30363d;
    display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .graph-container {{
    width: 100%; height: calc(100vh - 180px); position: relative;
    background: radial-gradient(ellipse at center, #0d1117 0%, #010409 100%);
  }}
  svg {{ width: 100%; height: 100%; cursor: grab; }}
  svg:active {{ cursor: grabbing; }}
  .node {{
    cursor: pointer;
  }}
  .node circle {{ stroke: #30363d; stroke-width: 1.5; }}
  .node text {{
    fill: #c9d1d9; font-size: 10px; font-family: monospace;
    pointer-events: none;
  }}
  .edge {{ stroke: #30363d; stroke-width: 1; opacity: 0.4; }}
  .edge.parent {{ stroke: #58a6ff; stroke-dasharray: 3,3; opacity: 0.7; }}
  .tooltip {{
    position: absolute; background: #161b22; border: 1px solid #58a6ff;
    padding: 10px 14px; border-radius: 6px; pointer-events: none;
    font-size: 12px; max-width: 320px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    display: none; z-index: 10;
  }}
  .tooltip h3 {{ margin: 0 0 6px; color: #58a6ff; font-size: 14px; }}
  .tooltip .caps {{
    color: #8b949e; margin-top: 6px;
  }}
  .tooltip .cap {{
    display: inline-block; background: rgba(88,166,255,0.15);
    color: #58a6ff; padding: 2px 6px; border-radius: 4px;
    font-size: 11px; margin: 2px;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>Quilt Fleet — Live Cell Graph</h1>
  <div class="meta">a2a Worker v2 · Vectorize-backed semantic search · KV-backed registry</div>
  <div class="stats">
    <div class="stat"><strong>{len(nodes)}</strong> cells</div>
    <div class="stat"><strong>{len(edges)}</strong> lineage edges</div>
    <div class="stat"><strong>{messages}</strong> pending messages</div>
""" + "".join(f'<div class="stat"><strong>{roles_count.get(r,0)}</strong> {r}</div>'
                for r in sorted(roles_count.keys())) + """
  </div>
</div>
<div class="legend">
""" + "".join(f"""<div class="legend-item">
    <div class="legend-dot" style="background:{role_color(r)}"></div>
    <span>{r}</span>
  </div>""" for r in sorted(set(n['role'] for n in nodes))) + """
</div>
<div class="graph-container">
  <svg id="graph"></svg>
</div>
<div class="tooltip" id="tooltip"></div>

<script>
// === D3 force-directed graph (vanilla, no deps) ===

const ROLE_COLORS = {
  advisor: "#58a6ff",
  shaper: "#f78166",
  "test-runner": "#a5a5ff",
  ensemble: "#d2a8ff",
  polyformal: "#7ee787",
  test: "#8b949e",
  anon: "#484f58",
};

function roleColor(role) {{ return ROLE_COLORS[role] || ROLE_COLORS.anon; }}

const nodes = {nodes_json};
const edges = {edges_json};

const svg = document.getElementById("graph");
const tooltip = document.getElementById("tooltip");
const width = svg.clientWidth;
const height = svg.clientHeight;

// Set up SVG
const svgNS = "http://www.w3.org/2000/svg";
svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);

// Force simulation
const sim = {{ dt: 0, alpha: 1, alphaTarget: 0, alphaMin: 0.001,
                velocityDecay: 0.4, force: {{}} }};

const positions = {{}};
nodes.forEach(n => {{
  positions[n.id] = {{
    x: width / 2 + (Math.random() - 0.5) * 300,
    y: height / 2 + (Math.random() - 0.5) * 300,
    vx: 0, vy: 0,
  }};
}});

// Simple force layout
function step() {{
  // Repulsion
  for (let i = 0; i < nodes.length; i++) {{
    for (let j = i+1; j < nodes.length; j++) {{
      const a = nodes[i]; const b = nodes[j];
      const pa = positions[a.id]; const pb = positions[b.id];
      const dx = pa.x - pb.x; const dy = pa.y - pb.y;
      const d2 = dx*dx + dy*dy + 0.01;
      const d = Math.sqrt(d2);
      const f = 8000 / d2;
      const fx = (dx / d) * f;
      const fy = (dy / d) * f;
      pa.vx += fx; pa.vy += fy;
      pb.vx -= fx; pb.vy -= fy;
    }}
  }}
  // Spring (edges)
  edges.forEach(e => {{
    const pa = positions[e.from]; const pb = positions[e.to];
    if (!pa || !pb) return;
    const dx = pa.x - pb.x; const dy = pa.y - pb.y;
    const d = Math.sqrt(dx*dx + dy*dy);
    const target = 80;
    const f = (d - target) * 0.05;
    const fx = (dx / d) * f;
    const fy = (dy / d) * f;
    pa.vx -= fx; pa.vy -= fy;
    pb.vx += fx; pb.vy += fy;
  }});
  // Center pull
  nodes.forEach(n => {{
    const p = positions[n.id];
    p.vx += (width/2 - p.x) * 0.001;
    p.vy += (height/2 - p.y) * 0.001;
    // damping
    p.vx *= 0.85; p.vy *= 0.85;
    p.x += p.vx; p.y += p.vy;
  }});
}}

// Draw edges
const edgesG = document.createElementNS(svgNS, "g");
edges.forEach(e => {{
  const line = document.createElementNS(svgNS, "line");
  line.setAttribute("class", "edge " + (e.type || ""));
  edgesG.appendChild(line);
  line._from = e.from; line._to = e.to;
}});
svg.appendChild(edgesG);

// Draw nodes
const nodesG = document.createElementNS(svgNS, "g");
const nodeEls = {{}};
nodes.forEach(n => {{
  const g = document.createElementNS(svgNS, "g");
  g.setAttribute("class", "node");
  g.setAttribute("transform", `translate(0,0)`);
  const circle = document.createElementNS(svgNS, "circle");
  const r = 12 + (n.load || 0) * 8;
  circle.setAttribute("r", r);
  circle.setAttribute("fill", roleColor(n.role));
  circle.setAttribute("opacity", "0.85");
  g.appendChild(circle);
  const text = document.createElementNS(svgNS, "text");
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("dy", r + 12);
  text.textContent = n.id.slice(0, 14);
  g.appendChild(text);
  g.addEventListener("mouseenter", e => {{
    tooltip.style.display = "block";
    tooltip.innerHTML = `
      <h3>${{n.id}}</h3>
      <div>role: ${{n.role}}</div>
      <div>caps: <span class="caps">${{n.caps.map(c => `<span class="cap">${{c}}</span>`).join("")}}</span></div>
      <div>load: ${{(n.load || 0).toFixed(2)}}</div>
      ${{n.parent_id ? `<div>parent: ${{n.parent_id}}</div>` : ""}}
      ${{n.children.length ? `<div>children: ${{n.children.join(", ")}}</div>` : ""}}
    `;
  }});
  g.addEventListener("mousemove", e => {{
    tooltip.style.left = (e.pageX + 12) + "px";
    tooltip.style.top = (e.pageY + 12) + "px";
  }});
  g.addEventListener("mouseleave", e => {{
    tooltip.style.display = "none";
  }});
  nodesG.appendChild(g);
  nodeEls[n.id] = g;
}});
svg.appendChild(nodesG);

function tick() {{
  step();
  edges.forEach((e, i) => {{
    const line = edgesG.children[i];
    const pa = positions[e.from]; const pb = positions[e.to];
    if (pa && pb) {{
      line.setAttribute("x1", pa.x);
      line.setAttribute("y1", pa.y);
      line.setAttribute("x2", pb.x);
      line.setAttribute("y2", pb.y);
    }}
  }});
  nodes.forEach(n => {{
    const p = positions[n.id];
    const g = nodeEls[n.id];
    g.setAttribute("transform", `translate(${{p.x}},${{p.y}})`);
  }});
  requestAnimationFrame(tick);
}}
tick();
</script>
</body>
</html>
"""


def role_color(role):
    """Color per role."""
    return {
        "advisor": "#58a6ff",
        "shaper": "#f78166",
        "test-runner": "#a5a5ff",
        "ensemble": "#d2a8ff",
        "polyformal": "#7ee787",
        "test": "#8b949e",
        "anon": "#484f58",
    }.get(role, "#484f58")


if __name__ == "__main__":
    main()
