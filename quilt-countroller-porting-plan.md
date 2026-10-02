# quilt-Countroller — Porting Plan

**Source repo:** https://github.com/SuperInstance/quilt-Countroller
**Size:** 11.5 MB · **Default branch:** main · **Status:** Imported from upstream EmbarcaTech capstone (Brazilian, Portuguese README, C/C++ on Pico SDK)
**Language:** C/C++ (CMake)

## What it is (upstream)

A Raspberry Pi Pico W embedded system:
- 5×5 NeoPixel RGB LED matrix
- Joystick input (X/Y axes via ADC)
- Two buttons
- OLED display (feedback)
- Two buzzers (PWM audio)

It runs a main loop: read inputs → update state → render to LED matrix → update OLED → sound buzzers. Portuguese README, EmbarcaTech Unit 7 capstone.

## What "Quilt-portable" means here

The Quilt substrate **already exists** for microcontrollers: `quilt-esp32` (no_std Rust, ~3KB flash). For the Pico, the choice is between:
- A C/CMake port of the Quilt runtime (similar pattern to `quilt-c` substrate)
- Rust on Pico (Pico SDK is C; Rust-Pico is young but exists)

Either way, the porting task is the same:

1. Wrap the joystick as a **Quilt cell** (`value=(x, y), axes=(), confidence=adc_quality`)
2. Wrap each button as a **Quilt cell** (`value=pressed|released, axes=(), confidence=debounce_quality`)
3. Wrap each NeoPixel as a **Quilt cell** (`value=(r, g, b), axes=(x, y), confidence=`)
4. Wrap each LED pattern (heart, IF, PI) as a **LINK-typed graph** between LED cells
5. Wrap the OLED display as a **VIEW** of any subgraph
6. Wrap the buzzers as **EFFECT**-typed cells (PWM duty cycle)
7. The whole system is a `Substrate(name='countroller')` and is mountable in any Quilt runtime

## Substrate mapping

| Hardware | Quilt cell | Opcodes |
|---|---|---|
| Joystick X | `cell(value=normalized_x, axes=())` | `BIND` once, `TICK` reads ADC |
| Joystick Y | `cell(value=normalized_y, axes=())` | same |
| Button A | `cell(value=pressed_count, axes=())` | `EFFECT` increments on press |
| Button B | same | same |
| Each NeoPixel (25 of them) | `cell(value=(r,g,b), axes=(x,y))` | `EFFECT` updates PWM |
| OLED display | `VIEW(subgraph)` | `VIEW` projects any cell values |
| Buzzer 1 | `cell(value=frequency_hz, axes=())` | `EFFECT` sets PWM |
| Buzzer 2 | same | same |
| LED patterns (heart, IF, PI) | `LINK(led_cells, type='pattern')` | `LINK` defines the pattern graph |
| Cursor on matrix | `cell(value=(cursor_x, cursor_y), axes=())` | `LINK` to LED cells for color |

## The 5+1 opcodes that actually run

```
BIND joystick, buttons, LED cells, buzzers, OLED
LINK joystick → cursor position → LED cells (typed "controlled_by")
LINK patterns (heart, IF, PI) → LED cells (typed "renders_pattern")
EFFECT LED cells update PWM when cursor moves or pattern toggles
EFFECT buzzers when buttons pressed
VIEW OLED reads any subset of cells
TICK at 60Hz (joystick sample rate)
FORGET unused cells to save flash
```

## The "ports to anything" extension

You said *"a version that easily ports to anything from prompts for a model to robots to a graphed data stream on a DAW etc."*

This is the killer app of the Countroller port. Once the cell-graph is the canonical description:

