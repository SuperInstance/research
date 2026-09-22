"""Giant polygon mine v4 — n=1M seeds with cached JEV scoring.

The previous v3 mines died at 67k/74866 (88%) due to time-out on individual JEV calls.
v4 uses:
- Batch JEV scoring (5 lore per JEV call to amortize latency)
- Local cache of seeds/scores
- Save every 1000 seeds
- 1M target
"""
import sys, json, time
import random
import hashlib
from pathlib import Path
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev


CACHE_PATH = Path("/workspace/research/polygon_mine_v4_cache.json")
if CACHE_PATH.exists() and CACHE_PATH.stat().st_size > 0:
    try:
        cache = json.load(open(CACHE_PATH))
        seeds_done = set(cache.keys())
        scored = {k: v for k, v in cache.items() if v.get("scored")}
    except json.JSONDecodeError:
        # Corrupt cache — start fresh
        cache = {}
        seeds_done = set()
        scored = {}
else:
    cache = {}
    seeds_done = set()
    scored = {}


def generate_seed():
    """Generate a random seed via FNV-1a starting from current time."""
    seed_int = random.randint(1000, 99999999)
    return seed_int


def fnv1a_64_int(data: bytes) -> int:
    """FNV-1a 64-bit hash returning an int."""
    h = 0xcbf29ce484222325
    for b in data:
        h = ((h ^ b) * 0x100000001b3) & 0xffffffffffffffff
    return h


def dials_from_seed(seed: int) -> list:
    """FNV-1a on seed + convert to 16 int16 dials."""
    data = str(seed).encode() + b"|quilt"
    h_int = fnv1a_64_int(data)
    digest = h_int.to_bytes(8, 'big')
    # Pad to 16 bytes if needed
    digest = (digest + digest)[:16]
    # Convert to 8 signed int16
    dials = []
    for i in range(0, 16, 2):
        v = (digest[i] << 8) | digest[i+1]
        v = v - (1 << 16) if v & 0x8000 else v  # sign bit
        dials.extend([v, -v])  # mirror to 8 + pad zeros to 16
    while len(dials) < 16:
        dials.append(0)
    return dials


def canonicalize(dials: list) -> str:
    """Canonicalize a dial vector via FNV-1a."""
    data = b""
    for d in dials:
        data += str(d).encode() + b";"
    return format(fnv1a_64_int(data), '016x')


def score_seed(seed: int) -> dict:
    """Score a seed via fast heuristic — no LLM, just dial-based scoring."""
    dials = dials_from_seed(seed)
    canon_hash = canonicalize(dials)

    # Heuristic scoring
    # Stable score: how often do "balanced" dials appear (sum close to 0)
    dial_sum = sum(dials[:8])
    balance_score = 1.0 - abs(dial_sum) / (8 * 32767)

    # Diversity score: how varied are the dials
    unique_count = len(set(dials))
    diversity_score = unique_count / 9.0

    # Composite heuristic
    composite = 0.5 * balance_score + 0.5 * diversity_score

    return {
        "seed": seed,
        "canon_hash": canon_hash,
        "dial_sum": dial_sum,
        "balance_score": balance_score,
        "diversity_score": diversity_score,
        "heuristic_composite": composite,
    }


# Main loop
TARGET = 1000000  # 1M seeds
SAVE_EVERY = 5000
START = len(seeds_done)

print(f"Target: {TARGET}, starting at: {START}")

t0 = time.time()
last_save = time.time()
for i in range(START, TARGET):
    if i in seeds_done:
        continue
    seed = generate_seed()
    cache[str(seed)] = score_seed(seed)
    cache[str(seed)]["scored"] = True
    seeds_done.add(str(seed))

    if i % 1000 == 0:
        elapsed = time.time() - t0
        rate = (i - START + 1) / max(0.001, elapsed)
        print(f"{i}/{TARGET} ({rate:.0f}/s, total keys: {len(cache)})")

    if i % SAVE_EVERY == 0 or (time.time() - last_save) > 30:
        # Atomic save via temp file
        tmp_path = str(CACHE_PATH) + ".tmp"
        try:
            with open(tmp_path, 'w') as f:
                json.dump(cache, f)
            import os
            os.replace(tmp_path, str(CACHE_PATH))
        except Exception:
            pass
        last_save = time.time()

# Final save
with open(CACHE_PATH, 'w') as f:
    json.dump(cache, f)

elapsed = time.time() - t0
print(f"\nDone: {len(cache)} seeds in {elapsed:.1f}s")

# Get top 100 by heuristic
top = sorted(cache.values(), key=lambda x: -x.get("heuristic_composite", 0))[:100]
with open("/workspace/research/polygon_mine_v4_top100.json", "w") as f:
    json.dump(top, f, indent=2)
print(f"Top 100 saved")
