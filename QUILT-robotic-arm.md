# QUILT — Robotic Arm as a cell-graph

This is the **Quilt projection layer** for the Gesture-Controlled
Robotic Arm. The original Python + hardware project is preserved (see
`UPSTREAM.md` and `QUILT_PORT.md` for the port plan); this document
shows how the same program becomes **visible as a cell-graph** using
the 5+1 opcodes.

Audience: applied engineers who know embedded systems / robotics / servo
control but not necessarily Quilt.

## What the cell-graph looks like

```
                         ┌────────────────────────────┐
                         │  cell:substrate           │
                         │  name=arm-glove-v1        │
                         │  axis=role                │
                         └────────────┬──────────────┘
                                     │ (typed: contains)
                                     ▼

   ┌──────────────────────────────────────────────────────┐
   │  GLOVE INPUT CELLS (5)                               │
   │                                                      │
┌──▼─────────┐ ┌──────────────┐ ┌──────────┐ ┌───────┐ ┌──▼────────────┐
│cell:finger1│ │cell:finger2  │ │cell:fg3  │ │cell: │ │cell:imu_orient│
│value=bend  │ │value=bend    │ │value=... │ │...    │ │value=(x,y,z)  │
│axes=(idx,) │ │axes=(idx,)   │ │          │ │       │ │axes=(x,y,z,)  │
│link=joint1 │ │link=joint2   │ │link=...  │ │...    │ │link=base_rot  │
└────────────┘ └──────────────┘ └──────────┘ └───────┘ └───────────────┘

   ┌──────────────────────────────────────────────────────┐
   │  ARM JOINT CELLS (4) + END EFFECTOR (1)             │
   │                                                      │
┌──▼─────────┐ ┌──────────────┐ ┌──────────┐ ┌───────┐ ┌──▼────────────┐
│cell:base  │ │cell:shoulder │ │cell:elbow│ │cell: │ │cell:end_eff    │
│value=angle│ │value=angle   │ │value=... │ │wrist │ │value=open|    │
│axes=(idx,)│ │axes=(idx,)   │ │          │ │      │ │       holding │
│link=glove │ │link=finger1  │ │link=...  │ │...   │ │link=grip_servo │
└────────────┘ └──────────────┘ └──────────┘ └───────┘ └───────────────┘
```

**Total: ~10 cells.** Small enough for a hello-world, complex enough to
demonstrate forward kinematics as typed links.

## The 5+1 opcodes in action

Every hardware action maps to a Quilt opcode:

| Hardware action | Quilt opcode | Cell(s) affected |
|---|---|---|
| Glove power on | `BIND` | All 5 input cells |
| Flex sensor sample | `EFFECT(finger_X, lambda v: bend_value)` | Bend value updates |
| IMU read | `EFFECT(imu_orient, lambda v: (x, y, z))` | Orientation updates |
| Servo position update | `EFFECT(shoulder, lambda v: angle)` | Joint angle updates |
| Gripper action | `EFFECT(end_effector, lambda v: open|holding|closed)` | End effector state updates |
| Forward kinematics | `VIEW(finger_X) → LINK (typed fk) → EFFECT(shoulder, ...)` | Computed joint angles |
| Control loop tick | `TICK(dt=0.02)` | 50Hz loop advances |

## The cell subtypes

| Cell | Type | Lifecycle |
|---|---|---|
| `cell:finger_1` to `cell:finger_5` | Sensor (5) | `BIND` once, `EFFECT` per sample |
| `cell:imu_orient` | Sensor (1) | `BIND` once, `EFFECT` per sample |
| `cell:base`, `cell:shoulder`, `cell:elbow`, `cell:wrist` | Actuator (4) | `BIND` once, `EFFECT` per angle update |
| `cell:end_effector` | Actuator (1) | `BIND` once, `EFFECT` per state change |

## The witness chain (physical demo audit trail)

Every servo movement, every sensor sample — all logged:

