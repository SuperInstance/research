# Sandbox notes — AI-Writings purge & witness archive session (2026-10-25)

Durable operational lessons. Env-specific, recur every wipe.

## The NAS wall at /workspace

`/workspace` is NFS-backed by a shared storage account that can hit 100% quota
(600G/600G, 0 avail) **even when the workspace itself holds zero files**. Symptoms:

- `dd`/`printf`/`cp` to `/workspace` → "Disk quota exceeded"; `cp` reports
  `failed to close '<path>': Disk quota exceeded` **while the stub still appears in
  `ls -la` at 0 bytes**.
- A 1-byte write yields a 0-byte file with exit 0. **Exit code 0 does not mean the
  write landed** — always check `wc -c` / md5, never `ls` alone.
- The `write` tool fails with `-122` ("close") on a full NAS.
- `git clone` into `/workspace` dies partway: cannot copy `.git/description`.
- `/tmp` and `/mnt/envd` (overlay, 28G free) are **not** subject to the NAS quota.
  The `read`/`write`/`edit` tools are jailed to `/workspace` and will not read `/tmp`
  ("Workspace path escapes Cloud Host root") — use bash for /tmp work.

**Rule:** do all work under `/tmp`, deliver from there, and keep git as the durable copy.

## Main can move under you mid-session

After pushing, `origin/main` was replaced by a **root commit** (`85a955f1`, "RECOVERY:
restore AI-Writings main to the full corpus"), which **dropped my pushed commit from
main's history** even though the commit object survived (HTTP 200 on the commits API).

- `git status` said "ahead of origin/main by 1 commit" while the remote had moved —
  a stale `origin/main` ref masks this. Always confirm the **actual remote sha via the
  API**, not the local ref.
- A root commit has `parents: []` and `stats: None` — that shape in the API response is
  the tell that history was rewritten, not merely added to.
- `git fetch` on this repo can hang past 30s; use `timeout` and prefer the API for
  history inspection.

## Archival practice

When a repo may be purged, a witness record is worth **more than the poll that made it**
if it documents how the current state was reached. Verify the observation still matches
the present state before calling a record "stale" — here the poll's canon iso
(`2026-10-25T20:34:30`, 1033 meta rows) was *identical* to the restored main's canon, so
the note was the only surviving record of the transition into it.

Reconstructing a lineage beats archiving one artifact: pulling `witness.log` at each of
4 commits gave snapshots of 24 → 26 → 28 → 30 lines, each diffing to `+2 / -0` — proof
the log was only ever appended to, never rewritten. The 28-line snapshot's md5 matched
the pre-poll md5 recorded independently during the poll: two observations agreeing.

## Shell bugs I hit (both self-inflicted, both looked like data corruption)

1. `while read -r n; do curl ... ; done < list` — the `curl` inside the loop **consumes
   stdin**, silently truncating the list. Symptom: every item "mismatched". Fix: use a
   `for` loop over `$(cat file)`, or `curl </dev/null`.
2. `cd X && ...` inside a loop body changes the cwd for subsequent iterations, so later
   relative paths land in the wrong directory. Symptom: files written one level up, and
   `md5sum` reporting "No such file" while `ls` shows them present.

Both produced a "remote vs local mismatch" that looked like a corrupted download. It
wasn't. **Always re-verify the local path exists before declaring a hash mismatch.**
