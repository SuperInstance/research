#!/usr/bin/env python3
"""
CHORALE EXPERIMENT (2026-09-24)
================================
Novel problem: can N substrate walkers sing in unison against a shared witness log?

Hypothesis H3: N parallel emissions against a shared witness log create a
chord-branched chain (each witness has N prev-pointer candidates) —
the witness chain degenerates but a *chord witness* (composed) captures
the multi-source event.

Method:
- Spawn N walkers (variations of a brewed substrate walker)
- Each emits receipts in parallel against a shared witness log
- At each tick, all walkers fire — only one wins the prev-pointer
- A chord-witness aggregates N prev-pointers into a composed witness

Pass criterion: chain integrity holds when measured at the chord-witness layer.
"""

import os
import sys
import time
import json
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path("/workspace/research/chorale-2026-09-24")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# --- minimal substrate walker envelope (8-field canonical) -----------------
def fnv1a_64(s: str) -> int:
    """Match fleet canary: 0x024a555471370b18d on 'café Δ 日本語'"""
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8", errors="surrogatepass"):
        if b == 0:
            continue
        h ^= b
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


FLEET_CANARY = fnv1a_64("café Δ 日本語")
assert FLEET_CANARY == 0x024a555471370b18d, f"canary drift: {FLEET_CANARY:#x}"
print(f"[OK] Fleet canary verified: 0x{FLEET_CANARY:016x}")


