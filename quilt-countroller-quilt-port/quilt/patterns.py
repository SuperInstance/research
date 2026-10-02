"""
LED patterns for the Countroller substrate.

Upstream supports 3 patterns: heart, IF (the EmbarcaTech institute initials),
PI. Each is a static layout — a 5×5 boolean grid.

The patterns are first-class Quilt citizens: they become typed LINK-graphs
between LED cells. `bind_pattern_to_leds()` creates the LINKs.
`render_pattern()` colors the LEDs (red for filled, off for empty).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .cells import LEDCell, Link


# ---------------------------------------------------------------------------
# Pattern data — 5×5 boolean grids
# ---------------------------------------------------------------------------

# Heart (matching upstream neopixel.c heart_pattern[5][5])
HEART: List[List[bool]] = [
    [False, True,  True,  True,  False],
    [True,  True,  True,  True,  True],
    [True,  True,  True,  True,  True],
    [False, True,  True,  True,  False],
    [False, False, True,  False, False],
]

# IF (Instituto Federal — EmbarcaTech capstone initials)
# Stylized: vertical bar on left + two horizontals + small bar on right
IF: List[List[bool]] = [
    [True,  True,  True,  False, False],
    [True,  False, False, False, True],
    [True,  True,  True,  False, False],
    [True,  False, False, False, True],
    [True,  False, False, False, True],
]

# PI (π) — stylized: two verticals + horizontal at top + center column
PI: List[List[bool]] = [
    [True,  True,  True,  True,  True],
    [True,  False, False, False, False],
    [True,  False, True,  False, False],
    [True,  False, False, False, False],
    [True,  False, False, False, False],
]


@dataclass
class Pattern:
    """A 5×5 LED pattern as a graph of typed links."""
    name: str
    grid: List[List[bool]]
    color: Tuple[int, int, int] = (255, 0, 0)  # red by default

    def cells_with_color(self) -> List[Tuple[int, int]]:
        """Return (x, y) positions of cells that should be lit."""
        return [
            (x, y)
            for y in range(5)
            for x in range(5)
            if self.grid[y][x]
        ]


HeartPattern = Pattern(name="heart", grid=HEART, color=(255, 0, 0))
IfPattern = Pattern(name="if", grid=IF, color=(0, 255, 0))
PiPattern = Pattern(name="pi", grid=PI, color=(0, 100, 255))


# ---------------------------------------------------------------------------
# Pattern → typed LINK graph
# ---------------------------------------------------------------------------

def bind_pattern_to_leds(pattern: Pattern, leds: Dict[Tuple[int, int], LEDCell]) -> List[Link]:
    """Create typed LINKs from the pattern's lit cells to the LED cells.

    The edge_type is `'renders:<pattern_name>:<x>,<y>'` so the substrate's
    LINK-graph carries the pattern semantics explicitly.

    Returns the list of Links created.
    """
    links = []
    for x, y in pattern.cells_with_color():
        led = leds.get((x, y))
        if led is not None:
            edge_type = f"renders:{pattern.name}:{x},{y}"
            link = Link(source=f"pattern:{pattern.name}", target=led.address, edge_type=edge_type)
            links.append(link)
    return links


def render_pattern(pattern: Pattern, leds: Dict[Tuple[int, int], LEDCell]) -> int:
    """Apply the pattern to the LED cells. Returns count of LEDs lit.

    This is the EFFECT-side of the LINK-graph: when the pattern activates,
    each linked LED cell gets its color set.
    """
    count = 0
    for x, y in pattern.cells_with_color():
        led = leds.get((x, y))
        if led is not None:
            led.set_color(*pattern.color)
            count += 1
    return count


def clear_pattern(leds: Dict[Tuple[int, int], LEDCell]) -> None:
    """Clear all LEDs (set to off)."""
    for led in leds.values():
        led.set_color(0, 0, 0)
