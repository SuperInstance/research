"""
Quilt port of quilt-Countroller — Python simulator.

The Countroller is a Raspberry Pi Pico W embedded system:
- 5×5 NeoPixel RGB LED matrix (WS2812)
- Joystick (X/Y axes via ADC)
- Two buttons (A, B) + joystick button
- OLED display (SSD1306, I2C)
- Two buzzers (PWM)

The upstream is in C/Pico SDK. This port wraps every input and output as a
Quilt cell, defines the forward kinematics / button actions as typed LINKs,
and runs the whole thing in pure Python. No hardware needed.

The cell-graph is the canonical description. Other polyformal ports
(C/Pico, Rust/Pico, TypeScript/browser, JSON-API) reuse the same schema.
"""

from .cells import (
    Cell, Substrate, Link,
    JoystickCell, ButtonCell, LEDCell, BuzzerCell, OLEDCell,
    JoystickButtonCell,
)
from .patterns import (
    HeartPattern, IfPattern, PiPattern,
    bind_pattern_to_leds, render_pattern,
)
from .simulator import CountrollerSimulator

__version__ = "0.1.0"
__all__ = [
    "Cell", "Substrate", "Link",
    "JoystickCell", "ButtonCell", "LEDCell", "BuzzerCell", "OLEDCell",
    "JoystickButtonCell",
    "HeartPattern", "IfPattern", "PiPattern",
    "bind_pattern_to_leds", "render_pattern",
    "CountrollerSimulator",
]