| Target | Translation | Where the cells become |
|---|---|---|
| **Prompts for a model** | LED matrix cells → token positions; joystick → cursor in prompt; buttons → "submit" / "regenerate" | UI cell-graph for an LLM playground |
| **Robots** | LED cells → joint positions; joystick → manual control; buttons → gripper / release | Same cell-graph, different EFFECT bindings |
| **DAW data stream** | LED cells → MIDI notes; joystick → fader; buttons → play/stop/record | Music cell-graph — `quilt-mhs` already covers MHS devices |
| **Browser** | LED cells → pixels in a canvas; joystick → mouse position | `quilt-cellular-arch` already targets WebGPU |
| **Trading** | LED cells → portfolio positions; joystick → buy/sell ratio; buttons → execute/cancel | The paper-trading use case from CUDA-Q §3.4 |

**One cell schema, N substrates.** That's the polyformalism payoff. The Countroller's 5×5 LED matrix is small enough to be the canonical "minimum cell graph" — a hello-world of the Quilt substrate that ports to every runtime.

## Implementation steps

| Step | Effort | What ships |
|---|---|---|
| 1. Translate upstream README to English | 30 min | `docs/UPSTREAM.md` — what it is, in English, with diagrams |
| 2. Define cell schema | 2 hr | Python dataclasses for joystick/button/LED/buzzer cells |
| 3. Wrap in `quilt-cordis` | 2-3 hr | Mountable in any Cordis runtime |
| 4. Polyformal port plan | 1-2 hr | The same cell-graph in 5 languages: C/Pico, Rust/Pico, TypeScript/browser, Python/simulator, JSON-API |
| 5. First polyformal port | 4-6 hr | Pick one (recommend Python/simulator) and ship it |
| 6. The 5-port demo | 8-12 hr | All 5 polyformal ports of the same cell-graph |
| 7. Witness chain | 1 hr | Every input → witness append |
| 8. Documentation | 2 hr | The polyformalism comparison |

**Total: ~22-32 hours for the 5-port demo (the full "ports to anything" vision).**

## API surface (for subagent management)

Same shape as the arm project:

```
GET  /cells?type=button|led|joystick|buzzer
GET  /cells/<addr>
POST /cells/<addr>/effect  body={"value": ...}
GET  /witness?since=<tick>
GET  /graph?root=led.<x>.<y>
POST /pattern  body={"name": "heart|IF|PI"}
```

The Countroller API is also small. The subagent job: maintain the FastAPI/axum server, generate typed clients, write conformance tests, deploy on the Pico + a Cloudflare Worker (so the API is reachable from any device).

## What you could ship next

The minimum viable polyformal demo is steps 1-5. The full "ports to anything" version is steps 1-7.

**My recommended first polyformal port target**: Python/simulator. Reasons:
- No hardware needed
- The simulator is the same cell-graph as the Pico firmware
- The witness chain works in the simulator → can replay
- Faster to ship than Pico (no SDK setup)
- Once Python/simulator works, ports to TypeScript/browser (canvas) and C/Pico are mechanical

## Bonus: the README in Portuguese is a feature, not a bug

EmbarcaTech is Brazilian. The Portuguese README is a real artifact of the upstream. **Keep it.** Add an English version alongside. The polyformalism here is bigger than just code — it's also *language*. A cell-graph that's documented in both Portuguese and English is itself a polyformalism.

---

**Files to create in the repo:**
- `quilt/__init__.py` — cell schema
- `quilt/cells.py` — joystick/button/LED/buzzer cells
- `quilt/substrate.py` — `Substrate(name='countroller')`
- `quilt/plugin.py` — `quilt-cordis` adapter
- `quilt/patterns.py` — heart/IF/PI as LINK-typed graphs
- `quilt/api.py` — FastAPI surface (subagent's domain)
- `docs/QUILT_PORT.md` — what changed from upstream
- `docs/UPSTREAM.md` — Portuguese README + English translation
- `examples/simulator.py` — Python simulator (first polyformal port)
- `examples/witness_replay.py` — replay a recorded session

The 5×5 LED matrix is the hello-world of the substrate. **Every cell is the same idea in different forms** — that's exactly what the Countroller's smallness enables.
