// Emergent Port Constructions - A substrate-style tycoon prototype
// Principles:
//   - Cells are scars (each cell has memory)
//   - Modules form from adjacency patterns
//   - Tournament scoring = composite
//   - Frontal cortex fires only on critical moments

// ----- Substrate -----
const FNV_OFFSET = 0xcbf29ce484222325n;
const FNV_PRIME = 0x100000001b3n;
const FNV_CANARY = 0x24a555471370b18dn;

function fnv1a_64(s) {
    let h = FNV_OFFSET;
    const MASK = (1n << 64n) - 1n;
    for (let i = 0; i < s.length; i++) {
        h ^= BigInt(s.charCodeAt(i));
        h = (h * FNV_PRIME) & MASK;
    }
    return h;
}

function fnvHex(s) {
    return '0x' + fnv1a_64(s).toString(16).padStart(16, '0');
}

// ----- Cell Types -----
const CELL_TYPES = {
    empty: { glyph: '·', color: '#222', weight: 0, name: 'empty' },
    dock: { glyph: '⚓', color: '#4af', weight: 100, name: 'dock' },
    crane: { glyph: '🏗', color: '#fa4', weight: 80, name: 'crane' },
    warehouse: { glyph: '📦', color: '#af4', weight: 60, name: 'warehouse' },
    container_yard: { glyph: '░', color: '#f4a', weight: 40, name: 'container_yard' },
    customs: { glyph: '✦', color: '#a4f', weight: 30, name: 'customs' },
    fuel_depot: { glyph: '⛽', color: '#f44', weight: 50, name: 'fuel_depot' },
};

// ----- Module Patterns (3-cell adjacency shapes) -----
const MODULE_PATTERNS = [
    {
        name: 'Working Port',
        cells: ['dock', 'crane', 'warehouse'],
        shape: [[0, 0], [1, 0], [0, 1]],
        bonus: { throughput: 10, capacity: 5, value: 100 },
        description: 'A complete working port: ships dock, cranes load, warehouses store.',
    },
    {
        name: 'Fuel Station',
        cells: ['dock', 'fuel_depot'],
        shape: [[0, 0], [1, 0]],
        bonus: { throughput: 3, capacity: 0, value: 30 },
        description: 'Ships refuel efficiently.',
    },
    {
        name: 'Container Hub',
        cells: ['crane', 'container_yard', 'warehouse'],
        shape: [[0, 0], [1, 0], [0, 1]],
        bonus: { throughput: 6, capacity: 8, value: 60 },
        description: 'Containers flow quickly through.',
    },
    {
        name: 'Inspection Line',
        cells: ['dock', 'customs', 'warehouse'],
        shape: [[0, 0], [1, 0], [2, 0]],
        bonus: { throughput: 4, capacity: 4, value: 70 },
        description: 'Customs inspects incoming cargo.',
    },
    {
        name: 'Full Complex',
        cells: ['dock', 'crane', 'warehouse', 'fuel_depot'],
        shape: [[0, 0], [1, 0], [0, 1], [1, 1]],
        bonus: { throughput: 15, capacity: 12, value: 200 },
        description: 'A complete port complex. High throughput.',
    },
];

// ----- Game State -----
class PortGame {
    constructor() {
        this.gridSize = 16;
        this.grid = []; // 2D array: {type, hash, prev_hash}
        for (let y = 0; y < this.gridSize; y++) {
            const row = [];
            for (let x = 0; x < this.gridSize; x++) {
                row.push({
                    type: 'empty',
                    hash: null,
                    prev_hash: null,
                    placedAt: null,
                });
            }
            this.grid.push(row);
        }
        this.money = 10000;
        this.time = 0;
        this.modules = [];
        this.selectedType = 'dock';
        this.selectedCell = null;
        this.lastHint = 0;
        this.hintHistory = [];

        // Per-cell-type placement cost
        this.cost = {
            dock: 200,
            crane: 300,
            warehouse: 250,
            container_yard: 150,
            customs: 100,
            fuel_depot: 180,
        };
    }

