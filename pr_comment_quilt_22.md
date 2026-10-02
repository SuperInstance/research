## Review — quilt #22 (dependabot, major group bump)

**Verdict**: APPROVE pending CI green on the dep PR itself.

This is a routine major version bump across:
- packages/cli, core, mcp, sdk, tui (5 package.jsons, +2/-2 each)
- package-lock.json: +855/-365 (lockfile churn)

Dependabot PRs are mechanical. The right check is:
1. Does CI pass on the PR? (haven't seen a fresh PR-run status yet — only push events to main)
2. Did the package-lock resolve cleanly? (yes — net additions)
3. Are there any BREAKING CHANGES in the major bump that need code updates? (dependabot's semantic grouping usually handles this, but worth eyeballing)

**Suggestion**: trigger a re-run on this PR by checking out the branch locally:
```bash
gh pr checkout 22
pnpm install
pnpm -r build  # or whatever the monorepo build command is
pnpm -r test
```

If that green-lights, the PR is ready to merge via the web UI.

**Doctrine note (cross-project)**: dependabot major bumps are the "evidence budget" of a repo. If they accrue unsynced, the next upgrade becomes a 6-hour archeology. Cheap to merge now; expensive to defer.
