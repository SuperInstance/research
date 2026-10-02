"""
Tests for the Countroller Quilt substrate.

The 5+1 opcodes (BIND, LINK, EFFECT, VIEW, TICK, FORGET) and the
Countroller-specific cells. Run with `python3 -m unittest tests.test_simulator`.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quilt import (
    CountrollerSimulator,
    JoystickCell, ButtonCell, LEDCell, BuzzerCell, OLEDCell,
    HeartPattern, IfPattern, PiPattern,
)
from quilt.cells import BIND, LINK, EFFECT, VIEW, FORGET, Cell, Substrate


class TestOpcodes(unittest.TestCase):
    """The 5+1 opcodes must satisfy the algebraic laws."""

    def test_bind_idempotent(self):
        cell = Cell(address="x", value=42)
        BIND(cell)
        BIND(cell)
        self.assertTrue(cell._bound)

    def test_link_creates_typed_edge(self):
        sub = Substrate(name="test")
        c1 = sub.bind(Cell(address="a", value=1))
        c2 = sub.bind(Cell(address="b", value=2))
        link = sub.link("a", "b", edge_type="controls")
        self.assertEqual(link.source, "a")
        self.assertEqual(link.target, "b")
        self.assertEqual(link.edge_type, "controls")

    def test_effect_runs_function(self):
        cell = Cell(address="counter", value=0)
        EFFECT(cell, lambda v: v + 1)
        EFFECT(cell, lambda v: v + 1)
        self.assertEqual(cell.value, 2)

    def test_view_returns_value(self):
        cell = Cell(address="x", value="hello")
        self.assertEqual(VIEW(cell), "hello")

    def test_forget_runs_inverse(self):
        cell = Cell(address="x", value=10)
        EFFECT(cell, lambda v: v + 5)
        self.assertEqual(cell.value, 15)
        FORGET(cell)
        self.assertEqual(cell.value, None)


class TestJoystick(unittest.TestCase):
    def test_update_normalizes(self):
        j = JoystickCell()
        j.update(2.0, -2.0)  # out of range
        self.assertEqual(j.value, (1.0, -1.0))

    def test_update_drops_confidence_at_extremes(self):
        j = JoystickCell()
        j.update(0.0, 0.0)
        c_at_center = j.confidence
        j.update(1.0, 1.0)
        c_at_edge = j.confidence
        self.assertGreater(c_at_center, c_at_edge)


class TestButton(unittest.TestCase):
    def test_press_increments(self):
        b = ButtonCell(address="a", label="A")
        self.assertEqual(b.value, 0)
        b.press()
        self.assertEqual(b.value, 1)
        b.press()
        b.press()
        self.assertEqual(b.value, 3)


class TestLED(unittest.TestCase):
    def test_set_color(self):
        led = LEDCell(address="led_2_2", x=2, y=2)
        led.set_color(255, 100, 50)
        self.assertEqual(led.value, (255, 100, 50))

    def test_set_color_clamps(self):
        led = LEDCell(address="led_0_0", x=0, y=0)
        led.set_color(300, -50, 128)
        self.assertEqual(led.value, (255, 0, 128))


class TestBuzzer(unittest.TestCase):
    def test_buzz_sets_frequency(self):
        bz = BuzzerCell(address="b1")
        bz.buzz(freq=2000)
        self.assertEqual(bz.value, 2000)

    def test_silence(self):
        bz = BuzzerCell(address="b1")
        bz.buzz(freq=2000)
        bz.silence()
        self.assertEqual(bz.value, 0)


class TestOLED(unittest.TestCase):
    def test_display(self):
        o = OLEDCell()
        o.display("Hello Quilt")
        self.assertEqual(o.value, "Hello Quilt")

    def test_display_truncates_to_32(self):
        o = OLEDCell()
        long_msg = "A" * 100
        o.display(long_msg)
        self.assertEqual(len(o.value), 32)


class TestPatterns(unittest.TestCase):
    def test_heart_has_expected_count(self):
        # Heart pattern: 17 lit cells in 5x5 (matches upstream neopixel.c)
        lit = HeartPattern.cells_with_color()
        self.assertEqual(len(lit), 17)

    def test_if_pattern_lit_count(self):
        lit = IfPattern.cells_with_color()
        self.assertGreater(len(lit), 5)

    def test_pi_pattern_lit_count(self):
        lit = PiPattern.cells_with_color()
        self.assertGreater(len(lit), 5)

    def test_pattern_binds_to_leds(self):
        from quilt.cells import LEDCell
        leds = {(x, y): LEDCell(address=f"led_{x}_{y}", x=x, y=y)
                for y in range(5) for x in range(5)}
        links = []
        for pattern in [HeartPattern, IfPattern, PiPattern]:
            links.extend(pattern_to_links_helper(pattern, leds))
        # Each pattern should bind at least 5 LEDs
        self.assertGreater(len(links), 15)


def pattern_to_links_helper(pattern, leds):
    from quilt.patterns import bind_pattern_to_leds
    return bind_pattern_to_leds(pattern, leds)


class TestSimulator(unittest.TestCase):
    def test_init_binds_32_cells(self):
        sim = CountrollerSimulator()
        # 25 LEDs + joystick + 2 buttons + joystick button + 2 buzzers + oled = 32
        self.assertEqual(len(sim.substrate.cells), 32)

    def test_init_creates_typed_links(self):
        sim = CountrollerSimulator()
        # joystick controls cursor, button_a sounds buzzer_1, etc.
        edge_types = {link.edge_type for link in sim.substrate.links}
        self.assertIn("controls_cursor", edge_types)
        self.assertIn("sounds", edge_types)
        self.assertIn("displays", edge_types)
        self.assertIn("renders", edge_types)

    def test_joystick_moves_cursor(self):
        sim = CountrollerSimulator()
        sim.update_joystick(0.8, 0.8)
        self.assertEqual(sim.cursor, (4, 4))
        sim.update_joystick(-0.8, -0.8)
        self.assertEqual(sim.cursor, (0, 0))

    def test_button_a_increments_once(self):
        sim = CountrollerSimulator()
        sim.press_button_a()
        self.assertEqual(sim.button_a.value, 1)
        sim.press_button_a()
        self.assertEqual(sim.button_a.value, 2)

    def test_button_a_sounds_buzzer_1(self):
        sim = CountrollerSimulator()
        sim.press_button_a()
        self.assertEqual(sim.buzzer_1.value, 1000)

    def test_joystick_button_sounds_both_buzzers(self):
        sim = CountrollerSimulator()
        sim.press_joystick_button()
        self.assertEqual(sim.buzzer_1.value, 1000)
        self.assertEqual(sim.buzzer_2.value, 1000)
        self.assertEqual(sim.joystick_button.value, 1)

    def test_pattern_renders_correct_count(self):
        sim = CountrollerSimulator()
        sim.activate_pattern(HeartPattern)
        lit_leds = sum(1 for led in sim.leds.values() if led.value != (0, 0, 0))
        self.assertEqual(lit_leds, len(HeartPattern.cells_with_color()))

    def test_clear_pattern_deactivates(self):
        sim = CountrollerSimulator()
        sim.activate_pattern(HeartPattern)
        sim.clear_pattern()
        for led in sim.leds.values():
            self.assertEqual(led.value, (0, 0, 0))
        self.assertIsNone(sim.active_pattern)

    def test_witness_records_state_changes(self):
        sim = CountrollerSimulator()
        n_before = len(sim.substrate.witness)
        sim.press_button_a()
        sim.press_button_b()
        n_after = len(sim.substrate.witness)
        self.assertGreater(n_after, n_before + 4)  # at least 4 new events

    def test_render_status_returns_string(self):
        sim = CountrollerSimulator()
        s = sim.render_status()
        self.assertIsInstance(s, str)
        self.assertIn("Quilt Countroller", s)


if __name__ == "__main__":
    unittest.main()
