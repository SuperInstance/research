# Quilt-Robotic-Arm---Gesture-Controlled — Porting Plan

**Source repo:** https://github.com/SuperInstance/Quilt-Robotic-Arm---Gesture-Controlled
**Size:** 2.6 MB · **Default branch:** Master · **Status:** Imported (push date 2025-05-18; mirror-create date 2026-09-15)
**Language:** None (it's a hardware project with mixed docs)

## What it is (upstream)

A college-style hardware project: a 4-link robotic arm (base + 2 links + end effector) controlled by a flex-sensor glove with an accelerometer. Pick-and-place. Real wiring diagrams in `assets/` and `designs/`. Source code in `src/`.

## What "Quilt-portable" means here

The Quilt substrate **already exists** for ESP32 microcontrollers: `quilt-esp32` is a no_std Rust runtime, ~3KB flash, sensors-as-cells, the spreadsheet becomes the firmware. The porting task is:

1. Wrap the glove sensors as **Quilt cells** (one cell per flex sensor + one for the IMU)
2. Wrap each joint motor as a **Quilt cell** (servo position is the cell value; PWM duty cycle is the EFFECT)
3. Define **typed LINKs** between sensor cells and joint cells (forward kinematics as a typed graph)
4. Make the glove→arm pipeline a **sheet**: the spreadsheet IS the controller
5. Add the witness chain (every position change is logged; replay possible)
6. Wrap the whole thing in `quilt-cordis` as a Cordis plugin (mountable in any Quilt runtime)

## Substrate mapping

| Hardware | Quilt cell | Opcodes |
|---|---|---|
| Flex sensor (per finger) | `cell(value=finger_bend, axes=(finger_index,), confidence=signal_quality)` | `BIND` per finger, `TICK` reads ADC |
| IMU (accelerometer) | `cell(value=orientation, axes=(x,y,z), confidence=signal_quality)` | `BIND` once, `TICK` reads I2C |
| Servo motor (per joint) | `cell(value=angle_degrees, axes=(joint_index,), confidence=)` | `EFFECT` sets PWM, `BIND` initial position |
| Glove→arm FK | `LINK(finger_cells, joint_cells, type='fk')` | `LINK` typed edges |
| End effector state | `cell(value=open|closed|holding, axes=())` | `BIND` state, `LINK` to grip servo |
| Whole pipeline | `Substrate(name='arm-glove-v1')` | `EXTEND(name, 'esp32', semantics)` |

## The 5+1 opcodes that actually run

```
BIND every sensor and actuator as a cell
LINK sensor cells → joint cells with FK type
EFFECT joint cells apply PWM when values cross thresholds
VIEW the whole sheet as a 2D spreadsheet (joint positions × time)
TICK at 50Hz (or whatever the servo loop demands)
FORGET to decommission (e.g., gripper state when object released)
```

## Why this is a good Quilt demo

- **Visible**: an LED matrix shows the cell values in real-time
- **Live**: the glove moves, the arm moves, the spreadsheet updates
- **Auditable**: the witness chain records every joint position change → can replay the demo
- **Polyformal**: same cell-graph describes the Python simulator, the ESP32 firmware, AND the documentation diagram
- **Portable to Quilt-DAW**: a MIDI control surface is the same shape — button cells, fader cells, LED feedback cells

## Implementation steps

| Step | Effort | What ships |
|---|---|---|
| 1. Inventory upstream code | 30 min | `src/` catalog — what runs where, what hardware, what protocols |
| 2. Define cell schema | 1-2 hr | Python dataclasses for sensor cells, joint cells, end-effector cell |
| 3. Wrap in `quilt-cordis` | 2-3 hr | `Cell.as_plugin()` and `Plugin.as_cell()` for the arm; mountable in any Cordis runtime |
| 4. Forward kinematics as LINKs | 2-3 hr | The typed FK function lives in the LINK; cells reference it |
| 5. Port to `quilt-esp32` | 4-6 hr | no_std Rust runtime on actual ESP32, ~3KB flash headroom for cells |
| 6. Witness chain | 1 hr | Every joint change → witness append (FNV-1a64 or similar) |
| 7. Simulator | 2 hr | Python simulator that uses the same cell schema; plays back recorded runs |
| 8. Documentation | 2 hr | The polyformalism comparison: same cell-graph in firmware, simulator, docs |

**Total: ~16-22 hours of work for a Quilt-portable arm demo.**

## API surface (the "subagent for APIs" you mentioned)

If you want a **separate subagent** to manage the API layer between glove and arm, the API surface is small:

```
# Read sensors (glove side)
GET  /cells?type=sensor
GET  /cells/<addr>
# Write actuators (arm side)
POST /cells/<addr>/effect  body={"value": <angle_degrees>}
# Subscribe (witness chain)
GET  /witness?since=<tick>
# FK query (graph)
GET  /graph?root=finger.1
```

The API server is ~50 lines of FastAPI (Python) or axum (Rust). It exposes the cell-graph as REST. The subagent's job: maintain this server, generate typed clients, write conformance tests.

## What you could ship next

The minimum viable Quilt-portable demo is steps 1-4. The "genius intermediate layer" version is steps 1-7 — the simulator + the firmware + the witness replay, all on the same cell-graph, all Quilt-shaped.

I'll wait for the green light before touching the actual repo. The plan above is the spec.

---

**Files to create in the repo:**
- `quilt/__init__.py` — cell schema
- `quilt/cells.py` — sensor + joint + end-effector cells
- `quilt/substrate.py` — `Substrate(name='arm-glove-v1')`
- `quilt/plugin.py` — `quilt-cordis` adapter
- `quilt/fk.py` — forward kinematics as typed LINKs
- `quilt/api.py` — FastAPI surface (the subagent's domain)
- `docs/QUILT_PORT.md` — what changed from upstream
- `examples/simulator.py` — Python simulator
- `examples/witness_replay.py` — replay a recorded run

All on the cell-graph. All portable. All auditable.
