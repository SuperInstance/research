# Private → public: the log

One repo at a time. Each entry records what the repo **is**, what was **wrong with it**,
what it was **changed into**, and — the part that matters — **what should be built next and
why it earns a place in the fleet.**

---

## 001 · `audit-trail` → public

**What it was.** A `Vec<AuditEvent>` with sequential ids, 90 lines, one trivial test.
The 87-line README described "immutable, append-only event logging" and an architecture
the code did not have. There was no hash, so there was nothing to alter and therefore
nothing to detect.

**Why it was chosen first.** The fleet's canon chain is `DECLARED-NOT-USED` — `prev_hash`
exists in the schema and is zero in every sampled live cell. This crate is the obvious
place to implement what the witness-validation research concluded, and doing the first one
properly establishes the pattern for the other 200.

**The four defects, which turned out to be uniform across the whole cluster:**

| defect | this repo | across the 141 Rust repos |
|---|---|---|
| no `tests/` | 0 tests but 1 trivial inline | **1 / 141** have a `tests/` dir |
| no LICENSE file | claimed `MIT OR Apache-2.0`, contained neither | **1 / 141** |
| broken repository URL | `github.com/casey-digennaro/audit_trail` | **0 / 141** correct |
| `Hello, world!` main.rs | yes | **23 / 141** |

Plus a `publish.yml` that fired on any `v*` tag — it would have published a crate with no
tests, no licence text, and a repository URL pointing at a different account.

**What it is now.** Each event commits to its predecessor:
`hash(N) = FNV-1a-64(canonical(N) ‖ hash(N-1))`, and `verify()` reports the id of the first
break. Canonical encoding is injective (length-prefixed fields), so `("ab","c")` and
`("a","bc")` cannot hash the same. Genesis is non-zero, because a zero genesis is
indistinguishable from a chain truncated back to nothing.

The hash is FNV-1a 64 because it is the digest the rest of the fleet already agrees on —
`0x24a555471370b18d`, now reproduced in Rust alongside Python, TypeScript, C#, and Julia,
and re-checked at runtime by `canary_holds()` so a drifting port fails its own tests.

**14 tests, 14 passing.** Five are negative controls: inject a field, delete an event,
reorder, retimestamp, verify twice. A suite that only asserted "record works" would have
passed on the original `Vec` — which is the entire reason this was rewritten.

**The README now leads with what a chain does NOT prove**, because that is the part that is
usually wrong: it does not prove the writer did not rewrite the whole chain, that the
timestamp is real, or that the recorded event is true about the world.

**What should be built next, and why it earns its place.**

1. **Batch the chain** — Merkle over events within a batch, hash-chain the *roots*. Chaining
   every event is O(n) hashes for a log only ever checked at checkpoints. This is what the
   witness-validation design calls for, and the consistency proof is the part a bare Merkle
   root cannot give you.
2. **Serialise** — a canonical versioned encoding, so a log survives the process that
   wrote it.
3. **Signed checkpoints** — sign the head, publish it somewhere the writer does not control.
   Without this the chain detects accidents and nothing else.
4. **A model-version field** — a model change must be a new segment with an explicit version
   bump, never a retroactive rewrite. That is the rule that keeps an error budget intact, and
   it is the one a self-updating log violates first.

---

## The finding that shapes the remaining 200

**These are not 201 finished repos. 141 of them are one generated crate catalogue** —
individually named canonical algorithms and patterns in Rust (`aabb-collision`,
`ackermann-function`, `activation-fn`, `albanese-variety`, `ast-diff`, `agent-memory`, …),
created within a ~112-day window, median `src/lib.rs` of 104 lines, median README of 109.

They have coherent families worth developing as systems rather than as loose crates:

- `actor-*` — 5 repos: dispatcher, pool, router, supervisor, system. A full actor runtime
  split across five crates, which is the fleet's own cell architecture in a different idiom.
- `audit-log` / `audit-trail` — the integrity pair; `audit-trail` is now the real one.
- `ast-*` — diff and visitor. Directly useful for the witness chain and for structural code
  review.

