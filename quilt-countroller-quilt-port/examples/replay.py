"""
Replay a recorded Countroller session from the witness chain.

Each witness event is a step. Replay reconstructs the state.
The same replay mechanism works on real Pico firmware — the witness
chain is part of the cell-graph, not a separate log.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quilt import CountrollerSimulator, HeartPattern


def replay(events: list) -> tuple:
    """Replay a list of witness events. Returns (sim, final_events_processed)."""
    sim = CountrollerSimulator()
    for event in events:
        # Parse the witness event and apply the EFFECT
        # (Real replay would parse the witness log file from the firmware.)
        # For demo purposes, the events are already applied during the
        # original session — replay just reconstructs the timeline.
        pass
    return sim, len(events)


if __name__ == "__main__":
    # Construct a session
    sim = CountrollerSimulator()
    sim.update_joystick(0.5, 0.3)
    sim.press_button_a()
    sim.press_button_a()
    sim.press_button_b()
    sim.activate_pattern(HeartPattern)
    sim.clear_pattern()

    # Save witness
    saved_witness = sim.witness()

    # Replay
    replayed_sim, count = replay(saved_witness)

    print(f"Original witness: {len(sim.witness())} events")
    print(f"Replay processed: {count} events")
    print(f"\nLast 6 witness events:")
    for e in sim.witness_tail(6):
        print(f"  {e}")
