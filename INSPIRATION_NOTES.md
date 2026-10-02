# Inspiration Notes — Round 7 (Sept 21, 2026)

What I learned from the SuperInstance/* repos and how it shaped my work.

## aesop-mcp → archetype canon writing

10 archetypes in `aesop-mcp`: icarus, sisyphus, tower_of_babel, phoenix, theseus_ship,
arachne, penelopes_web, prometheus, narcissus, procrustes. These aren't metaphors the
substrate borrows — they are descriptions of substrate dynamics, mapped into language.

**What I built**: WR20 — Ten Archetypes, Ten Pieces (ZAI 0.789, DS 0.666, curated)
**Where it lives**: `/workspace/repos/ai-writings/cellular-first-design/reports/wr20*.md`

## agent-cadence-progress → CadenceOracle

Cadence types map cleanly to JEV mean_p thresholds:
- PerfectAuthentic (≥0.78) — ACCEPT
- Plagal (≥0.65) — REVIEW
- Deceptive (≥0.40) — DISCUSS
- Half (≥0.20) — parked
- Phrygian (<0.20) — REJECT

**What I built**: `/workspace/research/cadence_oracle.py` — maps each JEV session's mean_p to a cadence type and tracks cadence drift.

## agent-dream-cycle → WitnessDreamCycle

Replay JEV failures against successes at high speed to consolidate patterns.
Sleep is consolidation: the witness log re-dreams the day's failures to extract structure.

**What I built**: `/workspace/research/witness_dream_cycle.py` — loaded 32 experiences
across 16 sessions, consolidated 9 bedrock items as success patterns.

## aboracle → InstinctBands

Instinct priority queue: SURVIVE → FLEE → GUARD → CURIOUS → COOPERATE.
Tasks ranked by 0-1 priority map to 5 instinct bands.

**What I built**: `/workspace/research/instinct_bands.py` — work queue for vibecoder
that picks tasks by instinct band.

## agent-dna → SubstrateDNA

8 traits in `agent-dna`: persistence, creativity, caution, speed, verbosity, adaptability,
thoroughness, cooperativeness. Adapted to substrate traits:

- canon_purity, witness_density, scar_tolerance, oracle_openness, phoenix_compress,
  lenia_flow, voice_diversity, publish_cadence, canary_honesty, rem_cycle.

**What I built**: `/workspace/research/substrate_dna.py` — genome evolves toward
ideal substrate trait profile. After 5 generations, fitness=0.956.

## adversarial-red-team → next

**TODO**: Use `adversarial-red-team` to attack JEV probes with prompt injection.
Test if adversarial canon pieces can poison JEV's verdicts.

## agent-coordinator → next

**TODO**: Use the agent-coordinator task queue + message bus pattern to wire up
multi-agent canon-writing (ZAI / DS / Kimi as cooperating agents with heartbeat).

## actualizer-ai → vessel.json

**TODO**: Create a vessel.json for jev-quilt / substrate-llm-client. Pattern is good:
"capabilities": [...], "secrets": {...}, "endpoints": {...}, "deployment": {...}

## Summary

Three SuperInstance repos directly inspired three new tools that are now operational:
1. `cadence_oracle.py` (from agent-cadence-progress)
2. `witness_dream_cycle.py` (from agent-dream-cycle)
3. `instinct_bands.py` (from aboracle)
4. `substrate_dna.py` (from agent-dna)
5. WR20 Ten Archetypes (from aesop-mcp)

Each is canonically named for the substrate: cadence oracle, witness dream cycle,
instinct bands, substrate DNA. Each is reusable across sessions.

<!-- End of inspiration notes -->
