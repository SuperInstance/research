# UPSTREAM — Gesture-Controlled Robotic Arm (preserved from upstream)

This document preserves the **original upstream project** — a
gesture-controlled robotic arm with pick-and-place functionality — faithfully,
with no Quilt framing imposed. If you want the original, **read this first**.
The Quilt layer (added by SuperInstance) is documented separately in
`QUILT.md`.

## Original description

> The Gesture-Controlled Robotic Arm is designed to automate repetitive
> tasks using hand gestures. The robotic arm consists of four links: a
> base, two links, and an end effector, enabling pick-and-place
> functionality.
>
> Control is achieved via a glove-based gesture system, equipped with
> flex sensors and an accelerometer, translating hand movements into
> precise robotic commands.

## What the upstream is

- A **4-link robotic arm** (base + 2 links + end effector)
- A **sensor-equipped glove** with flex sensors and an accelerometer
- Pick-and-place functionality
- Hardware documentation in `designs/` and `assets/`
- Python source code in `src/`
- A "Meet the Team!" section in the README (college project)

## What the upstream does

The user wears a glove. They make hand gestures. The robotic arm mirrors
the gestures. Pick-and-place tasks become intuitive: reach for an object,
grasp it, move it, release.

Specific features (from the README):
- 4-Link Robotic Arm Structure with precise movement
- Gesture-Based Control via flex sensors + accelerometer
- Future Plans for 4-link expansion (already mentioned in the upstream)

## How the upstream works

```
designs/           — Wiring diagrams, mechanical drawings
assets/            — Icons, images, UI mockups
docs/              — Project documentation
src/               — Python source code (gesture recognition, FK, motor control)
tests/             — Test suite
requirements.txt   — Python dependencies
CONTRIBUTING.md    — Contribution guidelines
README.md          — The upstream README (preserved)
```

### Hardware pipeline

1. Glove sensors (flex + IMU) sample at high rate
2. Python script reads sensor values via serial or BLE
3. Gesture recognition converts sensor stream to joint angles
4. Forward kinematics calculates end-effector position
5. Servo commands sent to arm via PWM
6. Arm joints move to specified angles

## Quick start (original)

```bash
git clone https://github.com/SuperInstance/Quilt-Robotic-Arm---Gesture-Controlled.git
cd Quilt-Robotic-Arm---Gesture-Controlled
pip install -r requirements.txt

# Read the upstream docs first
cat README.md
ls designs/
ls src/
```

(Actual hardware setup requires the glove + arm. See the upstream README.)

## Credits and license

- **Upstream:** College-style hardware project (4-link arm + gesture glove)
- **Upstream license:** MIT (preserved in `LICENSE`)
- **Quilt elevation:** SuperInstance (added the cell-graph projection layer)
- **Quilt layer license:** MIT (added as `LICENSE-QUILT`)

## Notes on the fork

- **Date imported:** 2026-09-15
- **Preserved:** All upstream code (`src/`, `designs/`, `assets/`,
  `docs/`, `tests/`, requirements.txt, CONTRIBUTING.md)
- **Added:** `QUILT_PORT.md` (the porting plan), `docs/QUILT.md`
  (the cell-graph projection), `docs/PLAIN_LANGUAGE.md`
  (captains-and-mechanics version), and a landing-page README
- **Pre-Quilt quirks:** The README is a typical college-style
  project write-up with emojis, a "Meet the Team!" section, and
  future-plans. We preserved it all.

---

For the **Quilt projection layer** that makes this program **visible as
a cell-graph**, see `QUILT.md`. For the **port plan** that wraps
sensors/joints as cells, see `QUILT_PORT.md`. For the **plain-language
version** that explains what this does for working people, see
`PLAIN_LANGUAGE.md`.
