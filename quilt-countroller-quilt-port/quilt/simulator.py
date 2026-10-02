"""
Python simulator for the quilt-Countroller substrate.

A faithful re-implementation of the upstream main loop, but using the
Quilt cell-graph as the canonical state. Runs in any Python 3.10+
interpreter — no hardware, no Pico SDK.

The simulator mirrors the upstream structure:
    init_system()       — bind all 25 LED cells + joystick + buttons + buzzers + OLED
    read_joystick()     — poll the joystick cell
    read_buttons()      — poll the button cells
    update_leds()       — render the cursor position to the matrix
    update_display()    — write state to the OLED cell (VIEW)
"""

from __future__ import annotations
from typing import Dict, Tuple

from .cells import (
    Substrate, JoystickCell, ButtonCell, JoystickButtonCell,
    LEDCell, BuzzerCell, OLEDCell,
)
from .patterns import HeartPattern, IfPattern, PiPattern


class CountrollerSimulator:
    """The Quilt cell-graph version of the Countroller.

    State: 25 LED cells + 1 joystick + 3 buttons + 2 buzzers + 1 OLED = 32 cells
    """

    def __init__(self):
        self.substrate = Substrate(name="countroller")
        self.joystick = JoystickCell()
        self.button_a = ButtonCell(address="button_a", label="A")
        self.button_b = ButtonCell(address="button_b", label="B")
        self.joystick_button = JoystickButtonCell()
        self.buzzer_1 = BuzzerCell(address="buzzer_1")
        self.buzzer_2 = BuzzerCell(address="buzzer_2")
        self.oled = OLEDCell()

        # 5×5 LED matrix
        self.leds: Dict[Tuple[int, int], LEDCell] = {}
        for y in range(5):
            for x in range(5):
                addr = f"led_{x}_{y}"
                self.leds[(x, y)] = LEDCell(address=addr, x=x, y=y)

        # Cursor on the matrix (which LED is "selected")
        self.cursor = (2, 2)

        # Active pattern (None = no pattern; the cursor is rendered instead)
        self.active_pattern = None

        # Init substrate: bind every cell
        for c in [self.joystick, self.button_a, self.button_b, self.joystick_button,
                  self.buzzer_1, self.buzzer_2, self.oled]:
            self.substrate.bind(c)
        for led in self.leds.values():
            self.substrate.bind(led)

        # Cross-cell links (typed):
        # joystick → cursor position (driven by joystick)
        self.substrate.link("joystick", "led_2_2", edge_type="controls_cursor")
        # button_a → buzzer_1 (button A sounds buzzer 1)
        self.substrate.link("button_a", "buzzer_1", edge_type="sounds")
        # button_b → buzzer_2 (button B sounds buzzer 2)
        self.substrate.link("button_b", "buzzer_2", edge_type="sounds")
        # joystick_button → both counters + both buzzers
        self.substrate.link("joystick_button", "buzzer_1", edge_type="sounds")
        self.substrate.link("joystick_button", "buzzer_2", edge_type="sounds")
        # buttons → OLED display (each button press updates display)
        self.substrate.link("button_a", "oled", edge_type="displays")
        self.substrate.link("button_b", "oled", edge_type="displays")
        # active_pattern → all LEDs (renders the pattern)
        for led in self.leds.values():
            self.substrate.link("active_pattern", led.address, edge_type="renders")

    # -----------------------------------------------------------------------
    # Input handlers — these are the "EFFECT" side of the input cells
    # -----------------------------------------------------------------------

    def update_joystick(self, x: float, y: float):
        """Simulate reading the joystick — updates joystick cell + cursor."""
        self.joystick.update(x, y)
        self.substrate.witness.append(
            f"EFFECT joystick → {self.joystick.value} @ tick={len(self.substrate.witness)}"
        )
        # Cursor follows joystick position, snapped to grid
        cx = max(0, min(4, int((x + 1.0) * 2.5)))
        cy = max(0, min(4, int((y + 1.0) * 2.5)))
        self.cursor = (cx, cy)

    def press_button_a(self):
        """Simulate Button A press."""
        self.button_a.press()  # This increments + appends to witness
        self.substrate.witness.append(f"EFFECT button_a → {self.button_a.value} @ tick={len(self.substrate.witness)}")
        self.substrate.effect("buzzer_1", lambda _: 1000)
        self.buzzer_1.buzz(freq=1000)
        msg = f"   Button A: {self.button_a.value}"
        self.substrate.effect("oled", lambda _: msg)
        self.oled.display(msg)

    def press_button_b(self):
        """Simulate Button B press."""
        self.button_b.press()
        self.substrate.witness.append(f"EFFECT button_b → {self.button_b.value} @ tick={len(self.substrate.witness)}")
        self.substrate.effect("buzzer_2", lambda _: 1000)
        self.buzzer_2.buzz(freq=1000)
        msg = f"   Button B: {self.button_b.value}"
        self.substrate.effect("oled", lambda _: msg)
        self.oled.display(msg)

    def press_joystick_button(self):
        """Simulate joystick center-click — sounds both buzzers, displays both counters."""
        self.joystick_button.press()
        self.substrate.witness.append(f"EFFECT joystick_button → {self.joystick_button.value} @ tick={len(self.substrate.witness)}")
        self.substrate.effect("buzzer_1", lambda _: 1000)
        self.substrate.effect("buzzer_2", lambda _: 1000)
        self.buzzer_1.buzz(freq=1000)
        self.buzzer_2.buzz(freq=1000)
        msg = f"   A: {self.button_a.value}, B: {self.button_b.value}"
        self.substrate.effect("oled", lambda _: msg)
        self.oled.display(msg)

    def activate_pattern(self, pattern):
        """Render a pattern to the LED matrix (heart / IF / PI)."""
        self.active_pattern = pattern
        # Clear all first
        for led in self.leds.values():
            self.substrate.effect(led.address, lambda _: (0, 0, 0))
            led.set_color(0, 0, 0)
        # Set pattern cells
        for x, y in pattern.cells_with_color():
            addr = f"led_{x}_{y}"
            self.substrate.effect(addr, lambda _: pattern.color)
            self.leds[(x, y)].set_color(*pattern.color)
        self.substrate.witness.append(
            f"PATTERN {pattern.name} rendered ({len(pattern.cells_with_color())} cells)"
        )

    def clear_pattern(self):
        """Deactivate any pattern and clear the matrix."""
        self.active_pattern = None
        for led in self.leds.values():
            self.substrate.effect(led.address, lambda _: (0, 0, 0))
            led.set_color(0, 0, 0)

    # -----------------------------------------------------------------------
    # Output view — render the LED matrix as a 2D string (the "VIEW" opcode)
    # -----------------------------------------------------------------------

    def render_led_matrix(self) -> str:
        """Render the 5×5 LED matrix as a 2D string for display."""
        lines = []
        for y in range(5):
            row = ""
            for x in range(5):
                led = self.leds[(x, y)]
                r, g, b = led.value
                if (r, g, b) == (0, 0, 0):
                    row += "·"
                else:
                    # Use brightness to choose a glyph
                    brightness = (r + g + b) / 3
                    if brightness > 200:
                        row += "█"
                    elif brightness > 100:
                        row += "▓"
                    else:
                        row += "░"
            lines.append(f"  {row}")
        return "\n".join(lines)

    def render_oled(self) -> str:
        """Render the OLED display as a string."""
        msg = self.oled.value or "(idle)"
        return f"  OLED: '{msg}'"

    def render_status(self) -> str:
        """Render the full system status — VIEW of all output cells."""
        lines = [
            "─" * 40,
            f"Quilt Countroller — substrate: {self.substrate.name}",
            f"  Cursor: {self.cursor}",
            f"  Joystick: {self.joystick.value}",
            f"  Button A count: {self.button_a.value}",
            f"  Button B count: {self.button_b.value}",
            f"  Joystick btn count: {self.joystick_button.value}",
            f"  Active pattern: {self.active_pattern.name if self.active_pattern else '(none)'}",
            f"  Witness events: {len(self.substrate.witness)}",
            "─" * 40,
            "  LED matrix:",
            self.render_led_matrix(),
            self.render_oled(),
            "─" * 40,
        ]
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Witness chain accessors
    # -----------------------------------------------------------------------

    def witness(self) -> list:
        return list(self.substrate.witness)

    def witness_tail(self, n: int = 10) -> list:
        return self.substrate.witness[-n:]