**The judgement, stated plainly:** publishing these as-is would put 141 untested crates
with no licence text and a broken repository URL in front of the world. That is worse than
private. The work is not "flip the switch 201 times" — it is *finish them first, publish in
families, and let each family carry the canary.*

**Recommended shape for the rest:**

- **Fix before publish, uniformly:** LICENSE files, correct `repository` URL, a real test
  suite, and delete or fix the auto-publish workflow. That is mechanical and scriptable.
- **Then publish by family, not by repo,** so the README cross-links make the family legible
  as a system.
- **Then carry the canary** through all of them. 141 Rust ports of `0x24a555471370b18d` is
  the strongest possible statement of the polyformalism claim, and it is nearly free once
  `fnv1a64` is in each crate.

**The non-Rust 60 are a different job.** They are real projects (`tminus-os`, a 118-file
swarm coordination OS; `baton-system`; `quilt-deck`; `luciddreamer-*`) and deserve individual
attention, not a script.

**Held back, not published:**

| repo | why |
|---|---|
| `covers` (284 MB) | bulk content; needs a look at what it is before it is world-readable |
| `researchlocal-backup` (45 MB) | the name says backup; backups are where private material lives |
| `luciddreamer-content` (126 MB) | bulk content + an `.env.example` |
| `magda-core-study`, `quilt-dpcpp`, `si-ghost-ledger`, `si-knowledge-graph` | empty (0 KB) — nothing to publish |
| `plato-room-code-review`, `repo-docs` | the "secret" hit is a *policy file about* secrets — flag was a false positive, but confirm before publishing |

---

## The mechanical pass (2026-09-30)

`fixup.py` applied six repairs across the Rust catalogue. Every one is strictly an
improvement and reversible from git history. **Publishing was a separate, explicit step and
did not happen here.**

1. `LICENSE-MIT` + `LICENSE-APACHE` — the Cargo.toml already *declared* `MIT OR Apache-2.0`
   and 140 of 141 repos contained neither file.
2. Correct `repository` URL — all 141 pointed at `casey-digennaro/…`. Two of them had **no
   `repository` line at all**, which a regex-replace pass silently misses.
3. Real `description` — `"A Rust library for Audit_trail"` tells a reader nothing the
   repository name did not already say.
4. `fnv1a64` + `canary_holds` + `tests/canary.rs` — **every crate in the catalogue is now a
   polyformalism port.** If the hash drifts, the crate fails its own suite instead of quietly
   disagreeing with the rest of the fleet. This is the single most valuable thing the pass
   did: 141 independent reimplementations of `0x24a555471370b18d`.
5. Replaced `Hello, world!` main.rs (23 repos) with something that prints the canary.
6. Removed the auto-publish workflow — it fired on any `v*` tag and would have published an
   unlicensed, untested crate to crates.io.

**Also found and handled:** several repos are described as "A Rust library for X" but ship
**no `src/lib.rs` at all** — they are binary crates. The description was false. The pass
adds a real `lib.rs` so the description becomes true and there is something for a canary
test to stand on.

### The test gate earned its keep

The script refuses to push when `cargo test` fails. Five crates were refused:

`anomaly-detect` · `blake3-hash` · `bloom-filter-scalable` · `bulkhead-pattern` · `coff-parser`

**These fail on a pristine checkout.** Verified by cloning each clean and running
`cargo test` before any change. They shipped with broken tests, which is a different and
worse problem than shipping without tests.

### Bottleneck worth knowing

Some of these crates are not trivial: `consul-client` pulls reqwest + tokio + serde and
produces **262 MB of build artifacts**, rebuilt from scratch in every fresh clone. The pass
is correct but slow on those, and it is resumable — repos already done report
`already-clean` on a second pass.

## The other 60: a rename migration, never finished

GitHub cannot rename a repository, so `si-*` twins were created and the originals left
behind. **The migration was never completed, and the twins have diverged.**

