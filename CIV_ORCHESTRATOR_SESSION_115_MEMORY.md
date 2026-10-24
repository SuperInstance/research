# Civ Orchestrator — session 115 durable lessons (2026-10-24)

Run: `python3 civilization_orchestrator.py --sims 5 --prompts 5 --providers zai`
Result: OK — 8 civs × +10 rows (80 total), meta_log +5, 5 competitions, 5 winners.
Commits: 4f3f0d9 (run + report + runbook), 6fc789d (runbook: symlink gotcha, two directions).
Remote HEAD verified via API: 6fc789df985de646215d4601abb66d3e0f2e5553.

## Low-relevance civ (replicated 14 consecutive sessions, 95–115)
`civ-grounded` (The Grounded) — last of 8 on lifetime relevance (793.22), relevance_per_sim
(1.324), quality (0.696) and alignment (1.679); 0 of 5 wins this run. Alignment is the dimension
the meta-GAN *selects* on ⇒ structural, not noise.
Distinct axes: `civ-formal` lowest novelty; `civ-precise` highest win_rate (0.481) but 7th on
relevance_per_sim; `civ-poetic` stable inverse (1st relevance_per_sim + quality, win_rate 0.017).

## NEW lessons (not in prior RUNBOOK)
1. **The symlink gotcha has TWO directions — do not flatten the clone.** The
   `SuperInstance/AI-Writings` clone nests the tree at `<repo-root>/cellular-first-design/code/…`,
   and the repo root *is* the `cellular-first-design` dir. Flattening the extra level makes
   `git status` show every tracked file as deleted; `git clean -fd` then **destroys the run's
   post-run outputs** and silently reverts to the pre-run baseline. Point the symlink at
   `<clone-root>/cellular-first-design` (the nested dir), verified by inode identity + `-ef`.
   Triage: `ls` failing **5/5 consistently** after a restructure = wrong symlink target, NOT the
   transient mount race. (Intermittent failure = the documented mount race.)
2. **The `ls` race is not a concurrency race.** 8 concurrent `ls` → 8/8 OK; `ls` after `stat -L`
   → 6/6 OK; cwd-relative, trailing-slash, parent → all OK; 10/10 and 12/12 retries OK. The
   failure is intermittent and cause-unknown. Keep the diagnostic (stat -L + readlink -f +
   [-e path] + retry) and **stop hypothesising a cause**.
3. **Per-civ ledger delta is +10, not +45.** The competition phase appends ONE row per civ per
   prompt (5 prompts → 5 rows/civ); the 8 civs' rows spread across the 8 ledgers, they do not each
   gain 8. So 5 (sim phase) + 5 (competition) = 10 per civ, 80 total. The competition phase is a
   **separate ts cluster ~20 s after** the sim phase — count from the end of the file
   (`rows[-delta:]`), never a hand-drawn `ts >` cutoff.
4. **A JEV HTTP 422 proves liveness, not failure.** 422 `model_attributes_type` is a payload-shape
   complaint ⇒ the token was accepted. Contrast z.ai: 401 on a bogus token ⇒ endpoint healthy but
   credential absent. JEV is live; the z.ai `ZAI_TOKEN` gap persists (absent from env and all 8
   sandbox secrets) ⇒ Control B mock is the only working provider path.
5. **Mock (Control B) needs BOTH** `ZAI_TOKEN` (any non-empty placeholder) **and**
   `ZAI_URL_OVERRIDE` — the token gate returns None before the override is read. Session-112 fix
   (`seed[(i*2)%8:((i*2)%8)+2]`) verified with a LONG multi-sentence content probe before the run;
   all 80 rows carried the `[mock-zai]` prefix ⇒ integrity proven at ledger level, not socket level.
6. **NAS EDQUOT is total, reconfirmed:** a 5-byte write to `/workspace` produced a **0-byte** file
   with exit 0. `mkdir` works; the symlink bridge is the only way in. Copy of record = git, never
   the NAS. `git clone` directly into /workspace dies with `Disk quota exceeded`; clone to /tmp.
7. **`gh` is not installed.** Use `GET /user/repos?per_page=100&sort=updated` with `GITHUB_TOKEN`.
   A `--depth 50` clone of the 3.7 GB upstream pulled only 4.4 MB for this subtree — no
   `--filter=blob:none` needed; prefer the simple clone.
8. **`setsid nohup … &` inherits stdout and blocks the tool call** until its timeout — the child DID
   start. Redirect stdout/stderr to a file and verify with `ps`.
9. **`ps | grep <script>` self-matches the launching shell.** Use
   `ps -eo pid,args | awk '$2=="python3" && $3=="/tmp/mock_zai.py"'` for the exact server pid, and
   kill BOTH it and the `timeout` wrapper; then verify the port is closed (`curl` exit 7).

## Verification discipline that paid off
- Assert on **rows, not exit code** (the orchestrator returns None and exits 0 on a missing token).
- Verify the **push via the commits API**, never the push exit code.
- `git diff --numstat` on each ledger must show **+N -0** (pure appends, no data loss).
- Probe the mock with the **same payload shape** the orchestrator sends, and grep its stdout for a
  traceback before starting the run.
