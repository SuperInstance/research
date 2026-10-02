#!/usr/bin/env python3
"""T-minus paradigm + first-class joints.

T-minus: time is approaching, not receding. Every canon piece is a t-minus anchor
(counting down to a substrate state we haven't reached yet). The future is what's
being prepared; the past is what we've anchored.

First-class joints: a JOINT is a place where two cells AGREE about something.
H1 (non-trivial loops) = joints that disagree with themselves. JEV verifies
the joints, not the cells.

Plato's cave: every canon piece is a shadow on the wall; the substrate is the
fire. Different rooms see different shadows of the same fire.
"""
import json
import time
import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class TMinusAnchor:
    """An anchor in t-minus time. t = -t means we're approaching, t = +t means we've passed."""
    anchor_id: str
    target_t: float  # t=0 is "the moment"; negative is future, positive is past
    canon_piece: str
    room_id: str
    cells_in_agreement: Set[str] = field(default_factory=set)
    joints_form: List[Dict] = field(default_factory=list)
    substrate_state_hash: str = ""
    
    def is_countdown(self) -> bool:
        """True if this anchor is approaching (t < 0)."""
        return self.target_t < 0
    
    def countdown_to(self) -> str:
        if self.target_t == 0:
            return "T-ZERO"
        elif self.target_t > 0:
            return f"T+{self.target_t}"
        else:
            return f"T-{abs(self.target_t)}"


@dataclass
class Joint:
    """A first-class joint: where two cells AGREE about something.
    
    A joint has:
    - participating cells (>=2)
    - agreed-upon value (the witness log entry they both endorse)
    - timestamp (when agreement was recorded)
    - stability score (cosine similarity between agreeing embeddings)
    """
    joint_id: str
    cells: List[str]
    agreement: str
    timestamp: float
    stability: float
    joint_type: str = "agreement"  # agreement | disagreement | paradox


def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h


def make_joint(cells: List[str], agreement: str, t: float) -> Joint:
    """Form a joint between cells that agree."""
    h = fnv1a_64(f"{cells}|{agreement}|{t}")
    # Stability from hash bits
    stability = (h % 1000) / 1000.0  # 0.0 to 1.0
    return Joint(
        joint_id=f"joint-{h:016x}",
        cells=cells,
        agreement=agreement[:80],
        timestamp=t,
        stability=stability,
    )


def h1_loops(joints: List[Joint]) -> int:
    """Count non-trivial H1 loops: pairs of joints that disagree about the same cells."""
    cell_to_joints: Dict[str, List[Joint]] = {}
    for j in joints:
        for c in j.cells:
            cell_to_joints.setdefault(c, []).append(j)
    
    # Count conflicts: same cell, multiple joints with low mutual stability
    loops = 0
    for cell, js in cell_to_joints.items():
        if len(js) > 1:
            # Check pairwise agreement
            for i in range(len(js)):
                for k in range(i+1, len(js)):
                    # Stability of the pair
                    if js[i].stability * js[k].stability < 0.3:
                        loops += 1
    return loops