    // Set cell type with prev_hash chain
    setCell(x, y, type) {
        if (x < 0 || x >= this.gridSize || y < 0 || y >= this.gridSize) return false;
        if (type !== 'empty' && this.money < this.cost[type]) return false;

        const cell = this.grid[y][x];

        if (type !== 'empty') {
            this.money -= this.cost[type];
        }

        cell.type = type;
        const prevHash = this.getPrevHash(x, y);
        cell.prev_hash = prevHash;
        cell.placedAt = this.time;
        cell.hash = fnvHex(`${x},${y},${type},${prevHash}`);

        // Check for new modules
        this.detectModules();
        return true;
    }

    getPrevHash(x, y) {
        // Use top-of-grid as prev_hash
        if (y === 0) return '0xcbf29ce484222325';
        const prevCell = this.grid[y - 1][x];
        return prevCell.hash || '0xcbf29ce484222325';
    }

    // Detect modules in grid
    detectModules() {
        this.modules = [];
        for (const pattern of MODULE_PATTERNS) {
            for (let y = 0; y < this.gridSize; y++) {
                for (let x = 0; x < this.gridSize; x++) {
                    if (this.matchesPattern(x, y, pattern)) {
                        this.modules.push({
                            name: pattern.name,
                            origin: { x, y },
                            cells: pattern.cells,
                            bonus: pattern.bonus,
                            description: pattern.description,
                        });
                    }
                }
            }
        }
        // Dedupe
        const seen = new Set();
        this.modules = this.modules.filter(m => {
            const key = `${m.origin.x},${m.origin.y},${m.name}`;
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }

    matchesPattern(bx, by, pattern) {
        const { cells, shape } = pattern;
        for (let i = 0; i < cells.length; i++) {
            const [dx, dy] = shape[i];
            const cx = bx + dx;
            const cy = by + dy;
            if (cx < 0 || cx >= this.gridSize || cy < 0 || cy >= this.gridSize) return false;
            if (this.grid[cy][cx].type !== cells[i]) return false;
        }
        return true;
    }

    // Compute emergent metrics
    computeMetrics() {
        const m = { throughput: 0, capacity: 0, congestion: 0, value: 0 };

        // Modules contribute bonuses
        for (const mod of this.modules) {
            m.throughput += mod.bonus.throughput;
            m.capacity += mod.bonus.capacity;
            m.value += mod.bonus.value;
        }

        // Congestion: density of cells
        let placed = 0;
        for (const row of this.grid) {
            for (const cell of row) {
                if (cell.type !== 'empty') placed++;
            }
        }
        const density = placed / (this.gridSize * this.gridSize);
        m.congestion = Math.min(100, Math.round(density * 150));

        return m;
    }

    // Tournament score (substrate-style)
    tournamentScore() {
        const m = this.computeMetrics();
        // Integrity: average hash chain validity
        let validChain = 0;
        for (const row of this.grid) {
            for (const cell of row) {
                if (cell.hash) validChain++;
            }
        }
        const integrity = validChain / (this.gridSize * this.gridSize);

        // Diversity: variety of cell types
        const types = new Set();
        for (const row of this.grid) {
            for (const cell of row) {
                if (cell.type !== 'empty') types.add(cell.type);
            }
        }
        const diversity = types.size / 6; // 6 cell types

        // Accessibility: how connected the port is
        const accessibility = Math.min(1, this.modules.length / 5);

        const composite = Math.cbrt(integrity * diversity * accessibility);
        return {
            integrity: integrity.toFixed(3),
            diversity: diversity.toFixed(3),
            accessibility: accessibility.toFixed(3),
            composite: composite.toFixed(3),
        };
    }

    // Frontal cortex hint - only at critical moments
    hint() {
        const now = Date.now();
        if (now - this.lastHint < 5000) {
            return "Hint: only available every 5s (frontal cortex is sparse).";
        }
        this.lastHint = now;

        // Find best placement opportunity
        const m = this.computeMetrics();
        const score = this.tournamentScore();

        // Suggest the cell with highest potential module completion
        for (let i = 0; i < MODULE_PATTERNS.length; i++) {
            const pattern = MODULE_PATTERNS[i];
            const cells = pattern.cells;
            const shape = pattern.shape;

            for (let y = 0; y < this.gridSize; y++) {
                for (let x = 0; x < this.gridSize; x++) {
                    let missing = 0;
                    let missingCell = null;
                    for (let j = 0; j < cells.length; j++) {
                        const [dx, dy] = shape[j];
                        const cx = x + dx;
                        const cy = y + dy;
                        if (cx >= 0 && cx < this.gridSize && cy >= 0 && cy < this.gridSize) {
                            if (this.grid[cy][cx].type !== cells[j]) {
                                missing++;
                                missingCell = { x: cx, y: cy, type: cells[j] };
                            }
                        } else {
                            missing++;
                        }
                    }
                    if (missing === 1 && missingCell) {
                        return `Add a ${CELL_TYPES[missingCell.type].name} at (${missingCell.x}, ${missingCell.y}) to complete a "${pattern.name}" module (worth +${pattern.bonus.throughput} throughput).`;
                    }
                }
            }
        }

        // No obvious module opportunities
        if (this.modules.length === 0) {
            return `Start with a ${this.selectedType} (cost $${this.cost[this.selectedType]}). Modules form from complementary cell adjacencies.`;
        }

        return `Current: ${this.modules.length} modules, score ${score.composite}. Try varying cell types for better diversity.`;
    }

    // Save/load
    save() {
        localStorage.setItem('emergent_ports_save', JSON.stringify({
            grid: this.grid,
            money: this.money,
            time: this.time,
            selectedType: this.selectedType,
        }));
        return true;
    }

    load() {
        const data = localStorage.getItem('emergent_ports_save');
        if (data) {
            const d = JSON.parse(data);
            this.grid = d.grid;
            this.money = d.money;
            this.time = d.time;
            this.selectedType = d.selectedType;
            return true;
        }
        return false;
    }

    reset() {
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                this.grid[y][x] = {
                    type: 'empty', hash: null, prev_hash: null, placedAt: null,
                };
            }
        }
        this.money = 10000;
        this.time = 0;
        this.modules = [];
    }
}

