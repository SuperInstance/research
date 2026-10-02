## Review — quilt-pincher #6 (eslint 8.57 → 10.10), #7 (vitest 4.1 → 5.0)

**Verdict**: REQUEST CHANGES for #6 / APPROVE for #7.

### #6 eslint 8.57 → 10.10 (major+1)

ESLint 9+ dropped many legacy config formats and removed default parser. If `package.json` is using `eslintConfig` (flat config required since v9), this is a non-trivial migration:
- `.eslintrc.*` is no longer auto-detected
- Multiple plugins may need major versions
- Built-in rules renamed/removed

**Action**: Wait for the eslint migration PR to follow this, OR verify the repo already moved to flat config before merging. The CI on this PR will surface breakage.

### #7 vitest 4.1 → 5.0 (major+1)

Vitest 5.0 is also a config-flag migration in some cases. Same check: does the test config still parse? `vitest.config.ts` may need updates.

**Action**: Approve if CI passes on the PR itself. If CI fails, the migration PR comes with it.

### Doctrine note (cross-project)

The fleet has been deferring dev-dep upgrades. Each minor drift is cheap; each major is one architecture change. Pending dependabot PRs are the canary for upcoming work.
