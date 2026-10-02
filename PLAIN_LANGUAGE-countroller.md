# PLAIN_LANGUAGE — quilt-Countroller for captains, mechanics, deckhands

You don't need to know C. You don't need to know Raspberry Pi. You don't
need to know Quilt. This is the short version.

## What this is

A small handheld device with **25 colored lights** arranged in a 5×5
grid, a **joystick**, **three buttons**, a **tiny screen**, and two
**beepers**. Plug it in, press the buttons, the lights light up.

It's the smallest possible piece of interactive electronics that does
something useful. Originally built as a Brazilian university capstone
project (EmbarcaTech Unit 7), now elevated with a Quilt layer so the
same device is **visible as a cell-graph** — a 32-cell spreadsheet that
shows exactly what's happening.

## What you can do with it

- Plug it into a USB port
- Wait for the lights to start
- Move the joystick — a small light moves with it
- Press the A button — beeper beeps, screen updates, A counter ticks up
- Press the B button — same with B
- Press the joystick itself — both beepers beep
- Hold a pattern button (heart, IF, π) — the grid lights up in that shape
- That's the whole device

## Small example

You're showing a kid how computers work. You give them the device. They
move the joystick. They see the light follow. They press a button.
They hear a beep and see the count tick up. They press a pattern.
They see the heart light up in red.

That's not a *demo of a feature*. **That's the whole lesson.** Inputs →
state → outputs. The kid just learned the foundation of all interactive
electronics in 30 seconds.

For a working person: imagine a small handheld for taking readings on a
boat. Joystick = sensor selector. Buttons = save / discard / next
reading. LED grid = which sensor is active. Tiny screen = reading
value. The Countroller is the chassis; the application is yours.

## What you could do today

If you wanted, you could:

1. **Use it as-is.** Flash the firmware, plug it in, play with it.
   It's a working interactive device.
2. **Replace the patterns.** The 5×5 grid can light up in any shape.
   Swap heart/IF/π for your boat's silhouette, your team's logo,
   the navigation markers you use most.
3. **Use it as a UI chassis.** The 5×5 grid + joystick + 3 buttons is
   enough for a small controller. Wire it to your application via USB
   serial and you have a physical interface for anything.
4. **Take it apart for parts.** The joystick, the NeoPixels, the OLED,
   the buttons — all cheap, all reusable. Use them in your own project.

That's the whole landscape. The Countroller is a **building block**,
not a finished product. What you build with it is yours.

## If you only have 60 seconds

- A small device: joystick, buttons, 5×5 LED grid, screen, beepers.
- Move the joystick, the light follows.
- Press a button, beep, count goes up.
- Press a pattern button, the grid lights up in that shape.
- The Quilt version makes every component a cell you can tap and
  inspect.
- If you're an engineer and you want to know about the cell-graph,
  read `QUILT.md`. If you want the upstream story, read `UPSTREAM.md`.

## What's not here yet

The Countroller is intentionally a **minimal proof of the cell-graph
concept**. It does not:

- Save state across power cycles (the counters reset on reboot)
- Connect to Wi-Fi (it's USB-tethered only)
- Have a battery (it's USB-powered only)
- Run AI workloads (it's a microcontroller, not a phone)

Those are all reasonable next steps. None of them are wired up. If you
need one of them, the upstream is a fine place to start — the code is
small enough that you can read the whole thing in 10 minutes.

---

Read time: ~2 minutes. Build time if you start from scratch: ~30 minutes
to install the Pico SDK, build the firmware, and flash it to the device.
