# UPSTREAM — quilt-Countroller (preserved from upstream)

This document preserves the **original upstream project** — Countroller,
an EmbarcaTech capstone by the Brazilian team — faithfully, with no
Quilt framing imposed. If you want the original, **read this first**.
The Quilt layer (added by SuperInstance) is documented separately in
`QUILT.md`.

## Original description

> Sistema interativo embarcado com matriz de LEDs, controle por joystick e
> feedback visual e sonoro.
>
> *(Interactive embedded system with LED matrix, joystick control, and
> visual and sound feedback.)*

## What the upstream is

- A **Raspberry Pi Pico W** embedded system
- **5×5 NeoPixel RGB** LED matrix
- **Joystick input** (X/Y axes via ADC)
- **Two buttons** (A and B) + joystick center-click
- **OLED display** (SSD1306, I2C)
- **Two buzzers** (PWM audio)
- **C/C++** on Pico SDK, CMake build system

## What the upstream does

A main loop:

1. **Read joystick** — sample ADC channels, normalize X/Y
2. **Read buttons** — debounce, increment counters
3. **Render patterns** — Heart, IF (Instituto Federal initials), PI
4. **Update OLED** — display current button counts and joystick info
5. **Sound buzzers** — beep on button press

The cursor moves on the LED matrix when the joystick moves. Patterns
are pre-programmed 5×5 boolean grids. The whole thing is interactive:
press a button, see the LED matrix respond, hear a buzz.

## How the upstream works

```
src/
├── init.c                  — System init (LEDs, buttons, buzzers, display)
├── joystick.c              — ADC read + normalize
├── buttons.c               — Debounce + counter increment
├── buzzer.c                — PWM init + beep
├── display.c               — I2C OLED init + message write
├── neopixel.c              — WS2812 serial + pattern rendering
└── main.c                  — main loop: read_joystick, read_buttons

include/
├── init.h, joystick.h, buttons.h, buzzer.h, display.h, neopixel.h
└── ssd1306/                — OLED driver

CMakeLists.txt              — Pico SDK build config
pico_sdk_import.cmake       — Pico SDK setup
```

### Data flow (per main loop iteration)

1. `read_joystick()` samples ADC channels → normalized X/Y values
2. `read_buttons()` polls GPIO, debounces, increments counters
3. `neopixel.c` renders the active pattern (heart / IF / PI)
4. `display.c` writes the OLED message ("Button A: 5", etc.)
5. `buzzer.c` triggers a beep if a button was pressed this iteration

## Quick start (original)

```bash
# Requires Raspberry Pi Pico SDK + CMake + ARM toolchain
mkdir build
cd build
cmake ..
make

# Flash to Pico
picotool load -f countroller.uf2
```

## Credits and license

- **Upstream:** Brazilian EmbarcaTech capstone (Unit 7)
- **Upstream license:** MIT (preserved in `LICENSE`)
- **Quilt elevation:** SuperInstance (added the cell-graph projection layer)
- **Quilt layer license:** MIT (added as `LICENSE-QUILT`)

## Notes on the fork

- **Date imported:** 2026-09-15
- **Preserved:** All upstream code (src/, include/, CMake config, Pico
  SDK setup). Nothing upstream was modified.
- **Added:** Python simulator port (`quilt/`), `QUILT_PORT.md` (the
  porting plan), `docs/QUILT.md`, `docs/PLAIN_LANGUAGE.md`,
  `docs/extends-to-anything.html`, and a landing-page README.
- **Pre-Quilt quirks:** The original README is in Portuguese. We
  preserved both the Portuguese version and translated it for the
  English-language docs. The artifact naming follows upstream
  conventions; the documentation naming follows the Quilt convention.

---

For the **Quilt projection layer** that makes this program **visible as
a cell-graph**, see `QUILT.md`. For the **plain-language version** that
explains what this does for working people, see `PLAIN_LANGUAGE.md`.
For the **extends-to-anything visualization** showing the 5-polyformal
ports, see `extends-to-anything.html`.
