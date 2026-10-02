#!/usr/bin/env python3
"""Spline Snaps — discretize continuous analogue trajectories into canonical anchors.

The substrate is continuous (analogue). The canon is discrete (digital).
The spline is the bridge: choose snaps (time, position, embedding) such that
the spline interpolating them matches the substrate to within epsilon.

Each snap is a witness entry. The snaps are first-class; the spline is derived.
"""
import numpy as np
import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Optional

@dataclass
class Snap:
    """A canonical anchor at a chosen moment in time and space."""
    snap_id: str
    t: float  # time coordinate (can be negative for t-minus)
    position: tuple  # (x, y, z) in substrate space
    embedding: tuple  # observed state at this snap
    hash: str  # FNV-1a hash of (t, position, embedding)
    observer: str  # which witness recorded this snap
    sim_id: str = "default"  # which simulation this belongs to
    room_id: str = "main"  # which room (joint-space)
    extra_dims: dict = field(default_factory=dict)  # extra axes (e.g., quantum basis)
    parent_snap: Optional[str] = None  # causal predecessor
    children_snaps: List[str] = field(default_factory=list)  # causal successors

    @classmethod
    def make(cls, t, position, embedding, observer="witness", sim_id="default",
             room_id="main", extra_dims=None, parent=None):
        h = hashlib.sha256(
            f"{t}|{position}|{embedding}|{observer}|{sim_id}|{room_id}".encode()
        ).hexdigest()[:16]
        return cls(
            snap_id=h, t=t, position=tuple(position), embedding=tuple(embedding),
            hash=h, observer=observer, sim_id=sim_id, room_id=room_id,
            extra_dims=extra_dims or {}, parent_snap=parent, children_snaps=[]
        )


def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for c in s.encode():
        h ^= c
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h


