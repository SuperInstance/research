"""
Quilt cells for the Countroller substrate.

The cell schema is the canonical description — every polyformal port
(C/Pico, Rust/Pico, TypeScript/browser, JSON-API) implements these same
classes. The 5+1 opcodes (BIND, LINK, EFFECT, VIEW, TICK, FORGET) are
the operations on the cell-graph.
"""

from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# The 5+1 opcodes (Quilt substrate)
# ---------------------------------------------------------------------------

def BIND(cell: "Cell") -> "Cell":
    """Bind a cell to the substrate. Idempotent — BIND(BIND(c)) = BIND(c)."""
    if cell.address and not cell._bound:
        cell._bound = True
    return cell


def LINK(a: "Cell", b: "Cell", edge_type: str = "default") -> "Link":
    """Create a typed edge between two cells."""
    return Link(source=a.address, target=b.address, edge_type=edge_type)


def EFFECT(cell: "Cell", fn: Callable[[Any], Any]) -> Any:
    """Run a transformation on a cell. Returns the new value."""
    old = cell.value
    new = fn(old)
    cell.value = new
    cell._effects.append((fn, lambda _: old))  # inverse for FORGET
    cell.confidence = min(1.0, cell.confidence + 0.01)  # small witness bump
    return new


def VIEW(cell: "Cell") -> Any:
    """Read a cell's value (pure projection)."""
    return cell.value


def TICK(dt: float = 0.016) -> None:
    """Advance the substrate clock. ~60Hz default."""
    time.sleep(dt)


def FORGET(cell: "Cell") -> None:
    """Retire a cell. Runs all effects in reverse order."""
    for fn, inverse in reversed(cell._effects):
        try:
            inverse(cell.value)
        except Exception:
            pass
    cell._effects = []
    cell.value = None
    cell._bound = False


# ---------------------------------------------------------------------------
# The cell base + Link
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    """The Quilt cell — the irreducible unit of the substrate.

    Same shape as quilt-cordis Cell, but with axes (topology of nearby
    addresses) and confidence (witness of durability).
    """
    address: str
    value: Any = None
    axes: Tuple[str, ...] = ()
    confidence: float = 1.0
    _effects: List[Tuple[Callable, Callable]] = field(default_factory=list)
    _bound: bool = False

    def __post_init__(self):
        BIND(self)

    def effect(self, fn, inverse=None):
        return EFFECT(self, fn)

    def dispose(self):
        FORGET(self)


@dataclass
class Link:
    """A typed edge between two cells. Used for FK, patterns, controls."""
    source: str
    target: str
    edge_type: str = "default"
    confidence: float = 1.0


@dataclass
class Substrate:
    """The Countroller substrate — a hosted cell-graph with a name."""
    name: str
    cells: Dict[str, Cell] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)
    witness: List[str] = field(default_factory=list)

    def bind(self, cell: Cell) -> Cell:
        BIND(cell)
        self.cells[cell.address] = cell
        self.witness.append(f"BIND {cell.address} @ tick={len(self.witness)}")
        return cell

    def link(self, source_addr: str, target_addr: str, edge_type: str = "default") -> Link:
        edge = Link(source_addr, target_addr, edge_type)
        self.links.append(edge)
        self.witness.append(f"LINK {source_addr}→{target_addr} ({edge_type}) @ tick={len(self.witness)}")
        return edge

    def effect(self, addr: str, fn: Callable[[Any], Any]) -> Any:
        cell = self.cells[addr]
        result = EFFECT(cell, fn)
        self.witness.append(f"EFFECT {addr} → {result} @ tick={len(self.witness)}")
        return result

    def view(self, addr: str) -> Any:
        return VIEW(self.cells[addr])

    def tick(self, dt: float = 0.016):
        TICK(dt)
        self.witness.append(f"TICK dt={dt:.3f} @ tick={len(self.witness)}")

    def forget(self, addr: str):
        FORGET(self.cells[addr])
        self.witness.append(f"FORGET {addr} @ tick={len(self.witness)}")


# ---------------------------------------------------------------------------
# Countroller-specific cell types
# ---------------------------------------------------------------------------

class JoystickCell(Cell):
    """Joystick X/Y position as a (x, y) tuple in [-1, 1].

    Upstream: ADC channels, normalized to 12-bit precision. Confidence
    drops slightly with each sample (signal noise on the ADC).
    """
    def __init__(self, address: str = "joystick"):
        super().__init__(address=address, value=(0.0, 0.0), axes=("x", "y"), confidence=1.0)

    def update(self, x: float, y: float):
        """Read new joystick position (normalized -1..1)."""
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        self.value = (x, y)
        # Confidence drops with magnitude (real ADCs are noisier at extremes)
        self.confidence = 1.0 - 0.05 * (abs(x) + abs(y)) / 2.0


class ButtonCell(Cell):
    """A pushbutton. Value is the press count (matches upstream semantics)."""
    def __init__(self, address: str, label: str):
        super().__init__(address=address, value=0, axes=("count",), confidence=1.0)
        self.label = label

    def press(self):
        self.value += 1
        self.confidence = 1.0  # discrete event, clean signal


class JoystickButtonCell(Cell):
    """The joystick's center click. Same shape as ButtonCell but linked
    to both counter streams on press (matches upstream behavior)."""
    def __init__(self, address: str = "joystick_button"):
        super().__init__(address=address, value=0, axes=("count",), confidence=1.0)

    def press(self):
        self.value += 1
        self.confidence = 1.0


class LEDCell(Cell):
    """One NeoPixel LED. Value is (r, g, b) in 0-255.

    25 of these form the 5×5 matrix; the substrate's `led_at(x, y)` helper
    addresses them by Cartesian position.
    """
    def __init__(self, address: str, x: int = 0, y: int = 0):
        super().__init__(address=address, value=(0, 0, 0), axes=("x", "y"), confidence=1.0)
        self.position = (x, y)

    def set_color(self, r: int, g: int, b: int):
        # Clamp to 0-255 (matches WS2812 hardware constraints)
        self.value = (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


class BuzzerCell(Cell):
    """A PWM buzzer. Value is frequency in Hz (0 = silent)."""
    def __init__(self, address: str, frequency: int = 0):
        super().__init__(address=address, value=frequency, axes=("freq",), confidence=1.0)

    def buzz(self, freq: int = 1000, duration_ms: int = 100):
        """Match upstream: buzz at frequency, then silence."""
        self.value = freq
        self.confidence = 0.95
        # In the simulator we don't actually sleep; in firmware, sleep_ms(duration_ms)

    def silence(self):
        self.value = 0


class OLEDCell(Cell):
    """The OLED display. Value is the current text message."""
    def __init__(self, address: str = "oled"):
        super().__init__(address=address, value="", axes=("text",), confidence=1.0)

    def display(self, msg: str):
        self.value = msg[:32]  # upstream is 32-char display
