"""observation-primitive: canonical substrate atom.

Distilled from R10 reverse-engineering. observation = subject/predicate/object/issuer/time/evidence/signature.

Inspired by evintunador/context-graph: every observation carries the evidence that justifies it.
"""
from typing import Any, Optional, Union
import json
import time as _time

__all__ = [
    "Observation",
    "OPCODES",
    "EVIDENCE",
    "FORGETTING",
    "fnv1a64",
    "fnv1a64_hex",
    "int16_dials",
]

FNV_OFFSET = 0xcbf29ce484222325
FNV_PRIME = 0x100000001b3
MASK_64 = 0xffffffffffffffff


def fnv1a64(s: Union[str, bytes, bytearray]) -> int:
    """FNV-1a 64-bit hash. Matches fleet canary 0x024a555471370b18d on 'cafe Delta Japanese'."""
    if isinstance(s, str):
        b = s.encode("utf-8")
    elif isinstance(s, (bytes, bytearray)):
        b = bytes(s)
    else:
        b = str(s).encode("utf-8")
    h = FNV_OFFSET
    for byte in b:
        h = ((h ^ byte) * FNV_PRIME) & MASK_64
    return h


def fnv1a64_hex(s: Union[str, bytes, bytearray]) -> str:
    """FNV-1a 64-bit as a 16-char hex string (leading zeros preserved)."""
    return format(fnv1a64(s), "016x")


def int16_dials(text: str, count: int = 16) -> list:
    """Signed int16 dials from observation hash (for live-canon /api/cell submission).

    Produces up to 16 signed int16 values in [-32768, 32767]. The first 7 non-zero
    are kept; the rest are 0. Matches the 0x024a555471370b18d fleet canary.
    """
    h = fnv1a64(text)
    dials = [0] * count
    nonzero = 0
    for i in range(count):
        v = h & 0xffff
        dial = v - 65536 if v > 32767 else v
        dials[i] = dial
        if dial != 0:
            nonzero += 1
            h = ((h * FNV_PRIME) + dial) & MASK_64
        if nonzero >= 7:
            break
    return dials


# The 11 typed opcodes (5 base + 6 missing from R10)
OPCODES = {
    "BIND": "BIND",          # (obs, obs) -> bundle
    "LINK": "LINK",          # (obs, obs) -> link
    "EFFECT": "EFFECT",      # obs -> world
    "VIEW": "VIEW",          # bundle -> display
    "TICK": "TICK",          # world -> obs

    "ATTEST": "ATTEST",      # obs -> trust_score (proposed R10)
    "DELEGATE": "DELEGATE",  # (issuer, issuer) -> authority_transfer (proposed R10)
    "CONTEST": "CONTEST",    # obs -> counter_obs (proposed R10)
    "MERGE": "MERGE",        # (obs, obs) -> composed_obs (proposed R10)
    "REVOKE": "REVOKE",      # obs -> superseded_obs (proposed R10)
    "WITHDRAW": "WITHDRAW",  # obs -> retracted_obs (proposed R10)
}

# Three forms of evidence (R10 canonical)
EVIDENCE = {
    "DIRECT": "direct",   # FNV-1a hash proves this happened
    "WITNESS": "witness", # other observations corroborate
    "PATTERN": "pattern", # JEPA detects this fits
}

# Three kinds of forgetting (R10 canonical)
FORGETTING = {
    "BUNDLE": "bundle",       # archive (bundle unreachable)
    "TRAVERSAL": "traversal", # scar (path lost, observation preserved)
    "EVIDENCE": "evidence",   # decay (no longer verifiable)
}


class Observation:
    """The canonical substrate atom.

    observation = { subject, predicate, object, issuer, time, evidence, signature }
    """

    __slots__ = ("subject", "predicate", "object", "issuer", "time", "evidence", "signature", "id")

    def __init__(
        self,
        *,
        subject: str,
        predicate: str,
        object: Any,
        issuer: Union[str, dict],
        time: Optional[int] = None,
        evidence: Optional[str] = None,
        signature: Optional[str] = None,
    ):
        if not subject:
            raise ValueError("observation requires subject")
        if not predicate:
            raise ValueError("observation requires predicate")
        if object is None:
            raise ValueError("observation requires object (use object=None if explicitly null)")
        if not issuer:
            raise ValueError("observation requires issuer")
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.issuer = issuer if isinstance(issuer, str) else issuer.get("id", str(issuer))
        self.time = int(time) if time is not None else _time.time_ns() // 1_000_000
        self.evidence = evidence
        self.signature = signature
        self.id = self._compute_id()

    def _compute_id(self) -> str:
        payload = json.dumps(
            {
                "s": self.subject,
                "p": self.predicate,
                "o": self.object,
                "i": self.issuer,
                "t": self.time,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return fnv1a64_hex(payload)

    def validate(self) -> bool:
        return bool(self.id) and bool(self.issuer)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "issuer": self.issuer,
            "time": self.time,
            "evidence": self.evidence,
            "signature": self.signature,
        }

    def __repr__(self):
        return f"Observation({self.id[:8]}..., subject={self.subject!r}, predicate={self.predicate!r})"