```
BIND cell:finger_1 @ tick=0
BIND cell:imu_orient @ tick=1
BIND cell:base @ tick=2
BIND cell:shoulder @ tick=3
BIND cell:end_effector @ tick=7
EFFECT cell:finger_1 → 0.85 (significant bend) @ tick=48
EFFECT cell:imu_orient → (0.1, 0.2, 9.8) @ tick=49
LINK fk:finger_1 → shoulder (90° at full bend) @ tick=50
EFFECT cell:shoulder → 90.0 @ tick=50
EFFECT cell:base → 45.0 (rotate to face object) @ tick=51
EFFECT cell:shoulder → 90.0 → 75.0 (lower arm) @ tick=120
EFFECT cell:elbow → 60.0 → 45.0 (extend) @ tick=121
EFFECT cell:end_effector → holding @ tick=180
EFFECT cell:shoulder → 75.0 → 100.0 (lift) @ tick=240
...
```

The witness chain **proves** the arm did what it was supposed to do. No
more "the gripper closed but I don't know why."

## Polyformal port plan (from QUILT_PORT.md)

| Port | What it adds |
|---|---|
| **Python (upstream)** | Reference port. Cells wrap sensor reads + servo writes. |
| **C / Pico firmware** | The 5+1 opcodes in C. For real-time control. |
| **Rust / no_std** | Type-safe, embassy-time-driven TICK. For resource-constrained targets. |
| **TypeScript / browser** | The arm + glove as a WebGPU animation. The cell-graph drives a 3D model. |
| **JSON-API** | REST over the cell-graph. Telemetry feeds dashboards. |

## Integration with the broader Quilt ecosystem

- **`quilt-esp32`** — the existing ESP32 substrate. Port the arm there
  for direct sensor I/O without a separate SBC.
- **`mudra-vessel-bridge`** — existing gesture pipeline. The glove code
  can adopt its gesture vocabulary directly.
- **`quilt-cordis`** — the cell-plugin bridge. Each joint + sensor becomes
  a Cordis plugin; the FK function lives in the LINK graph.
- **`flx-cuda`** — GPU-accelerated forward kinematics. Hundreds of
  inverse-kinematics iterations to find the optimal joint configuration.

## Code example (Python, reference port)

```python
from quilt import Cell, Substrate

sub = Substrate(name="arm-glove-v1")

# BIND the cells (glove + arm)
f1 = sub.bind(Cell(address="finger_1", value=0.0, axes=("idx",)))
imu = sub.bind(Cell(address="imu_orient", value=(0, 0, 0), axes=("x", "y", "z")))
base = sub.bind(Cell(address="base", value=0.0, axes=("idx",)))
shoulder = sub.bind(Cell(address="shoulder", value=0.0, axes=("idx",)))
elbow = sub.bind(Cell(address="elbow", value=0.0, axes=("idx",)))
wrist = sub.bind(Cell(address="wrist", value=0.0, axes=("idx",)))
end_eff = sub.bind(Cell(address="end_effector", value="open", axes=("state",)))

# TYPED LINKS — glove sensors → arm joints (forward kinematics)
sub.link("finger_1", "shoulder", edge_type="fk:1_to_shoulder")
sub.link("finger_2", "elbow", edge_type="fk:2_to_elbow")
sub.link("finger_3", "wrist", edge_type="fk:3_to_wrist")
sub.link("imu_orient", "base", edge_type="fk:imu_to_base_rotation")
sub.link("finger_5", "end_effector", edge_type="fk:thumb_to_gripper")

# EFFECT — glove flex 1 sample
sub.effect("finger_1", lambda v: 0.85)

# The FK function (could run on CPU or flx-cuda GPU):
def forward_kinematics(sub):
    """Read glove cells, write joint cells."""
    bend = sub.view("finger_1")
    target_shoulder = bend * 90.0  # 90° at full bend
    sub.effect("shoulder", lambda v: target_shoulder)

forward_kinematics(sub)

# VIEW the result
print(f"shoulder angle: {sub.view('shoulder')}")  # 76.5°
print(f"witness events: {len(sub.witness)}")
```

## The honest scope

- **What was ported:** Sensor pipeline, forward kinematics, servo control
- **What was preserved:** All upstream code (`src/`, `designs/`,
  `assets/`, `docs/`)
- **What was added:** The cell-graph projection (this document)
- **What's stubbed:** Physical hardware integration (Python only;
  no SDK for the actual servos yet)
- **What's deferred:** Real-time C/Rust firmware ports, GPU
  forward kinematics, multi-arm synchronization

## See also

- `UPSTREAM.md` — original repo, faithfully documented
- `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands
- `QUILT_PORT.md` — the umbrella port plan
- `README.md` (landing page) — dispatches you to the right doc
