/* SUPERINSTANCE — a twist engine.
   Four substrates, one law: layers + deliberate offset -> interference -> emergence.
   TWIST  two hex lattices, one rotation -> moire superlattice (measured, not asserted)
   FLOCK  the same birds under four collective nouns
   CHIRP  a phased array of twelve transducers: beam steering as a twist in time
   QUILT  a tempo-twisted cell grid; the ledger counts holes, b1 = E - V + C   */
"use strict";

const TAU = Math.PI * 2;
const canvas = document.getElementById("sea");
const ctx = canvas.getContext("2d");
const chartCv = document.getElementById("chart");
const chartCtx = chartCv.getContext("2d");
const metricsEl = document.getElementById("metrics");
const ctrlEl = document.getElementById("ctrl-body");
const doctrineEl = document.getElementById("doctrine");
const titleEl = document.getElementById("mode-title");
const subEl = document.getElementById("mode-sub");

let W = 0, H = 0, DPR = 1;
function resize() {
  DPR = Math.min(2, window.devicePixelRatio || 1);
  W = window.innerWidth; H = window.innerHeight;
  canvas.width = W * DPR; canvas.height = H * DPR;
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  const cw = chartCv.clientWidth || 252;
  chartCv.width = cw * DPR; chartCv.height = 72 * DPR;
  chartCtx.setTransform(DPR, 0, 0, DPR, 0, 0);
  if (MODES[state.mode] && MODES[state.mode].resize) MODES[state.mode].resize();
}
window.addEventListener("resize", resize);

/* ---------- shared helpers ---------- */
function lerp(a, b, t) { return a + (b - a) * t; }
function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

function makeSlider(label, min, max, step, get, set, fmt) {
  const wrap = document.createElement("div");
  wrap.className = "ctrl";
  const lab = document.createElement("label");
  const name = document.createElement("span"); name.textContent = label;
  const val = document.createElement("b");
  lab.append(name, val);
  const input = document.createElement("input");
  input.type = "range"; input.min = min; input.max = max; input.step = step;
  input.value = get();
  const show = () => { val.textContent = fmt ? fmt(get()) : get(); };
  input.addEventListener("input", () => { set(parseFloat(input.value)); show(); });
  show();
  wrap.append(lab, input);
  return wrap;
}
function makeButtons(options, get, set) {
  const wrap = document.createElement("div");
  wrap.className = "ctrl";
  const row = document.createElement("div"); row.className = "btnrow";
  const refresh = () => {
    row.querySelectorAll("button").forEach(b =>
      b.classList.toggle("active", b.dataset.k === get()));
  };
  for (const [k, label] of options) {
    const b = document.createElement("button");
    b.className = "fbtn"; b.dataset.k = k; b.textContent = label;
    b.addEventListener("click", () => { set(k); refresh(); });
    row.appendChild(b);
  }
  wrap.appendChild(row);
  refresh();
  return wrap;
}
function setMetrics(list) {
  metricsEl.innerHTML = "";
  for (const [k, v, cls] of list) {
    const row = document.createElement("div"); row.className = "metric";
    const ke = document.createElement("span"); ke.className = "k"; ke.textContent = k;
    const ve = document.createElement("span"); ve.className = "v" + (cls ? " " + cls : "");
    ve.textContent = v;
    row.append(ke, ve); metricsEl.appendChild(row);
  }
}
function chartAxes(label) {
  const w = chartCv.clientWidth, h = 72;
  chartCtx.clearRect(0, 0, w, h);
  chartCtx.strokeStyle = "rgba(237,228,211,.08)";
  chartCtx.lineWidth = 1;
  chartCtx.beginPath(); chartCtx.moveTo(0, h / 2 + .5); chartCtx.lineTo(w, h / 2 + .5); chartCtx.stroke();
  chartCtx.fillStyle = "#73909c";
  chartCtx.font = "8px ui-monospace, monospace";
  chartCtx.fillText(label, 6, 11);
}

/* ============================================================
   TWIST — two hex lattices, one rotation. The superlattice
   appears; the resonance curve is measured live, not asserted.
   ============================================================ */
