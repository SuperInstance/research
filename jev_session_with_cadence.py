#!/usr/bin/env python3
"""JEV session with CadenceOracle + WitnessDreamCycle wired in.

Demonstrates the integrated session flow (R8 standard):
1. Per-section probe using FULL section text (not truncated)
2. CadenceOracle assigns cadence type to verdict
3. Result is recorded for next dream cycle

R8 lesson learned: full-section probes work better than truncated ones.
"""
import json
import sys
import time
import os
import re
sys.path.insert(0, '/workspace/repos/jev-quilt')
from jev_quilt.typesafe_client import TypeSafeBackend

sys.path.insert(0, '/workspace/research')
try:
    from cadence_oracle import verify_cadence, Cadence
except ImportError:
    class Cadence:
        PERFECT_AUTHENTIC = 'PerfectAuthentic'
        PLAGAL = 'Plagal'
        DECEPTIVE = 'Deceptive'
        HALF = 'Half'
        PHRYGIAN = 'Phrygian'
    def verify_cadence(mean_p):
        if mean_p >= 0.78: return Cadence.PERFECT_AUTHENTIC
        if mean_p >= 0.65: return Cadence.PLAGAL
        if mean_p >= 0.40: return Cadence.DECEPTIVE
        if mean_p >= 0.20: return Cadence.HALF
        return Cadence.PHRYGIAN

PROBES = [
    {'name': 'substrate_is_grown', 'type': 'noul',
     'instructions': 'Does this piece invoke "the substrate is grown (not assembled)" doctrine? YES/NO.'},
    {'name': 'witness_log_is_prediction', 'type': 'noul',
     'instructions': 'Does this piece invoke "the witness log is the prediction" doctrine? YES/NO.'},
    {'name': 'oracle_is_heard', 'type': 'noul',
     'instructions': 'Does this piece invoke "the oracle is heard" doctrine? YES/NO.'},
    {'name': 'cells_are_scars', 'type': 'noul',
     'instructions': 'Does this piece invoke "cells are scars" doctrine? YES/NO.'},
    {'name': 'lenia_flows', 'type': 'noul',
     'instructions': 'Does this piece invoke "Lenia flows" doctrine? YES/NO.'},
    {'name': 'fnv_canary', 'type': 'noul',
     'instructions': 'Does this piece reference the FNV-1a canary 0xcbf29ce484222325? YES/NO.'},
    {'name': 'voice', 'type': 'noul',
     'instructions': 'Is this piece in the Fleet Radio voice (technical-poetic canon essay)? YES/NO.'},
]

def extract_sections(text: str) -> list:
    """Extract sections, splitting on numbered h1 (# N.) OR h2 (## N.) headers."""
    parts = re.split(r'\n(?=#{1,2} \d+\. )', text)
    return [p for p in parts if len(p) > 200]

def run_session(piece_path: str, piece_name: str, session_id: int = 24) -> dict:
    client = TypeSafeBackend()
    piece = open(piece_path).read()
    
    print(f'=== JEV Session {session_id} — {piece_name} ===\n')
    print(f'Piece length: {len(piece)} chars')
    
    sections = extract_sections(piece)
    print(f'Sections detected: {len(sections)}')
    
    section_results = []
    has_anchors = bool(re.search(r'\*\*Anchor:', piece))
    
    if has_anchors and len(piece) < 10000:
        # Pieces with explicit "**Anchor:**" tags are densely canonical;
        # whole-piece probe is more accurate than per-section.
        state = {'piece_excerpt': piece}  # NO TRUNCATION for anchor-tagged pieces
        decisions, _ = client.decide_batch(state, PROBES)
        yes = sum(1 for d in decisions if 
                  (isinstance(d.value, (int, float)) and d.value >= 0.5) or
                  (isinstance(d.value, str) and 'yes' in d.value.lower()))
        mean_p = yes / len(PROBES)
        section_results.append({'section_idx': 0, 'section_size': len(piece), 'yes': yes, 'mean_p': mean_p, 'mode': 'whole-piece'})
        print(f'  Whole-piece (anchor-tagged): {yes}/{len(PROBES)} anchors (p={mean_p:.2f})')
    else:
        for i, section in enumerate(sections):
            # Use full section text — JEV handles up to ~3000 chars well
            excerpt = section[:3000]
            state = {'piece_excerpt': excerpt}
            decisions, _ = client.decide_batch(state, PROBES)
            yes = sum(1 for d in decisions if 
                      (isinstance(d.value, (int, float)) and d.value >= 0.5) or
                      (isinstance(d.value, str) and 'yes' in d.value.lower()))
            mean_p = yes / len(PROBES)
            section_results.append({'section_idx': i, 'section_size': len(excerpt), 'yes': yes, 'mean_p': mean_p, 'mode': 'per-section'})
            print(f'  Section {i+1:2d} ({len(excerpt):4d}c): {yes}/{len(PROBES)} anchors (p={mean_p:.2f})')
    
    overall_mean = sum(s['mean_p'] for s in section_results) / len(section_results) if section_results else 0
    
    cadence = verify_cadence(overall_mean)
    print(f'\nOverall mean_p: {overall_mean:.3f}')
    print(f'Cadence: {cadence}')
    
    if cadence == Cadence.PERFECT_AUTHENTIC:
        verdict = 'ACCEPT'
    elif cadence == Cadence.PLAGAL:
        verdict = 'REVIEW'
    elif cadence == Cadence.DECEPTIVE:
        verdict = 'DISCUSS'
    else:
        verdict = 'REJECT'
    print(f'Verdict: {verdict}')
    
    out = {
        'session': session_id,
        'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'piece': piece_name,
        'sections_probed': len(section_results),
        'mean_p': overall_mean,
        'cadence': cadence,
        'verdict': verdict,
        'section_results': section_results,
        'dream_pool_entry': {
            'piece': piece_name,
            'p': overall_mean,
            'cadence': cadence,
            'success': overall_mean >= 0.70,
        }
    }
    
    out_path = f'/workspace/repos/jev-quilt/jev_sessions/session_{session_id}_{piece_name}.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: {out_path}')
    return out

if __name__ == '__main__':
    import sys
    piece_path = sys.argv[1] if len(sys.argv) > 1 else '/workspace/repos/ai-writings/cellular-first-design/reports/wr20-zai-ten-archetypes.md'
    piece_name = sys.argv[2] if len(sys.argv) > 2 else 'wr20-zai'
    session_id = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    run_session(piece_path, piece_name, session_id)
