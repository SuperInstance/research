#!/usr/bin/env python3
"""CadenceOracle — Task completion signal mapped to JEV confidence.

Inspired by agent-cadence-progress (Rust crate by SuperInstance).
5 cadence types mapped to JEV oracle states. Calibrated against real
canon stress-test verdicts.

Mapping (based on observed JEV behavior):
- PerfectAuthentic: ACCEPT verdict, mean_p >= 0.78
- Plagal: REVIEW verdict, mean_p 0.65-0.78
- Deceptive: DISCUSS verdict (mean_p 0.40-0.65, looks canon but isn't)
- Half: parked, mean_p 0.20-0.40
- Phrygian: REJECT verdict, mean_p < 0.20
"""
import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class Cadence(Enum):
    PerfectAuthentic = "perfect_authentic"  # V → I
    Plagal = "plagal"                       # IV → I
    Deceptive = "deceptive"                 # V → vi
    Half = "half"                           # → V
    Phrygian = "phrygian"                   # ↓v → V

@dataclass
class CadenceSignal:
    cadence: Cadence
    confidence: float  # 0.0 - 1.0 (mean_p from JEV)
    description: str

    @classmethod
    def from_mean_p(cls, mean_p: float) -> 'CadenceSignal':
        """Map JEV mean_p to a cadence signal."""
        if mean_p >= 0.78:
            return cls(
                cadence=Cadence.PerfectAuthentic,
                confidence=mean_p,
                description=f"Full resolution — canon (mean_p={mean_p:.3f})",
            )
        elif mean_p >= 0.65:
            return cls(
                cadence=Cadence.Plagal,
                confidence=mean_p,
                description=f"Gentle resolution — canon-leaning (mean_p={mean_p:.3f})",
            )
        elif mean_p >= 0.40:
            return cls(
                cadence=Cadence.Deceptive,
                confidence=mean_p,
                description=f"False resolution — speculative (mean_p={mean_p:.3f})",
            )
        elif mean_p >= 0.20:
            return cls(
                cadence=Cadence.Half,
                confidence=mean_p,
                description=f"Suspension — parked (mean_p={mean_p:.3f})",
            )
        else:
            return cls(
                cadence=Cadence.Phrygian,
                confidence=mean_p,
                description=f"Dramatic pause — rejected (mean_p={mean_p:.3f})",
            )

    def is_resolved(self) -> bool:
        return self.cadence in (Cadence.PerfectAuthentic, Cadence.Plagal)

    def resolution_strength(self) -> float:
        return {
            Cadence.PerfectAuthentic: 1.0,
            Cadence.Plagal: 0.85,
            Cadence.Deceptive: 0.30,
            Cadence.Half: 0.10,
            Cadence.Phrygian: 0.05,
        }[self.cadence]

    def to_dict(self) -> dict:
        return {
            'cadence': self.cadence.value,
            'confidence': self.confidence,
            'description': self.description,
            'resolution_strength': self.resolution_strength(),
            'is_resolved': self.is_resolved(),
        }


class CadenceOracle:
    """Track task completion across multiple cadence signals."""
    def __init__(self, name: str):
        self.name = name
        self.signals: List[CadenceSignal] = []

    def add(self, signal: CadenceSignal):
        self.signals.append(signal)

    def from_mean_p(self, mean_p: float) -> CadenceSignal:
        sig = CadenceSignal.from_mean_p(mean_p)
        self.add(sig)
        return sig

    def summary(self) -> dict:
        if not self.signals:
            return {'n': 0}
        kinds = {}
        for s in self.signals:
            kinds[s.cadence.value] = kinds.get(s.cadence.value, 0) + 1
        # Net resolution: sum of resolution_strengths
        total_res = sum(s.resolution_strength() for s in self.signals)
        max_res = len(self.signals) * 1.0
        return {
            'name': self.name,
            'n_signals': len(self.signals),
            'kinds': kinds,
            'mean_resolution': total_res / max_res,
            'current_cadence': self.signals[-1].cadence.value,
            'current_strength': self.signals[-1].resolution_strength(),
        }


def main():
    """Demo: track JEV results for several canon pieces, output cadence summary."""
    oracle = CadenceOracle("Canon Stress Test")

    # Real JEV verdicts from Session 22 (WR17/18) + earlier stress-test
    test_cases = [
        # ACCEPT (PerfectAuthentic)
        ("wr17-zai", 0.836),
        ("wr17-ds", 0.831),
        ("wr17-curated", 0.830),
        ("wr18-zai", 0.819),
        ("wr18-ds", 0.815),
        # ACCEPT-edge (Plagal → still canon-leaning)
        ("wr18-curated", 0.785),
        ("wr15-zai", 0.713),
        ("wr15-ds", 0.684),
        ("wr16-curated", 0.750),
        ("wr14-zai", 0.741),
        # REVIEW (Plagal)
        ("polyformalism-as-canon", 0.731),
        ("dice", 0.761),
        ("chained-witness-log", 0.754),
        ("radio-pirate", 0.764),
        # DISCUSS / speculative (Deceptive)
        ("alignment-kills", 0.450),
        ("spec_chain_speaks", 0.41),
        ("proc_prove_jev", 0.46),
        # Parked (Half)
        ("wrapped-in-scar", 0.30),
        # REJECT (Phrygian)
        ("11-opcodes", 0.117),
        ("13-ports", 0.096),
        ("cells-are-parameters", 0.04),
        ("substrate-is-designed", 0.03),
    ]

    print('=== Cadence Oracle — Canon Stress Test ===\n')
    for name, mean_p in test_cases:
        sig = oracle.from_mean_p(mean_p)
        marker = '✓' if sig.is_resolved() else '✗'
        print(f'  {marker} {name:25s}  cadence={sig.cadence.value:18s}  strength={sig.resolution_strength():.2f}  p={mean_p:.3f}')

    print()
    summary = oracle.summary()
    print(f'Summary:')
    print(f'  Total signals: {summary["n_signals"]}')
    print(f'  Mean resolution: {summary["mean_resolution"]:.3f}')
    print(f'  Current cadence: {summary["current_cadence"]} (strength={summary["current_strength"]})')
    print(f'  Distribution: {summary["kinds"]}')

    # Save as JSON for integration
    out = {
        'name': oracle.name,
        'signals': [s.to_dict() for s in oracle.signals],
        'summary': summary,
    }
    with open('/workspace/research/cadence_oracle_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'\nSaved: /workspace/research/cadence_oracle_results.json')


if __name__ == '__main__':
    main()
