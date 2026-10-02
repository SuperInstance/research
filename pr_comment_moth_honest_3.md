## Review — moth-honest #3 prereg (strong-inference pre-registration)

**Verdict**: MERGEABLE (after #2 lands).

Strong-inference per Platt is the right rubric. The structural check — *a hypothesis without an exclusion observation cannot be falsified, enforced in __post_init__* — is exactly what makes pre-registration trustworthy, otherwise it's theater.

The refusal-label taxonomy is the other half the doctrine needs:

| label | meaning |
|-------|---------|
| `correct-restraint` | predicted restraint on clean exercise — earned |
| `missed-bug` | restraint on planted-bug exercise — gate failed |
| `abstention` | restraint or silence without context — neutral |

Booked against ground truth = auditable. If pre-registration says "I'll claim evidence X would falsify rival Y" and then the run produces evidence X, you have a falsification record without subjective judgment.

**Cross-project with cellforge**: This is the same principle as **causal-consistency verdict on rewind (v0.4.1)**: declare in advance what would falsify the operation, then check the actual outcome.

**Optional**:
- Add a `prereg_manifest.jsonl` per run so external benches can re-verify without reading the diff.
- Consider surfacing in CI: if prereg file is missing, fail the test.

**Net**: ready.
