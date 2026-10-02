# QUILT — quilt-Countroller as a cell-graph

This is the **Quilt projection layer** for quilt-Countroller. The
original Pico firmware is preserved (see `UPSTREAM.md`); this document
shows how the same program becomes **visible as a 32-cell substrate**
using the 5+1 opcodes.

Audience: applied engineers who know embedded systems / microcontrollers
/ the Pico SDK but not necessarily Quilt.

## What the cell-graph looks like

```
                         ┌────────────────────────┐
                         │  cell:substrate         │
                         │  name=countroller       │
                         │  axis=role              │
                         └───────────┬────────────┘
                                     │ (typed: contains)
                                     ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                 │
┌──▼───────────────┐  ┌─────────────────┐  ┌────────────────┐  ┌───────▼──────────┐
│  cell:joystick    │  │  cell:button_a   │  │  cell:button_b │  │  cell:joystick_btn│
│  value=(x, y)     │  │  value=count     │  │  value=count    │  │  value=count     │
│  axes=(x, y)      │  │  axes=(count,)   │  │  axes=(count,) │  │  axes=(count,)   │
│  link=cursor      │  │  link=buzzer_1   │  │  link=buzzer_2 │  │  link=both_buzzers│
└──────────────────┘  └─────────────────┘  └────────────────┘  └──────────────────┘
                                                                 
┌─────────────────────┐  ┌────────────────────┐  ┌─────────────────────┐
│  cell:buzzer_1       │  │  cell:buzzer_2     │  │  cell:oled          │
│  value=freq_hz      │  │  value=freq_hz     │  │  value=text_msg     │
│  axes=(freq,)       │  │  axes=(freq,)      │  │  axes=(text,)       │
│  link=button_a       │  │  link=button_b     │  │  link=buttons       │
└─────────────────────┘  └────────────────────┘  └─────────────────────┘

       ┌──────────────────────────────────────────────────┐
       │  25 × cell:led_X_Y                                │
       │  value=(r, g, b)                                 │
       │  axes=(x, y)                                    │
       │  link=cursor, link=active_pattern               │
       └──────────────────────────────────────────────────┘
```

**Total: 32 cells.** Same count as a small hello-world of the substrate.

## The 5+1 opcodes in action

Every upstream action maps to a Quilt opcode:

| Upstream action | Quilt opcode | Cell(s) affected |
|---|---|---|
| System init | `BIND` | All 32 cells |
| Joystick ADC read | `EFFECT(joystick, lambda v: (x, y))` | Joystick cell value updates |
| Button press | `EFFECT(button_X, lambda v: v + 1)` | Counter cell increments |
| Buzzer beep | `EFFECT(buzzer_X, lambda v: 1000)` | Buzzer cell freq = 1000 |
| OLED write | `EFFECT(oled, lambda v: msg)` | OLED cell text updates |
| LED color set | `EFFECT(led_X_Y, lambda v: (r, g, b))` | LED cell color updates |
| Main loop tick | `TICK(dt=0.016)` | Clock advances (60Hz) |
| Component unmount | `FORGET(cell)` | Cell removed |

## The cell subtypes

| Cell | Type | Lifecycle |
|---|---|---|
| `joystick` | Sensor | `BIND` once, `EFFECT` per ADC read |
| `button_a`, `button_b`, `joystick_button` | Event | `BIND` once, `EFFECT` per press |
| `buzzer_1`, `buzzer_2` | Actuator | `BIND` once, `EFFECT` per beep |
| `oled` | Display | `BIND` once, `EFFECT` per message |
| `led_X_Y` (×25) | Actuator | `BIND` once, `EFFECT` per render |

## The witness chain

Every state change appends to a witness log:

```
BIND joystick @ tick=0
BIND button_a @ tick=1
BIND buzzer_1 @ tick=2
BIND led_2_2 @ tick=3
EFFECT joystick → (0.5, 0.3) @ tick=42
EFFECT led_2_2 → (255, 0, 0) @ tick=43
EFFECT button_a → 1 @ tick=58
EFFECT buzzer_1 → 1000 @ tick=59
EFFECT oled → "Button A: 1" @ tick=60
EFFECT buzzer_1 → 0 @ tick=65
TICK dt=0.016 @ tick=66
EFFECT joystick → (0.6, 0.4) @ tick=82
EFFECT led_3_2 → (255, 0, 0) @ tick=83
EFFECT joystick → (-0.4, -0.3) @ tick=98
EFFECT led_1_1 → (255, 0, 0) @ tick=99
```

The witness chain IS the system's audit trail. Replay it and you
reconstruct the exact sequence of inputs and outputs. **Critical for
debugging.** "Why did the LED light up at that moment?" → check the
witness chain.

## Polyformal port plan

The same 32-cell substrate ports to:

| Port | What it adds |
|---|---|
| **Pico firmware (upstream)** | Real hardware. WS2812 LEDs, ADC joystick, GPIO buttons, PWM buzzers, I2C OLED. |
| **Python simulator** | Pure Python. No hardware. Reference port; 28 tests passing. |
| **Rust / no_std** | Same cells on Rust + Quilt-ESP32 / Quilt-Pico runtime. ~3KB flash. |
| **TypeScript / browser** | Canvas pixels replace NeoPixels. WebBluetooth to real Pico. |
| **JSON-API** | Cell-graph exposed as REST. Cloudflare Workers. |

**See also `extends-to-anything.html` for the visualization.**

## Integration with the broader Quilt ecosystem

- **`quilt-cordis`** — the cell-plugin bridge. Each upstream module
  becomes a Cordis plugin.
- **`quilt-casting`** — model router. The "pick pattern" button could
  pick which pattern to render via the casting plugin.
- **`flx-cuda`** — GPU-accelerated LED rendering. Thousands of cells
  composited at frame rate.
- **`flux-hardware`** — hardware backend picker. Pico for embedded,
  WebGPU for browser, CUDA for batch simulation.

## Code example (Python, reference port)

```python
from quilt import CountrollerSimulator

sim = CountrollerSimulator()
sim.update_joystick(x=0.5, y=0.3)        # EFFECT joystick
sim.press_button_a()                     # EFFECT button_a + buzzer_1 + oled
sim.activate_pattern(HeartPattern)       # BIND all pattern cells + EFFECT LEDs
print(sim.render_status())               # VIEW all output cells
print(sim.witness_tail(5))               # VIEW the witness chain tail
```

The reference port is in `quilt/` and runs the demo in `examples/demo.py`.
28 tests in `tests/test_simulator.py` cover the opcodes, cells, patterns,
and simulator.

## The honest scope

- **What was ported:** The component tree, the state shape, the event flow
- **What was preserved:** All upstream code (`src/`, `include/`,
  CMake, Pico SDK config)
- **What was added:** The cell-graph projection (this document), the
  Python simulator (`quilt/`), the example/demo and tests, the
  extends-to-anything visualization
- **What's stubbed:** None — both the upstream and the Python port
  are working
- **What's deferred:** Rust port, TypeScript port, JSON-API deployment,
  vectorize cross-pollination

## See also

- `UPSTREAM.md` — original repo, faithfully documented
- `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands
- `QUILT_PORT.md` — the umbrella porting plan
- `extends-to-anything.html` — the 5-polyformal port visualization
- `README.md` (landing page) — dispatches you to the right doc