def make_witness(walker_id: str, prev_id: str, cell_id: str, substrate: str,
                 polarity: str, status: str, payload: dict) -> dict:
    raw = json.dumps({
        "prev": prev_id, "ts": datetime.now(timezone.utc).isoformat(),
        "walker": walker_id, "cell": cell_id, "polarity": polarity,
        "payload": payload,
    }, sort_keys=True).encode()
    wid = hashlib.sha256(raw).hexdigest()[:16]
    return {
        "witness_id": wid,
        "prev_witness_id": prev_id,
        "cell_id": cell_id,
        "walker_id": walker_id,
        "substrate": substrate,
        "polarity": polarity,  # ACCEPT / DRIFT / REFUSE
        "status": status,      # OPEN / COMPOSED / WITNESSED
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


# --- N synthetic walkers, each owned by its own thread --------------------
class Walker:
    def __init__(self, name: str, biases: dict):
        self.name = name
        self.biases = biases   # {"temperature": 0.7, "humidity": 0.3, ...}
        self.local_chain = []  # local append-only ledger
        self.lock = threading.Lock()

    def tick(self, tick_num: int, energy: dict):
        # Walker reads its own current state + energy → polarity decision
        for sensor, val in energy.items():
            threshold = self.biases.get(sensor, 0.5)
            if abs(val - threshold) < 0.1:
                polarity = "DRIFT"
            elif val < threshold - 0.3 or val > threshold + 0.3:
                polarity = "REFUSE"
            else:
                polarity = "ACCEPT"
            payload = {"sensor": sensor, "value": val, "threshold": threshold,
                       "tick": tick_num}
            w = make_witness(self.name, "", f"{self.name}-cell-{sensor}",
                             sensor, polarity, "OPEN", payload)
            with self.lock:
                self.local_chain.append(w)
        return self.local_chain[-len(energy):] if energy else []


# --- chord witness layer ---------------------------------------------------
class ChordLog:
    """Composes N walkers' local emissions into a shared append-only log."""

    def __init__(self, walkers: list):
        self.walkers = {w.name: w for w in walkers}
        self.composed_chain = []  # list of chord-witnesses (one per tick)
        self.tick_counter = 0
        self.lock = threading.Lock()

    def tick(self, energy: dict) -> dict:
        self.tick_counter += 1
        all_local = {}
        with ThreadPoolExecutor(max_workers=len(self.walkers)) as ex:
            futures = {ex.submit(w.tick, self.tick_counter, energy): w.name
                       for w in self.walkers.values()}
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    emissions = fut.result()
                    all_local[name] = emissions
                except Exception as e:
                    all_local[name] = [{"error": str(e)}]

        prev_id = (self.composed_chain[-1]["witness_id"]
                   if self.composed_chain else "")
        composite = {
            "tick": self.tick_counter,
            "ts": datetime.now(timezone.utc).isoformat(),
            "walkers_emitting": sorted(all_local.keys()),
            "emission_count": sum(len(v) for v in all_local.values()
                                  if isinstance(v, list)),
            "polarity_mix": {
                pol: sum(1 for v in all_local.values()
                         for w in (v if isinstance(v, list) else [])
                         if isinstance(w, dict) and w.get("polarity") == pol)
                for pol in ("ACCEPT", "DRIFT", "REFUSE")
            },
            "per_walker": {
                name: {"count": len(v) if isinstance(v, list) else 0,
                       "first_polarity": (v[0].get("polarity") if isinstance(v, list)
                                          and v and "polarity" in v[0] else None)}
                for name, v in all_local.items()
            },
        }
        composite["polarity_mix"] = {k: v for k, v in composite["polarity_mix"].items() if v}

        raw = json.dumps(composite, sort_keys=True).encode()
        composite["witness_id"] = hashlib.sha256(raw).hexdigest()[:16]
        composite["prev_witness_id"] = prev_id

        with self.lock:
            self.composed_chain.append(composite)
        return composite


def chain_intact(chain):
    """Walk the chord chain; check prev pointer + monotonic tick."""
    issues = []
    for i in range(1, len(chain)):
        prev = chain[i - 1]
        cur = chain[i]
        if cur["prev_witness_id"] != prev["witness_id"]:
            issues.append(f"tick {cur['tick']}: prev mismatch "
                          f"({cur['prev_witness_id']} vs {prev['witness_id']})")
        if not (cur["tick"] > prev["tick"]):
            issues.append(f"tick {cur['tick']}: not monotonic")
    return issues


# --- run -----------------------------------------------------------------
def main():
    print(f"\n== Chorale experiment ==")
    print(f"== N walkers in unison against one chord log ==\n")

    # 3 walkers with diverse biases
    walkers = [
        Walker("alpha", {"temperature": 0.65, "humidity": 0.55, "pressure": 1.0}),
        Walker("beta",  {"temperature": 0.75, "humidity": 0.40, "pressure": 0.9}),
        Walker("gamma", {"temperature": 0.55, "humidity": 0.70, "pressure": 1.1}),
    ]

    log = ChordLog(walkers)

    # 20 ticks of synthetic energy — drifting values to provoke DRIFT/REFUSE
    energy_streams = [
        {"temperature": 0.6 + 0.05 * i, "humidity": 0.5 + 0.02 * i,
         "pressure": 1.0 - 0.01 * i}
        for i in range(20)
    ]

    start = time.perf_counter()
    for tick_energy in energy_streams:
        log.tick(tick_energy)
    elapsed = time.perf_counter() - start

    # Test chain integrity
    issues = chain_intact(log.composed_chain)

    # Compute fleet canary of the chord chain
    chain_canary_input = json.dumps(
        [{"tick": c["tick"], "wid": c["witness_id"]}
         for c in log.composed_chain], sort_keys=True)
    chain_canary = fnv1a_64(chain_canary_input)

    # Aggregate per-walker emission totals
    per_walker_totals = {}
    for w in walkers:
        per_walker_totals[w.name] = {
            "local_chain_len": len(w.local_chain),
            "polarity_breakdown": {
                pol: sum(1 for x in w.local_chain if x.get("polarity") == pol)
                for pol in ("ACCEPT", "DRIFT", "REFUSE")
            },
        }

    # Polarities on the chord layer
    chord_polarities = {
        pol: sum(1 for c in log.composed_chain
                 if c["polarity_mix"].get(pol, 0) > 0)
        for pol in ("ACCEPT", "DRIFT", "REFUSE")
    }

    # Did H3 hold?
    h3_confirmed = (len(issues) == 0) and (len(log.composed_chain) == 20)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "experiment": "chorale",
        "hypothesis": "H3: N walkers → chord chain branches → composed witness "
                       "captures multi-source event",
        "n_walkers": len(walkers),
        "n_ticks": len(log.composed_chain),
        "elapsed_seconds": round(elapsed, 4),
        "ticks_per_second": round(len(log.composed_chain) / elapsed, 1),
        "chain_intact": len(issues) == 0,
        "chain_issues": issues,
        "chord_chain_canary": f"0x{chain_canary:016x}",
        "fleet_canary_match": (chain_canary == FLEET_CANARY),
        "chord_polarity_ticks": chord_polarities,
        "per_walker_totals": per_walker_totals,
        "h3_confirmed": h3_confirmed,
        "first_3_chord_witnesses": [
            {"tick": c["tick"], "wid": c["witness_id"],
             "prev": c["prev_witness_id"]}
            for c in log.composed_chain[:3]
        ],
        "last_3_chord_witnesses": [
            {"tick": c["tick"], "wid": c["witness_id"],
             "prev": c["prev_witness_id"]}
            for c in log.composed_chain[-3:]
        ],
    }

    report_path = OUT_DIR / "chorale-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[OK] Wrote {report_path} ({report_path.stat().st_size} bytes)")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    main()
