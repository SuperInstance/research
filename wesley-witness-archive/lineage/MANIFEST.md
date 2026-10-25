# Witness poll lineage — AI-Writings `bots/wesley-mechanic`

Complete lineage of the four most recent canon-watcher polls, reconstructed from the
`AI-Writings` remote. Every commit object below survives on the remote (verified via the
commits API); only the last one (`85f56ad`) became unreachable from `main` when `main` was
restored via root commit `85a955f1`.

## Poll commits (all on `AI-Writings`)

| # | commit | poll time | log lines | witness note |
|---|---|---|---|---|
| 1 | `73611600f223412b07f9d6068e33cf4a2ce01aa6` | 2026-10-25T20:03:59Z | 24 | `witness-note-20261025T200359Z.md` |
| 2 | `22bb1f924e31b731df080804aae7ca70dd0fe152` | 2026-10-25T20:17:19Z | 26 | `witness-note-20261025T201719Z.md` |
| 3 | `b9a47fffc7a28d5c1e9ac26c75e027ff5a456e82` | 2026-10-25T20:33:03Z | 28 | `witness-note-20261025T203303Z.md` |
| 4 | `85f56ad2859439be8a1d629db0af9f6af46bc226` | 2026-10-25T20:47:10Z | 30 | `witness-note-20261025T204710Z.md` |

Each commit has the identical 3-file shape: `witness.log` (+2 lines), `poll_state.json`
(rewritten), and one new `notes/witness-note-<stamp>.md`.

## Log snapshots (`log-snapshots/`)

| file | bytes | lines | md5 |
|---|---|---|---|
| `witness.log.59` | 14409 | 24 | `79adc4e141b96c3090f4bcf5f58c799e` |
| `witness.log.19` | 15999 | 26 | `9a668eb09619c35020e8f8c0c4ddcd3f` |
| `witness.log.03` | 17589 | 28 | `3066572e7d3fba68273eb41a072a8281` |
| `witness.log.10` | 19182 | 30 | `82c8bb556b2fbf0db18f1618f4c0e786` |

**Strict-append verification:** every consecutive pair diffs to `+2 / -0` lines. No line was
ever removed or rewritten across the four polls. The 28-line snapshot md5
`3066572e7d3fba68273eb41a072a8281` independently matches the pre-poll md5 recorded
separately during poll #4 — two independent observations of the same file agreeing.

## Notes (`notes/`)

All 12 witness notes currently on `AI-Writings` `main` (11 historical + the sandbox-recovery
note), plus poll #4's note. The 11 historical notes are byte-identical to the files on
`AI-Writings` main; poll #4's note was the one dropped by the restore and exists only in
commit `85f56ad`.

## Canon timeline

| poll | canon iso | meta rows | civs | leader |
|---|---|---|---|---|
| pre-#1 | `2026-10-25T19:53:08` | 1013 | 8 | `civ-poetic` |
| #1 | `2026-10-25T20:13:31` | 1023 | 8 | `civ-poetic` |
| #2 | `2026-10-25T20:23:05` | 1028 | 8 | `civ-poetic` |
| #3 | `2026-10-25T20:34:30` | 1033 | 8 | `civ-poetic` |
| #4 | `2026-10-25T20:34:30` | 1033 | 8 | `civ-poetic` |

Poll #4 observed no *further* canon movement beyond what #3 had already recorded — but the
canon's prior state (iso `20:23:05`, 1028 rows) was itself only ever captured inside poll
#3's diff, so the #3→#4 transition remains the authoritative record of the canon's arrival at
its current state.

> Note: the `notes/` directory in this lineage folder duplicates the parent
> `wesley-witness-archive/notes/` copy of poll #4's note. That is intentional — the parent
> holds *this* poll's artifacts, the lineage folder holds the *whole* series.