// ----- Renderer -----
class PortRenderer {
    constructor(canvas, game) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.game = game;
        this.cellSize = canvas.width / game.gridSize;
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Background
        ctx.fillStyle = '#0a0a14';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Highlight module cells
        const moduleCells = new Set();
        for (const mod of this.game.modules) {
            // Not visualized for simplicity
        }

        // Draw grid
        for (let y = 0; y < this.game.gridSize; y++) {
            for (let x = 0; x < this.game.gridSize; x++) {
                const cell = this.game.grid[y][x];
                const type = CELL_TYPES[cell.type];

                // Background
                ctx.fillStyle = (x + y) % 2 === 0 ? '#0a0a14' : '#0e0e1c';
                ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);

                // Cell glyph
                if (cell.type !== 'empty') {
                    ctx.fillStyle = type.color;
                    ctx.font = `${this.cellSize * 0.7}px monospace`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(type.glyph,
                        x * this.cellSize + this.cellSize / 2,
                        y * this.cellSize + this.cellSize / 2);
                }

                // Selection highlight
                if (this.game.selectedCell &&
                    this.game.selectedCell.x === x &&
                    this.game.selectedCell.y === y) {
                    ctx.strokeStyle = '#ff4';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x * this.cellSize + 2, y * this.cellSize + 2,
                                  this.cellSize - 4, this.cellSize - 4);
                }

                // Module highlight (overlay)
                let inModule = false;
                for (const mod of this.game.modules) {
                    for (const [dx, dy] of [[0,0],[1,0],[0,1],[1,1]]) {
                        if (mod.origin.x + dx === x && mod.origin.y + dy === y) {
                            inModule = true;
                            break;
                        }
                    }
                    if (inModule) break;
                }
                if (inModule) {
                    ctx.strokeStyle = '#4af';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x * this.cellSize, y * this.cellSize,
                                  this.cellSize, this.cellSize);
                }

                // Grid lines
                ctx.strokeStyle = '#1a1a30';
                ctx.lineWidth = 0.5;
                ctx.strokeRect(x * this.cellSize, y * this.cellSize,
                              this.cellSize, this.cellSize);
            }
        }
    }
}

