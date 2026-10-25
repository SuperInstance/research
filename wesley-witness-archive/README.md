# Wesley witness archive — AI-Writings canon poll 2026-10-25T20:47:10Z

Archival copy of a single canon-watcher poll against the `AI-Writings` civilization canon.

**Why this lives here and not in `AI-Writings`:** the poll was executed against `AI-Writings`
and pushed to its `main` (commit `85f56ad`), but `main` was subsequently restored to a
recovered corpus via a root commit (`85a955f1`, "RECOVERY: restore AI-Writings main to the
full corpus and re-unite the split lineages"). That recovery did not carry the witness
files forward, so `bots/wesley-mechanic/witness.log` on `main` is back to 28 lines and the
poll's two appended lines plus its witness note are no longer reachable from `main`.

The commit object `85f56ad` still exists on the `AI-Writings` remote (verified via the
commits API, HTTP 200) but is unreachable from `main`. This directory is the durable,
reachable copy.

## Why the record is not stale

The canon observed by this poll is **the current canon** of `AI-Writings`. Verified against
the restored `main` via the contents API:

| field | poll observed | restored main |
|---|---|---|
| `leaderboard.json` iso | `2026-10-25T20:34:30` | `2026-10-25T20:34:30` |
| `meta_log.jsonl` rows | 1033 | 1033 |
| civs | 8 | 8 |

So this witness note is the only surviving record of *how* the canon arrived at its present
state — the transition from iso `2026-10-25T20:23:05` (1028 rows) to iso
`2026-10-25T20:34:30` (1033 rows), with the per-civilization relevance/wins/losses deltas.

## Contents

| file | bytes | md5 |
|---|---|---|
| `witness.log` | 19182 | `82c8bb556b2fbf0db18f1618f4c0e786` |
| `poll_state.json` | 5964 | `0fdf3ef5d31dbc1076379fcde549fb03` |
| `notes/witness-note-20261025T204710Z.md` | 1436 | `d88b6b314cf93cfb45b247dd35cd4fe1` |
| `POLL_RECEIPT.md` | 1545 | `fe585c10165b5f1b3afa71a49d5cf80f` |
| `wesley_watcher.py` | 13208 | `c4abf5a47d1f3b9e80c904588ba7b298` |

`witness.log` is the full 30-line log (28 historical lines + 2 from this poll). The append
was verified **pure**: `git diff --numstat` = `2 0`, and the pre-existing 28 lines are
byte-identical to their pre-poll state (md5 `3066572e7d3fba68273eb41a072a8281`).

## Poll summary

- canon snapshot `2026-10-25T20:23:05` -> `2026-10-25T20:34:30`
- meta log rows `1028` -> `1033` (+5)
- 26 differences across 8 civilizations
- fingerprint `24ee14a0a230fb974fcf204397a24613882c4c9b489f75b8d003599f70263a99`
  -> `0cf2c2645a4a63343e4d95ee353801f2cbbcd55fe19cccb318ef21dd976200c4`
- leader `civ-poetic` (relevance 3521.57); lowest `civ-therapist` (2482.43)
- last recorded competition: "Write 100 words on JEV as a decision oracle.", won by `civ-precise`

## Sandbox conditions at time of poll

The NAS backing `/workspace` was at a hard 100% quota (600G/600G, 0 available), so even a
1-byte write produced a 0-byte file. The clone, poll, and commit were performed under
`/tmp`; the durable copy was pushed to git and verified via the API rather than by trusting
push output.

## The watcher script

`wesley_watcher.py` is the tool that produced these records. It is archived here as a
safety copy; it is currently byte-identical to `bots/wesley-mechanic/wesley_watcher.py`
on `AI-Writings` `main` (both md5 `c4abf5a47d1f3b9e80c904588ba7b298`, verified via the
contents API). If `AI-Writings` is purged, this copy keeps the poll reproducible.