const twist = {
  theta: 1.06, s: 11, curve: [], windows: [], flashes: [],
  base: null, R0: 430, dragging: false,
  doctrine: "no new atoms — <em>a new angle</em>. the property is in the twist.",
  title: "TWIST", sub: "two lattices, one deliberate misalignment",

  hex(s, R) {
    const pts = [], dy = s * Math.sin(Math.PI / 3);
    const nj = Math.ceil(R / dy) + 1, ni = Math.ceil(R / s) + 1;
    for (let j = -nj; j <= nj; j++) {
      const xo = (Math.abs(j) % 2) ? s / 2 : 0;
      for (let i = -ni; i <= ni; i++) {
        const x = i * s + xo, y = j * dy;
        if (x * x + y * y <= R * R) pts.push([x, y]);
      }
    }
    return pts;
  },
  hash(pts, eps) {
    const m = new Map();
    for (const p of pts) {
      const k = Math.floor(p[0] / eps) + "," + Math.floor(p[1] / eps);
      let a = m.get(k); if (!a) { a = []; m.set(k, a); }
      a.push(p);
    }
    return m;
  },
  near2(m, x, y, eps) {
    const cx = Math.floor(x / eps), cy = Math.floor(y / eps);
    let best = Infinity;
    for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) {
      const a = m.get((cx + i) + "," + (cy + j));
      if (!a) continue;
      for (const p of a) {
        const d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y);
        if (d < best) best = d;
      }
    }
    return best;
  },
  rotated(pts, th) {
    const c = Math.cos(th), s = Math.sin(th), out = new Array(pts.length);
    for (let i = 0; i < pts.length; i++)
      out[i] = [pts[i][0] * c - pts[i][1] * s, pts[i][0] * s + pts[i][1] * c];
    return out;
  },
  alignment(ptsA, ptsB, eps) {
    const m = this.hash(ptsA, eps), e2 = eps * eps;
    let hit = 0;
    for (const p of ptsB) if (this.near2(m, p[0], p[1], eps) < e2) hit++;
    return hit / ptsB.length;
  },
  init() {
    this.s = clamp(Math.min(W, H) / 72, 9, 15);
    this.R0 = Math.hypot(W, H) / 2 + this.s * 4;
    this.base = this.hex(this.s, this.R0);
    this.curve = [];
    const eps = this.s * 0.30;
    for (let i = 0; i <= 260; i++) {
      const th = lerp(0.15, 6.0, i / 260) * Math.PI / 180;
      this.curve.push([th, this.alignment(this.base, this.rotated(this.base, th), eps)]);
    }
    this.windows = [];
    for (let i = 2; i < this.curve.length - 2; i++) {
      const v = this.curve[i][1];
      if (v > 0.10 && v > this.curve[i - 1][1] && v > this.curve[i + 1][1] &&
          v > this.curve[i - 2][1] && v > this.curve[i + 2][1]) {
        const last = this.windows[this.windows.length - 1];
        if (!last || this.curve[i][0] - last[0] > 0.12 * Math.PI / 180)
          this.windows.push(this.curve[i]);
      }
    }
    this.flashes = [];
  },
  controls() {
    ctrlEl.appendChild(makeSlider(
      "TWIST THETA", 0.15, 6.0, 0.005,
      () => this.theta, v => { this.theta = v; },
      v => v.toFixed(3) + "°"));
    ctrlEl.appendChild(makeButtons(
      [["snap", "SNAP TO NEXT WINDOW"]],
      () => "",
      () => {
        const th = this.theta * Math.PI / 180;
        const next = this.windows.find(w => w[0] > th + 0.01);
        this.theta = (next ? next[0] : this.windows[0][0]) * 180 / Math.PI;
      }));
  },
  frame(dt, t) {
    const cx = W / 2, cy = H / 2;
    const s = this.s, th = this.theta * Math.PI / 180;
    const eps = s * 0.30;
    const A = this.base, B = this.rotated(A, th);
    const mA = this.hash(A, eps);
    const sig = s * 0.24, twoSig2 = 2 * sig * sig;

    ctx.fillStyle = "#0a1a24";
    ctx.fillRect(0, 0, W, H);

    ctx.save(); ctx.translate(cx, cy);
    ctx.globalCompositeOperation = "lighter";

    const dot = Math.max(1.8, s * 0.22);
    ctx.fillStyle = "rgba(70,224,192,.30)";
    for (const p of A) {
      ctx.fillRect(p[0] - dot / 2, p[1] - dot / 2, dot, dot);
    }
    ctx.fillStyle = "rgba(247,160,38,.34)";
    for (const p of B) {
      ctx.fillRect(p[0] - dot / 2, p[1] - dot / 2, dot, dot);
    }
    ctx.globalCompositeOperation = "source-over";

    if (!this.alignCache || this._cacheTheta !== this.theta || ((this.frameNo = (this.frameNo || 0) + 1) % 6 === 0)) {
      this._cacheTheta = this.theta;
      this.alignCache = new Float32Array(B.length);
      let S = 0, n = 0;
      for (let i = 0; i < B.length; i++) {
        const d2 = this.near2(mA, B[i][0], B[i][1], eps * 3);
        const al = Math.exp(-d2 / twoSig2);
        this.alignCache[i] = al;
        S += al; n++;
      }
      this.S = S / n;
    }
    for (let i = 0; i < B.length; i++) {
      if (this.alignCache[i] > 0.86 && Math.random() < 0.003)
        this.flashes.push({ x: B[i][0], y: B[i][1], life: 1 });
    }

    for (let i = this.flashes.length - 1; i >= 0; i--) {
      const f = this.flashes[i];
      f.life -= dt * 1.4;
      if (f.life <= 0) { this.flashes.splice(i, 1); continue; }
      ctx.strokeStyle = `rgba(247,160,38,${f.life * 0.8})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(f.x, f.y, 3 + (1 - f.life) * 14, 0, TAU);
      ctx.stroke();
    }
    ctx.restore();

    const lam = s / (2 * Math.sin(th / 2));
    this.lam = lam;
    const nearWin = this.windows.some(w => Math.abs(w[0] - th) < 0.03 * Math.PI / 180 * 6);
    this.inWindow = nearWin;

    if (!this._dragBound) {
      this._dragBound = true;
      let sx = 0, st0 = 0;
      canvas.addEventListener("pointerdown", e => {
        if (state.mode !== "twist") return;
        this.dragging = true; sx = e.clientX; st0 = this.theta;
      });
      window.addEventListener("pointermove", e => {
        if (!this.dragging) return;
        this.theta = clamp(st0 + (e.clientX - sx) * 0.008, 0.15, 6.0);
      });
      window.addEventListener("pointerup", () => { this.dragging = false; });
    }
  },
  chart() {
    const w = chartCv.clientWidth, h = 72;
    chartAxes("S(THETA) — ALIGNMENT, MEASURED");
    const x0 = 0.15 * Math.PI / 180, x1 = 6.0 * Math.PI / 180;
    chartCtx.beginPath();
    for (let i = 0; i < this.curve.length; i++) {
      const [th, v] = this.curve[i];
      const x = (th - x0) / (x1 - x0) * w;
      const y = h - 6 - v * (h - 18);
      i ? chartCtx.lineTo(x, y) : chartCtx.moveTo(x, y);
    }
    chartCtx.strokeStyle = "rgba(70,224,192,.75)"; chartCtx.lineWidth = 1.2; chartCtx.stroke();
    chartCtx.fillStyle = "rgba(247,160,38,.9)";
    for (const wp of this.windows) {
      const x = (wp[0] - x0) / (x1 - x0) * w;
      chartCtx.fillRect(x - 0.5, h - 6 - wp[1] * (h - 18) - 3, 1.5, 3);
    }
    const tx = (this.theta * Math.PI / 180 - x0) / (x1 - x0) * w;
    chartCtx.strokeStyle = "#f7a026"; chartCtx.lineWidth = 1.4;
    chartCtx.beginPath(); chartCtx.moveTo(tx, 0); chartCtx.lineTo(tx, h); chartCtx.stroke();
  },
  metrics() {
    return [
      ["TWIST", this.theta.toFixed(3) + "°", "hot"],
      ["MEAN REGISTRY", (this.S || 0).toFixed(4), ""],
      ["SUPERCELL LAMBDA", this.lam ? (this.lam / this.s).toFixed(1) + " cells" : "—", "sig"],
      ["MAGIC WINDOWS", String(this.windows.length), ""],
      ["IN A WINDOW", this.inWindow ? "YES — CORRELATED" : "no — plain grids", this.inWindow ? "hot" : ""],
    ];
  }
};

/* ============================================================
   FLOCK — same birds, four nouns. The word builds the group.
   ============================================================ */
const FICTIONS = {
  murmuration: {
    label: "MURMURATION", ali: 1.0, coh: 0.55, sep: 1.25, tgt: 0, vmax: 2.7,
    line: "seven neighbors. no plan. no architect."
  },
  pack: {
    label: "PACK", ali: 0.8, coh: 0.35, sep: 0.85, tgt: 1.6, vmax: 3.6,
    line: "pursuit. perimeter. the alpha question."
  },
  kennel: {
    label: "KENNEL", ali: 0.25, coh: 0.15, sep: 0.7, tgt: 0, vmax: 1.1,
    pen: true, line: "containment. feeding. waiting."
  },
  parliament: {
    label: "PARLIAMENT", ali: 0.9, coh: 1.3, sep: 0.6, tgt: 0, vmax: 0.9,
    ring: true, line: "the owl that speaks last has watched the longest."
  }
};
const flock = {
  birds: [], fiction: "murmuration", lureT: 0, polHist: [],
  doctrine: "the word <em>builds</em> the group. four nouns, same birds.",
  title: "FLOCK", sub: "relational rules only — no world-model anywhere",
  init() {
    this.birds = [];
    const n = Math.min(340, Math.floor(W * H / 5200));
    for (let i = 0; i < n; i++) {
      const a = Math.random() * TAU;
      this.birds.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: Math.cos(a), vy: Math.sin(a)
      });
    }
    this.grid = new Map();
  },
  resize() { if (state.mode === "flock") this.init(); },
  controls() {
    ctrlEl.appendChild(makeButtons(
      Object.keys(FICTIONS).map(k => [k, FICTIONS[k].label]),
      () => this.fiction,
      k => { this.fiction = k; }));
  },
  frame(dt, t) {
    const F = FICTIONS[this.fiction];
    this.lureT += dt * 0.35;
    const lx = W / 2 + Math.cos(this.lureT) * W * 0.3;
    const ly = H / 2 + Math.sin(this.lureT * 1.7) * H * 0.26;
    const cx = W / 2, cy = H / 2, penR = Math.min(W, H) * 0.26, ringR = Math.min(W, H) * 0.3;

    const cell = 46, grid = this.grid;
    grid.clear();
    const B = this.birds;
    for (let i = 0; i < B.length; i++) {
      const k = Math.floor(B[i].x / cell) + "," + Math.floor(B[i].y / cell);
      let a = grid.get(k); if (!a) { a = []; grid.set(k, a); }
      a.push(i);
    }

    ctx.fillStyle = "#0a1a24"; ctx.fillRect(0, 0, W, H);

    if (F.pen) {
      ctx.strokeStyle = "rgba(247,160,38,.35)"; ctx.setLineDash([4, 6]);
      ctx.beginPath(); ctx.arc(cx, cy, penR, 0, TAU); ctx.stroke();
      ctx.setLineDash([]);
    }
    if (F.tgt) {
      ctx.fillStyle = "rgba(247,160,38,.9)";
      ctx.beginPath(); ctx.arc(lx, ly, 4, 0, TAU); ctx.fill();
    }

    let svx = 0, svy = 0, spd = 0;
    const step = clamp(dt * 60, 0.5, 2);
    for (let i = 0; i < B.length; i++) {
      const b = B[i];
      const gx = Math.floor(b.x / cell), gy = Math.floor(b.y / cell);
      let nA = 0, ax = 0, ay = 0, px = 0, py = 0, sx = 0, sy = 0;
      for (let i2 = -1; i2 <= 1 && nA < 7; i2++) for (let j2 = -1; j2 <= 1 && nA < 7; j2++) {
        const arr = grid.get((gx + i2) + "," + (gy + j2));
        if (!arr) continue;
        for (const j of arr) {
          if (j === i || nA >= 7) continue;
          const o = B[j], dx = o.x - b.x, dy = o.y - b.y;
          const d2 = dx * dx + dy * dy;
          if (d2 > 46 * 46 || d2 < 1e-6) continue;
          nA++; ax += o.vx; ay += o.vy; px += o.x; py += o.y;
          const inv = 1 / d2; sx -= dx * inv; sy -= dy * inv;
        }
      }
      let fx = 0, fy = 0;
      if (nA > 0) {
        const al = Math.hypot(ax, ay) || 1;
        fx += (ax / al - b.vx / (Math.hypot(b.vx, b.vy) || 1)) * F.ali * 0.05;
        fy += (ay / al - b.vy / (Math.hypot(b.vx, b.vy) || 1)) * F.ali * 0.05;
        fx += ((px / nA - b.x)) * F.coh * 0.0016;
        fy += ((py / nA - b.y)) * F.coh * 0.0016;
        fx += sx * F.sep * 0.9; fy += sy * F.sep * 0.9;
      }
      if (F.tgt) { fx += (lx - b.x) * 0.00045 * F.tgt; fy += (ly - b.y) * 0.00045 * F.tgt; }
      if (F.pen) {
        const dx = cx - b.x, dy = cy - b.y, d = Math.hypot(dx, dy) || 1;
        if (d > penR) { fx += dx / d * 0.06; fy += dy / d * 0.06; }
        fx *= 0.985; fy *= 0.985;
      }
      if (F.ring) {
        const dx = b.x - cx, dy = b.y - cy, d = Math.hypot(dx, dy) || 1;
        const err = ringR - d;
        fx += dx / d * err * 0.0012 - dy / d * 0.012;
        fy += dy / d * err * 0.0012 + dx / d * 0.012;
      }
      b.vx += fx * step; b.vy += fy * step;
      const v = Math.hypot(b.vx, b.vy) || 1;
      const vc = clamp(v, F.vmax * 0.35, F.vmax);
      b.vx = b.vx / v * vc; b.vy = b.vy / v * vc;
      b.x += b.vx * step; b.y += b.vy * step;
      if (b.x < -8) b.x = W + 8; if (b.x > W + 8) b.x = -8;
      if (b.y < -8) b.y = H + 8; if (b.y > H + 8) b.y = -8;

      svx += b.vx / vc; svy += b.vy / vc; spd += vc;
      const ang = Math.atan2(b.vy, b.vx);
      ctx.strokeStyle = "rgba(70,224,192,.8)";
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.moveTo(b.x - Math.cos(ang) * 4, b.y - Math.sin(ang) * 4);
      ctx.lineTo(b.x + Math.cos(ang) * 4, b.y + Math.sin(ang) * 4);
      ctx.stroke();
    }
    const pol = Math.hypot(svx, svy) / B.length;
    this.polHist.push(pol); if (this.polHist.length > 220) this.polHist.shift();
    this.pol = pol; this.meanSpd = spd / B.length;
  },
  chart() {
    const w = chartCv.clientWidth, h = 72;
    chartAxes("POLARIZATION — |MEAN HEADING|");
    if (this.polHist.length < 2) return;
    chartCtx.beginPath();
    for (let i = 0; i < this.polHist.length; i++) {
      const x = i / 219 * w, y = h - 6 - this.polHist[i] * (h - 18);
      i ? chartCtx.lineTo(x, y) : chartCtx.moveTo(x, y);
    }
    chartCtx.strokeStyle = "rgba(247,160,38,.85)"; chartCtx.lineWidth = 1.2; chartCtx.stroke();
  },
  metrics() {
    const F = FICTIONS[this.fiction];
    return [
      ["FICTION", F.label, "hot"],
      ["BIRDS", String(this.birds.length), ""],
      ["MEAN SPEED", (this.meanSpd || 0).toFixed(2), ""],
      ["POLARIZATION", (this.pol || 0).toFixed(3), "sig"],
      ["RULE", F.line, ""]
    ];
  }
};

/* ============================================================
   CHIRP — twelve transducers, progressive phase twist = beam.
   The interference field is computed; contacts are found by it.
   ============================================================ */
const chirp = {
  twist: 0, auto: true, fish: [], log: [], heading: 0,
  doctrine: "the box rings. <em>listen in time</em> for what you cannot see in space.",
  title: "CHIRP", sub: "twelve transducers — resolution bought with bandwidth, position bought with time",
  N: 12, lambda: 26,
  init() {
    this.fish = [];
    for (let i = 0; i < 6; i++)
      this.fish.push({
        x: W * (0.15 + Math.random() * 0.7),
        y: H * (0.15 + Math.random() * 0.5),
        vx: (Math.random() - 0.5) * 0.25, vy: (Math.random() - 0.5) * 0.2,
        cool: 0, lastR: null, lastT: 0
      });
    this.log = [];
    this.off = document.createElement("canvas");
    this.frameCount = 0;
  },
  resize() { if (state.mode === "chirp") this.init(); },
  controls() {
    ctrlEl.appendChild(makeSlider(
      "PHASE TWIST / ELEMENT", -60, 60, 0.5,
      () => this.twist, v => { this.twist = v; this.auto = false; },
      v => v.toFixed(1) + "°"));
    ctrlEl.appendChild(makeButtons(
      [["scan", "AUTO-SWEEP"], ["hold", "HOLD BEAM"]],
      () => this.auto ? "scan" : "hold",
      k => { this.auto = (k === "scan"); }));
  },
  fieldAt(x, y, t, src) {
    const k = TAU / this.lambda;
    let re = 0, im = 0;
    const w = t * TAU * 0.9;
    const dphi = this.heading * Math.PI / 180;
    for (let n = 0; n < this.N; n++) {
      const dx = x - src[n][0], dy = y - src[n][1];
      const ph = k * Math.sqrt(dx * dx + dy * dy) - w + n * dphi;
      re += Math.cos(ph); im += Math.sin(ph);
    }
    return Math.sqrt(re * re + im * im) / this.N;
  },
  frame(dt, t) {
    if (!this.off) this.init();
    if (this.auto) this.heading = 52 * Math.sin(t * 0.22);
    this.twist = this.heading;

    const src = [];
    for (let n = 0; n < this.N; n++)
      src.push([lerp(W * 0.16, W * 0.84, n / (this.N - 1)), H * 0.94]);

    let st = Math.max(4, Math.round(Math.min(W, H) / 140));
    let gw = Math.ceil(W / st), gh = Math.ceil(H / st);
    while (gw * gh * this.N > 500000) { st += 1; gw = Math.ceil(W / st); gh = Math.ceil(H / st); }

    this.frameCount++;
    if (this.frameCount % 2 === 0 || this.off.width !== gw) {
      this.off.width = gw; this.off.height = gh;
      const octx = this.off.getContext("2d");
      const img = octx.createImageData(gw, gh);
      const d = img.data;
      const k = TAU / this.lambda, wv = t * TAU * 0.9;
      const dphi = this.heading * Math.PI / 180;
      for (let gy = 0; gy < gh; gy++) {
        const y = gy * st + st / 2;
        for (let gx = 0; gx < gw; gx++) {
          const x = gx * st + st / 2;
          let re = 0, im = 0;
          for (let n = 0; n < this.N; n++) {
            const dx = x - src[n][0], dy = y - src[n][1];
            const ph = k * Math.sqrt(dx * dx + dy * dy) - wv + n * dphi;
            re += Math.cos(ph); im += Math.sin(ph);
          }
          const I = Math.sqrt(re * re + im * im) / this.N;
          const v = Math.pow(I, 1.7);
          const o = (gy * gw + gx) * 4;
          d[o]     = Math.round(lerp(10, 247, Math.max(0, v - 0.35) * 1.6));
          d[o + 1] = Math.round(lerp(26, 190, v));
          d[o + 2] = Math.round(lerp(36, 120, v * v));
          d[o + 3] = 255;
        }
      }
      octx.putImageData(img, 0, 0);
    }
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(this.off, 0, 0, W, H);
    ctx.fillStyle = "#0a1a24";
    ctx.fillRect(0, H * 0.94 + 5, W, H - H * 0.94);

    for (const s of src) {
      ctx.fillStyle = "#f7a026";
      ctx.fillRect(s[0] - 2, s[1] - 3, 4, 6);
    }

    const arrayCx = (src[0][0] + src[this.N - 1][0]) / 2;
    for (const f of this.fish) {
      f.x += f.vx; f.y += f.vy;
      if (f.x < W * 0.08 || f.x > W * 0.92) f.vx *= -1;
      if (f.y < H * 0.1 || f.y > H * 0.62) f.vy *= -1;
      f.cool -= dt;
      const I = this.fieldAt(f.x, f.y, t, src);
      const r = Math.hypot(f.x - arrayCx, f.y - H * 0.94) / 40;
      if (I > 0.72 && f.cool <= 0) {
        f.cool = 2.2; f.flash = 1;
        const closure = (f.lastR !== null) ? (f.lastR - r) / Math.max(0.5, t - f.lastT) : null;
        this.log.unshift({
          r, closure,
          brg: Math.atan2(f.x - arrayCx, (H * 0.94 - f.y)) * 180 / Math.PI
        });
        if (this.log.length > 4) this.log.pop();
        f.lastR = r; f.lastT = t;
      }
      f.flash = Math.max(0, (f.flash || 0) - dt * 0.7);
      ctx.fillStyle = f.flash > 0 ? `rgba(247,160,38,${0.4 + f.flash * 0.6})` : "rgba(70,224,192,.85)";
      ctx.beginPath(); ctx.arc(f.x, f.y, f.flash > 0 ? 5.5 : 3.5, 0, TAU); ctx.fill();
      if (f.flash > 0) {
        ctx.strokeStyle = `rgba(247,160,38,${f.flash})`;
        ctx.beginPath(); ctx.arc(f.x, f.y, 6 + (1 - f.flash) * 22, 0, TAU); ctx.stroke();
      }
    }
    this.lastContact = this.log[0] || null;
  },
  chart() {
    const w = chartCv.clientWidth, h = 72;
    chartAxes("BEAM HEADING — DEG OFF BOW");
    const cx = w / 2, cy = h - 8, R = h * 0.72;
    chartCtx.strokeStyle = "rgba(237,228,211,.18)";
    chartCtx.beginPath(); chartCtx.arc(cx, cy, R, Math.PI, TAU); chartCtx.stroke();
    const a = -Math.PI / 2 + this.heading * Math.PI / 180 * 1.4;
    chartCtx.strokeStyle = "#f7a026"; chartCtx.lineWidth = 1.6;
    chartCtx.beginPath(); chartCtx.moveTo(cx, cy);
    chartCtx.lineTo(cx + Math.cos(a) * R * 0.92, cy + Math.sin(a) * R * 0.92);
    chartCtx.stroke();
    chartCtx.fillStyle = "#73909c"; chartCtx.font = "8px ui-monospace, monospace";
    chartCtx.fillText("-60", 8, h - 4); chartCtx.fillText("+60", w - 24, h - 4);
  },
  metrics() {
    const c = this.lastContact;
    return [
      ["TWIST / ELEMENT", this.heading.toFixed(1) + "°", "hot"],
      ["ELEMENTS", "12 TRANSDUCERS", ""],
      ["CONTACT RANGE", c ? c.r.toFixed(2) + " NM" : "—", "sig"],
      ["CONTACT BEARING", c ? c.brg.toFixed(1) + "°" : "—", ""],
      ["CLOSURE", c && c.closure !== null && c.closure !== undefined
        ? (c.closure > 0 ? "CLOSING " : "OPENING ") + Math.abs(c.closure).toFixed(2) + " KN"
        : "AWAITING SECOND PING", c && c.closure > 0 ? "hot" : ""]
    ];
  }
};

/* ============================================================
   QUILT — a tempo-twisted cell grid. Every cell a boolean snap.
   The ledger counts the holes: b1 = E - V + C.
   ============================================================ */
const quilt = {
  N: 24, delta: 0.06, K: 1.1, phi: null, w0: TAU * 0.42, fired: null,
  stepBack: false, hist: [], acc: 0,
  doctrine: "the pattern is not in any hook. <em>b1 = E − V + C</em> — the ledger counts the holes.",
  title: "QUILT", sub: "two sub-lattices twisted in tempo; the step-back is computed, live",
  init() {
    const n = this.N * this.N;
    this.phi = new Float64Array(n);
    this.fired = new Float64Array(n).fill(-99);
    for (let i = 0; i < n; i++) this.phi[i] = Math.random() * TAU;
    this.hist = [];
  },
  resize() { if (state.mode === "quilt") this.init(); },
  controls() {
    ctrlEl.appendChild(makeSlider(
      "TEMPO TWIST DELTA", 0, 0.4, 0.002,
      () => this.delta, v => { this.delta = v; },
      v => (v * 100).toFixed(1) + "%"));
    ctrlEl.appendChild(makeSlider(
      "COUPLING K", 0, 3, 0.02,
      () => this.K, v => { this.K = v; },
      v => v.toFixed(2)));
    ctrlEl.appendChild(makeButtons(
      [["zoom", "STEP BACK"]],
      () => "",
      () => { this.stepBack = !this.stepBack; }));
  },
  frame(dt, t) {
    const N = this.N, phi = this.phi, K = this.K, d = this.delta;
    const step = clamp(dt, 0.001, 0.05);
    const deltaPhi = new Float64Array(N * N);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const w = ((x + y) % 2 === 0) ? this.w0 : this.w0 * (1 + d);
      let cpl = 0;
      if (x > 0) cpl += Math.sin(phi[i - 1] - phi[i]);
      if (x < N - 1) cpl += Math.sin(phi[i + 1] - phi[i]);
      if (y > 0) cpl += Math.sin(phi[i - N] - phi[i]);
      if (y < N - 1) cpl += Math.sin(phi[i + N] - phi[i]);
      deltaPhi[i] = (w + K * cpl * 0.25) * step;
    }
    for (let i = 0; i < N * N; i++) {
      phi[i] += deltaPhi[i];
      if (phi[i] >= TAU) { phi[i] -= TAU; this.fired[i] = t; }
    }

    const Wc = 1.2;
    const active = new Int8Array(N * N);
    let V = 0;
    for (let i = 0; i < N * N; i++) if (t - this.fired[i] < Wc) { active[i] = 1; V++; }
    const parent = new Int32Array(N * N); for (let i = 0; i < N * N; i++) parent[i] = i;
    const find = (a) => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; } return a; };
    let E = 0;
    const edges = [];
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const i = y * N + x;
      if (!active[i]) continue;
      const tryLink = (j) => {
        if (active[j]) {
          E++; edges.push([i, j]);
          const ra = find(i), rb = find(j);
          if (ra !== rb) parent[ra] = rb;
        }
      };
      if (x < N - 1) tryLink(i + 1);
      if (y < N - 1) tryLink(i + N);
      if (x < N - 1 && y < N - 1) tryLink(i + N + 1);
      if (x > 0 && y < N - 1) tryLink(i + N - 1);
    }
    const roots = new Set();
    for (let i = 0; i < N * N; i++) if (active[i]) roots.add(find(i));
    const C = roots.size;
    const b1 = Math.max(0, E - V + C);
    this.acc += dt;
    if (this.acc > 0.12) { this.acc = 0; this.hist.push(b1); if (this.hist.length > 220) this.hist.shift(); }
    this.V = V; this.E = E; this.C = C; this.b1 = b1;

    ctx.fillStyle = "#0a1a24"; ctx.fillRect(0, 0, W, H);
    const size = Math.min(W, H) * (this.stepBack ? 0.52 : 0.78);
    const cs = size / N, ox = (W - size) / 2, oy = (H - size) / 2;

    ctx.strokeStyle = "rgba(247,160,38,.20)"; ctx.lineWidth = 1;
    for (const [a, b] of edges) {
      const ax = a % N, ay = (a / N) | 0, bx = b % N, by = (b / N) | 0;
      ctx.beginPath();
      ctx.moveTo(ox + (ax + 0.5) * cs, oy + (ay + 0.5) * cs);
      ctx.lineTo(ox + (bx + 0.5) * cs, oy + (by + 0.5) * cs);
      ctx.stroke();
    }
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const i = y * N + x;
      const ph = phi[i] / TAU;
      const age = t - this.fired[i];
      const flash = age < 0.5 ? 1 - age * 2 : 0;
      const g = Math.pow(ph, 3);
      const r = Math.round(lerp(lerp(14, 46, g), 247, flash));
      const gg = Math.round(lerp(lerp(38, 224, g), 160, flash));
      const b = Math.round(lerp(lerp(48, 192, g), 38, flash));
      ctx.fillStyle = `rgb(${r},${gg},${b})`;
      ctx.fillRect(ox + x * cs + 0.5, oy + y * cs + 0.5, cs - 1, cs - 1);
    }
  },
  chart() {
    const w = chartCv.clientWidth, h = 72;
    chartAxes("B1 OVER TIME — HOLES IN THE CO-FIRE GRAPH");
    if (this.hist.length < 2) return;
    const mx = Math.max(4, ...this.hist);
    chartCtx.beginPath();
    for (let i = 0; i < this.hist.length; i++) {
      const x = i / 219 * w, y = h - 6 - this.hist[i] / mx * (h - 18);
      i ? chartCtx.lineTo(x, y) : chartCtx.moveTo(x, y);
    }
    chartCtx.strokeStyle = "rgba(70,224,192,.85)"; chartCtx.lineWidth = 1.2; chartCtx.stroke();
  },
  metrics() {
    return [
      ["TEMPO TWIST", (this.delta * 100).toFixed(1) + "%", "hot"],
      ["V — SNAPS", String(this.V || 0), ""],
      ["E — RELATIONS", String(this.E || 0), ""],
      ["C — COMPONENTS", String(this.C || 0), ""],
      ["B1 — HOLES", String(this.b1 || 0), "sig"]
    ];
  }
};

/* ============================================================
   mode manager + boot
   ============================================================ */
const MODES = { twist, flock, chirp, quilt };
const state = { mode: "twist", t: 0 };

function setMode(name) {
  state.mode = name;
  document.querySelectorAll(".tab").forEach(b =>
    b.classList.toggle("active", b.dataset.mode === name));
  const M = MODES[name];
  titleEl.textContent = M.title;
  subEl.textContent = M.sub;
  doctrineEl.innerHTML = M.doctrine;
  ctrlEl.innerHTML = "";
  M.init();
  M.controls();
  try { history.replaceState(null, "", "?mode=" + name); } catch (e) {}
}
document.querySelectorAll(".tab").forEach(b =>
  b.addEventListener("click", () => setMode(b.dataset.mode)));

let last = performance.now(), railAcc = 0;
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  state.t += dt;
  const M = MODES[state.mode];
  M.frame(dt, state.t);
  railAcc += dt;
  if (railAcc > 0.14) { railAcc = 0; M.chart(); setMetrics(M.metrics()); }
  requestAnimationFrame(loop);
}

resize();
const q = new URLSearchParams(location.search).get("mode");
setMode(MODES[q] ? q : "twist");
requestAnimationFrame(loop);