def catmull_rom_spline(snaps: List[Snap], t_query: float) -> np.ndarray:
    """Catmull-Rom spline interpolation through snaps.
    
    A Catmull-Rom spline passes through all control points (snaps) and uses
    tangent vectors from neighboring points for smooth interpolation.
    
    Returns: the interpolated embedding at t_query.
    """
    if not snaps:
        return np.zeros(0)
    if len(snaps) == 1:
        return np.array(snaps[0].embedding)
    
    # Sort by time
    snaps = sorted(snaps, key=lambda s: s.t)
    times = [s.t for s in snaps]
    
    # Find bracketing segment
    if t_query <= times[0]:
        return np.array(snaps[0].embedding)
    if t_query >= times[-1]:
        return np.array(snaps[-1].embedding)
    
    for i in range(len(snaps) - 1):
        if times[i] <= t_query <= times[i+1]:
            # Get 4 control points (or fewer at boundaries)
            p0 = np.array(snaps[max(0, i-1)].embedding)
            p1 = np.array(snaps[i].embedding)
            p2 = np.array(snaps[i+1].embedding)
            p3 = np.array(snaps[min(len(snaps)-1, i+2)].embedding)
            
            # Parameterize in segment
            t0, t1 = times[i], times[i+1]
            t_norm = (t_query - t0) / (t1 - t0) if t1 > t0 else 0
            
            # Catmull-Rom basis
            t2 = t_norm * t_norm
            t3 = t2 * t_norm
            
            # Standard Catmull-Rom
            result = 0.5 * (
                (2 * p1) +
                (-p0 + p2) * t_norm +
                (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
                (-p0 + 3*p1 - 3*p2 + p3) * t3
            )
            return result
    
    return np.array(snaps[-1].embedding)


def main():
    print('=== Spline Snaps — Canonical Anchors ===\n')
    
    # Create a trajectory of snaps along the substrate
    snaps = []
    
    # Sim 1, Room A: a smooth arc through 4D space
    snaps.append(Snap.make(t=-10.0, position=(0, 0, 0), embedding=(1.0, 0.0, 0.0, 0.0),
                           observer="witness-α", sim_id="cosmic", room_id="A",
                           extra_dims={"quantum_basis": "|+⟩", "lens": "panorama"}))
    snaps.append(Snap.make(t=-5.0, position=(1, 0, 0), embedding=(0.5, 0.5, 0.5, 0.5),
                           sim_id="cosmic", room_id="A",
                           extra_dims={"quantum_basis": "|+⟩", "lens": "panorama"},
                           parent=snaps[0].snap_id))
    snaps.append(Snap.make(t=0.0, position=(2, 1, 0), embedding=(0.0, 1.0, 0.0, 0.0),
                           sim_id="cosmic", room_id="A",
                           extra_dims={"quantum_basis": "|+⟩", "lens": "panorama"},
                           parent=snaps[1].snap_id))
    snaps.append(Snap.make(t=5.0, position=(3, 1, 1), embedding=(0.0, 0.0, 1.0, 0.0),
                           sim_id="cosmic", room_id="A",
                           extra_dims={"quantum_basis": "|+⟩", "lens": "panorama"},
                           parent=snaps[2].snap_id))
    snaps.append(Snap.make(t=10.0, position=(4, 2, 1), embedding=(0.0, 0.0, 0.0, 1.0),
                           sim_id="cosmic", room_id="A",
                           extra_dims={"quantum_basis": "|+⟩", "lens": "panorama"},
                           parent=snaps[3].snap_id))
    
    # Sim 2, Room B: a different trajectory (will produce a different interpolation)
    snaps.append(Snap.make(t=-10.0, position=(0, 0, 0), embedding=(1.0, 0.0, 0.0, 0.0),
                           observer="witness-β", sim_id="quantum", room_id="B",
                           extra_dims={"quantum_basis": "|0⟩", "lens": "microscope"}))
    snaps.append(Snap.make(t=-5.0, position=(0, 1, 0), embedding=(0.5, 0.5, 0.5, 0.5),
                           sim_id="quantum", room_id="B",
                           extra_dims={"quantum_basis": "|0⟩", "lens": "microscope"},
                           parent=snaps[5].snap_id))
    snaps.append(Snap.make(t=0.0, position=(0, 2, 0), embedding=(0.0, 1.0, 0.0, 0.0),
                           sim_id="quantum", room_id="B",
                           extra_dims={"quantum_basis": "|0⟩", "lens": "microscope"},
                           parent=snaps[6].snap_id))
    snaps.append(Snap.make(t=5.0, position=(0, 3, 0), embedding=(0.0, 0.0, 1.0, 0.0),
                           sim_id="quantum", room_id="B",
                           extra_dims={"quantum_basis": "|0⟩", "lens": "microscope"},
                           parent=snaps[7].snap_id))
    
    print(f'Created {len(snaps)} snaps across {len(set(s.sim_id for s in snaps))} sims')
    print(f'Time range: [{min(s.t for s in snaps)}, {max(s.t for s in snaps)}]')
    print()
    
    # Show snaps
    print('--- All snaps ---')
    for s in snaps:
        print(f'  snap {s.snap_id}  sim={s.sim_id} room={s.room_id}  t={s.t:+.1f}  pos={s.position}  emb_len={len(s.embedding)}')
    print()
    
    # Test interpolation along each trajectory
    print('--- Spline interpolation along each trajectory ---')
    query_times = [-7.5, -2.5, 2.5, 7.5]
    for sim in ['cosmic', 'quantum']:
        sim_snaps = [s for s in snaps if s.sim_id == sim]
        print(f'\n  Sim: {sim}')
        for t_q in query_times:
            emb = catmull_rom_spline(sim_snaps, t_q)
            print(f'    t={t_q:+.1f}  →  embedding ≈ {tuple(round(x, 3) for x in emb)}')
    
    # Save
    out = {
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'concept': 'spline_snaps',
        'description': 'Canonical snaps along continuous analogue trajectories',
        'n_snaps': len(snaps),
        'n_sims': len(set(s.sim_id for s in snaps)),
        'n_rooms': len(set(s.room_id for s in snaps)),
        'sample_snaps': [asdict(s) for s in snaps[:3]],
    }
    with open('/workspace/research/analogue_substrate/spline_snaps.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: /workspace/research/analogue_substrate/spline_snaps.json')


if __name__ == '__main__':
    main()
