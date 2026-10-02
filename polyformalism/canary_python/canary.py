"""Quilt fleet canary verification — Python reference implementation.

Returns: 0x024a555471370b18d
"""
import struct

CANARY = "café Δ 日本語"

def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h = h ^ b
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

if __name__ == "__main__":
    print(f"fnv1a-64('{CANARY}') = {hex(fnv1a_64(CANARY))}")
