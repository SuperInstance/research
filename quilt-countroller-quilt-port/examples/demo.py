"""
Demo: run the Countroller Quilt simulator through a full session.

Demonstrates:
- Initial state (no pattern, cursor at center)
- Joystick input (cursor moves)
- Button A press (counter + buzzer + OLED update)
- Button B press (counter + buzzer + OLED update)
- Joystick button press (both counters + both buzzers + OLED)
- Heart pattern activation
- Clear pattern
- Witness replay

The same cell-graph that runs in this Python simulator runs in:
- C/Pico firmware (quilt-c substrate)
- Rust/Pico (no_std, on real ESP32/Pico)
- TypeScript/browser (canvas pixels)
- JSON-API (REST over the cell-graph)

Every cell, every link, every EFFECT — same.
"""

import sys
import os

# Add the parent dir to path so we can import quilt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quilt import CountrollerSimulator, HeartPattern, IfPattern, PiPattern


def main():
    sim = CountrollerSimulator()

    print("=== Initial state ===")
    print(sim.render_status())

    print("\n=== Move joystick to top-right (x=+0.8, y=+0.8) ===")
    sim.update_joystick(x=0.8, y=0.8)
    print(sim.render_status())

    print("\n=== Move joystick to bottom-left (x=-0.6, y=-0.6) ===")
    sim.update_joystick(x=-0.6, y=-0.6)
    print(sim.render_status())

    print("\n=== Press Button A ===")
    sim.press_button_a()
    print(sim.render_status())

    print("\n=== Press Button A again (count → 2) ===")
    sim.press_button_a()
    print(sim.render_status())

    print("\n=== Press Button B ===")
    sim.press_button_b()
    print(sim.render_status())

    print("\n=== Press Joystick button (sounds both buzzers) ===")
    sim.press_joystick_button()
    print(sim.render_status())

    print("\n=== Activate heart pattern ===")
    sim.activate_pattern(HeartPattern)
    print(sim.render_status())

    print("\n=== Clear pattern ===")
    sim.clear_pattern()
    print(sim.render_status())

    print("\n=== Activate IF pattern (Instituto Federal) ===")
    sim.activate_pattern(IfPattern)
    print(sim.render_status())

    print("\n=== Clear, activate PI pattern ===")
    sim.clear_pattern()
    sim.activate_pattern(PiPattern)
    print(sim.render_status())

    print("\n=== Witness replay (last 12 events) ===")
    for event in sim.witness_tail(12):
        print(f"  {event}")

    print(f"\n=== Total witness events: {len(sim.witness())} ===")
    print(f"=== Substrate cell count: {len(sim.substrate.cells)} ===")
    print(f"=== Substrate link count: {len(sim.substrate.links)} ===")


if __name__ == "__main__":
    main()