// ----- Main -----
window.addEventListener('load', () => {
    const game = new PortGame();
    const canvas = document.getElementById('port-grid');
    const renderer = new PortRenderer(canvas, game);

    // Render initial
    renderer.render();
    updateUI();

    // Canvas click
    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / renderer.cellSize);
        const y = Math.floor((e.clientY - rect.top) / renderer.cellSize);

        // If erase mode, clear
        if (game.selectedType === 'erase') {
            const prev = game.grid[y][x].type;
            if (prev !== 'empty') {
                game.money += Math.floor(game.cost[prev] * 0.5);
                game.setCell(x, y, 'empty');
                renderer.render();
                updateUI();
            }
            return;
        }

        // Otherwise place cell
        if (game.setCell(x, y, game.selectedType)) {
            game.selectedCell = { x, y };
            // Flash if module was formed
            const prevModules = game.modules.length;
            game.detectModules();
            const flash = document.getElementById('event-flash');
            flash.classList.add('flash');
            setTimeout(() => flash.classList.remove('flash'), 200);
            renderer.render();
            updateUI();
        }
    });

    // Cell type buttons
    document.querySelectorAll('.cell-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cell-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            game.selectedType = btn.dataset.type;
        });
    });
    document.querySelector('.cell-btn').classList.add('active');

    // Hint button
    document.getElementById('btn-hint').addEventListener('click', () => {
        const hint = game.hint();
        const box = document.getElementById('hint-box');
        box.textContent = hint;
        box.classList.remove('hidden');
    });

    // Save/load/reset
    document.getElementById('btn-save').addEventListener('click', () => {
        game.save();
        alert('Saved!');
    });
    document.getElementById('btn-load').addEventListener('click', () => {
        if (game.load()) {
            renderer.render();
            updateUI();
            alert('Loaded!');
        }
    });
    document.getElementById('btn-reset').addEventListener('click', () => {
        if (confirm('Reset port?')) {
            game.reset();
            renderer.render();
            updateUI();
        }
    });

    function updateUI() {
        const m = game.computeMetrics();
        const s = game.tournamentScore();
        document.getElementById('money').textContent = '$' + game.money;
        document.getElementById('time').textContent = game.time;
        document.getElementById('modules').textContent = game.modules.length;
        document.getElementById('throughput').textContent = m.throughput;
        document.getElementById('capacity').textContent = m.capacity;
        document.getElementById('congestion').textContent = m.congestion + '%';
        document.getElementById('value').textContent = m.value;
        document.getElementById('composite').textContent = s.composite;
        document.getElementById('integrity').textContent = s.integrity;
        document.getElementById('diversity').textContent = s.diversity;
        document.getElementById('accessibility').textContent = s.accessibility;

        const cellHashEl = document.getElementById('cell-hash');
        const prevHashEl = document.getElementById('prev-hash');
        if (game.selectedCell) {
            const cell = game.grid[game.selectedCell.y][game.selectedCell.x];
            cellHashEl.textContent = cell.hash || '—';
            prevHashEl.textContent = cell.prev_hash || '—';
        } else {
            cellHashEl.textContent = '—';
            prevHashEl.textContent = '—';
        }

        // Modules list
        const list = document.getElementById('modules-list');
        if (game.modules.length === 0) {
            list.innerHTML = '<li class="empty">No modules yet. Place cells to form them.</li>';
        } else {
            list.innerHTML = game.modules.map(m =>
                `<li><strong>${m.name}</strong> at (${m.origin.x}, ${m.origin.y}) +${m.bonus.throughput} thru, +${m.bonus.value} value</li>`
            ).join('');
        }
    }

    // Tick timer
    setInterval(() => {
        game.time++;
        updateUI();
    }, 1000);
});