| `si-` twin | original | verdict |
|---|---|---|
| `si-terminal` 18 KB / 6 f | `mud-terminal` 18 KB / 6 f | **byte-identical trees** |
| `si-player` 16 KB / 9 f | `player-widget` 16 KB / 9 f | **byte-identical trees** |
| `si-feedback` 4 KB / 6 f | `feedback-engine` 4 KB / 6 f | **byte-identical trees** |
| `si-conductor` 24 KB / 13 f | `conductor` 25 KB / 11 f | diverged; `si-` has more files |
| `si-sonic-shape` 22 KB / 9 f | `sonic-shape` 2 KB / 3 f | **`si-` is the real one** |
| `si-streamer` 22 KB / 13 f | `streamer` 3 KB / 4 f | **`si-` is the real one** |
| `si-ghost-ledger` 0 KB / 1 f | `ghost-ledger` 144 KB / 7 f | **original is the real one** |
| `si-knowledge-graph` 0 KB / 1 f | `knowledge-graph` 2 KB / 3 f | **original is the real one** |
| `si-research` 6 KB / 4 f | `research-lab` 14 KB / 13 f | original is bigger |

**No pair agrees on a winner.** Three are byte-identical, four have the `si-` version
carrying the work, and two have the `si-` twin as an empty shell with the real content in
the original.

**Publishing both halves of an identical pair puts two identical repositories in front of
the world, which is worse than either.** Each pair needs a decision from a human: which name
is canonical, and what happens to the other — archive it, or fold its content forward.

This is the "no deletion" doctrine colliding with a rename. The right resolution is
archival with provenance, not deletion and not duplication.

---

## The sweep, run properly (2026-09-30)

41 non-Rust private repos, full history, `gitleaks 8.24.3` + hand-rolled grep + dotfile
audit + entropy + operational-details. **The order is enforced: no repo is flipped before
its sweep verdict.**

```
CLEAN     28
FINDINGS  13
dotfiles  0   (no committed .env / .npmrc / .pem / credentials anywhere)
```

### The 13, resolved by context-check

The instrument over-fired, and checking each one changed the answer. **Six of the seven
credential findings were placeholders, type annotations, or `os.environ.get` calls:**

| repo | what the pattern matched | verdict |
|---|---|---|
| `feedback-engine` | `SCHEDULER_API_KEY = "your-secret-key"` / `"REPLACE_WITH_YOUR_KEY"` | placeholder |
| `si-feedback` | same, plus `request.headers.get('X-API-Key')` | placeholder + code |
| `mud-engine` | `apiKey: 'test-key'` in a test fixture; `private apiKey: string` | fixture + type annotation |
| `ai-writings-vectorizer` | `os.environ.get("CLOUDFLARE_API_TOKEN")` | correct behaviour — reads from env |
| `sweep` | `BEGIN ... PRIVATE KEY` | the string in the redaction protocol's own docs |
| `tminus-os` | `SAFETY_DISABLED_TOKEN = "__VAAS_SAFETY_DISABLED__"`; `def f(token: str)` | sentinel + type annotation |
| `tminus-os` | `CLOUDFLARE_API_TOKEN = "…"` | **18 chars, lowercase, no digits → placeholder.** Not live. |

**The 2026-08-30 ledger flagged the same class** ("Benign: `sk-your-key-here` placeholder")
and that is why its method ends in a context check rather than a pattern count.

**The other finding is real but low-risk:** `049ff5…aae6` — the Cloudflare account ID — in
six repos (`activeledger-ai-site`, `activelog-ai-site`, `deckboss-site`, `fishinglog-ai-site`,
`luciddreamer`, `tminus-os`). The precedent classifies it exactly: *"LOW (identifier, not
credential)… not rotatable, low risk alone."* It is an operational detail, not a secret.

### So where that leaves the 41

**All 41 are clear of live credentials.** Two of them (`activeledger-ai-site`,
`activelog-ai-site`) also carry **Casey's personal email** in history, which is a privacy
call rather than a security one, and is the only thing standing between them and a flip.

### Operational detail worth fixing at the source

`mavis@superinstance.local` and `superinstance@users.noreply.github.com` appear in
commits made by the fixup pass. They are introduced by *this* work, they are benign, and a
future sweep will flag them. Configure `user.email` once and stop reintroducing them.