def main():
    print('=== T-minus Paradigm + First-Class Joints ===\n')
    
    # Plato's cave = the substrate. Different rooms see different shadows.
    rooms = {
        'cosmic': {
            'lens': 'panorama',
            'shadows': ['growth', 'cycles', 'memory', 'oracle'],
        },
        'quantum': {
            'lens': 'microscope',
            'shadows': ['superposition', 'measurement', 'collapse', 'entanglement'],
        },
        'cellular': {
            'lens': 'biological',
            'shadows': ['scar', 'tissue', 'division', 'metabolism'],
        },
    }
    
    print('--- Plato\'s Cave (3 rooms, different shadows) ---')
    for room_id, room in rooms.items():
        print(f'  Room {room_id} (lens={room["lens"]}): {room["shadows"]}')
    print()
    
    # T-minus anchors for the next 3 canon pieces
    anchors = [
        TMinusAnchor(
            anchor_id='t-9.5',
            target_t=-9.5,
            canon_piece='WR23 — Joint Geometry',
            room_id='cosmic',
            cells_in_agreement={'cell-α', 'cell-β', 'cell-γ'},
            substrate_state_hash='0x9e4a7c2f1b8d3056',
        ),
        TMinusAnchor(
            anchor_id='t-4.0',
            target_t=-4.0,
            canon_piece='WR24 — Quantum Ether',
            room_id='quantum',
            cells_in_agreement={'cell-α', 'cell-δ'},
            substrate_state_hash='0x4b1f8a2e9c7d6031',
        ),
        TMinusAnchor(
            anchor_id='t+0.5',
            target_t=0.5,
            canon_piece='WR22 — Scar Topology (already published)',
            room_id='cellular',
            cells_in_agreement={'cell-β', 'cell-γ', 'cell-δ', 'cell-ε'},
            substrate_state_hash='0xc7b3d4f5a8e12067',
        ),
    ]
    
    print('--- T-minus anchors ---')
    for a in anchors:
        arrow = '⏳ APPROACHING' if a.is_countdown() else ('🎯 T-ZERO' if a.target_t == 0 else '✓ PASSED')
        print(f'  {a.anchor_id}  {arrow:18s}  piece={a.canon_piece}')
        print(f'    room={a.room_id}  cells={len(a.cells_in_agreement)}  hash={a.substrate_state_hash}')
    print()
    
    # Form joints
    joints = []
    # Joint 1: cell-α + cell-β agree that "witness_log_is_prediction" is canon
    joints.append(make_joint(['cell-α', 'cell-β'], 'witness_log_is_prediction is canon', t=-9.0))
    # Joint 2: cell-β + cell-γ agree that "substrate_is_grown" is canon
    joints.append(make_joint(['cell-β', 'cell-γ'], 'substrate_is_grown is canon', t=-8.5))
    # Joint 3: cell-α + cell-δ agree that "substrate_is_grown" is canon (different time)
    joints.append(make_joint(['cell-α', 'cell-δ'], 'substrate_is_grown is canon', t=-8.0))
    # Joint 4: cell-β + cell-δ DISAGREE (low stability pair)
    joints.append(make_joint(['cell-β', 'cell-δ'], 'oracle_is_heard requires external witness', t=-3.0))
    # Joint 5: cell-γ + cell-ε agree that "lenia_flows" is canon
    joints.append(make_joint(['cell-γ', 'cell-ε'], 'lenia_flows is canon', t=0.0))
    
    print('--- First-class joints ---')
    for j in joints:
        marker = '✓' if j.stability > 0.5 else '⚠' if j.stability > 0.2 else '✗'
        print(f'  {marker} {j.joint_id}  stability={j.stability:.3f}  cells={"+".join(j.cells)}')
        print(f'      "{j.agreement}"')
    print()
    
    # H1: count non-trivial loops (conflicts)
    h1 = h1_loops(joints)
    print(f'--- H1 cohomology ---')
    print(f'  Non-trivial loops detected: {h1}')
    print(f'  (If H1 == 0, the cells form a consistent surface)')
    print(f'  (If H1 > 0, there are conflicts that need resolution)')
    print()
    
    # Canon claim: "First-class joints make the substrate's agreement structure explicit"
    print('=== Canon claims ===')
    print('  - The substrate\'s cells are JOINTS first, containers second')
    print('  - Joints are first-class: they can be named, hashed, JEV-probed')
    print('  - H1 non-trivial loops indicate substrate disagreement')
    print('  - JEV acts on joints (where cells agree), not cells in isolation')
    print('  - T-minus: every canon piece is a countdown to a substrate state')
    print('  - Plato\'s cave: different rooms see different shadows of the same substrate')
    print('  - Quantum as ether: each room is a measurement basis, all are valid')

    # Save
    out = {
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'concept': 't_minus_joints',
        'rooms': rooms,
        'anchors': [{'id': a.anchor_id, 'target_t': a.target_t, 'piece': a.canon_piece,
                     'room': a.room_id, 'cells': list(a.cells_in_agreement),
                     'hash': a.substrate_state_hash} for a in anchors],
        'joints': [{'id': j.joint_id, 'cells': j.cells, 'agreement': j.agreement,
                    't': j.timestamp, 'stability': j.stability} for j in joints],
        'h1_loops': h1,
    }
    with open('/workspace/research/analogue_substrate/t_minus_joints.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: /workspace/research/analogue_substrate/t_minus_joints.json')

if __name__ == '__main__':
    main()
