# Emergent Port Constructions — Prototype

A substrate-style tycoon game where players construct modular ports from composable cells.

## Concept

In cargo-line-tycoon, ports are not built as monolithic structures. They emerge from the player's placement of "port cells" — dock, crane, warehouse, container_yard, customs, fuel_depot — on a 16×16 grid. When complementary cells are adjacent, they auto-form **modules** (e.g. dock + crane + warehouse = working_port) with bonus metrics.

## Architecture (Substrate Doctrine)

- **Cells are scars**: every cell has a memory (placedAt timestamp)
- **FNV-1a 64-bit prev_hash chain**: each cell's hash depends on the cell above it (canary 0x24a555471370b18d)
- **Tournament scoring**: composite = ∛(integrity × diversity × accessibility)
- **Frontal cortex**: hint system fires only on critical moments (every 5s)
- **Polyformalism**: emergent modules show the principle that simple rules → complex systems

## How to Play

1. Click a cell in the grid (or use the buttons to select a cell type)
2. Click on the grid to place a cell (cost varies by type)
3. Place complementary cells adjacent to each other to form modules
4. Hit "Hint" for an occasional suggestion (frontal cortex pattern)
5. Save/load your port to localStorage
6. Reset to start over

## Files

- `emergent_ports.html` - Main page
- `emergent_ports.js` - Game logic (PortGame + PortRenderer)
- `style.css` - Cyberpunk dark theme

## Inspired by

- `/workspace/research/substrate-walker/` - same substrate architecture (Rust+WASM)
- The Cargo Line Tycoon game design (top idea from tycoon GAN: 32.0/40 score)
- The doctrine of **emergence from simple rules**

