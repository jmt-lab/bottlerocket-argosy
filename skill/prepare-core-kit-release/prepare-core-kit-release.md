---
type: Skill
description: Prepare a bottlerocket-core-kit release — bump release-version in Twoliter.toml and write the CHANGELOG.md section from verified PR contents, as two signed commits in strict order; use when cutting a new core-kit version.
---

# Prepare a core-kit release

Rules, changelog format and examples: `document/core-kit/release-process`. Commit/CHANGELOG conventions: `document/core-kit/conventions`. Run from the root of a `bottlerocket-core-kit` checkout. Ask for the target version `X.Y.Z` if not given.

1. **Find the range.** Last released version = top `# vX.Y.Z` header in `CHANGELOG.md`. Use `<last_tag>..HEAD` (or `--since=<last release date>` if untagged).
2. **List PRs.** `git log --merges --oneline <range>`; collect each `Merge pull request #NNN`.
3. **Verify every PR's contents.** For each merge commit run `git show <merge_commit> --stat` and classify from the touched paths only — never from summaries or branch names. Split mixed PRs (e.g. `sources/` plus `packages/`) into one entry per section.
4. **Commit 1 — version bump (must come first).** Set `release-version = "X.Y.Z"` in `Twoliter.toml`:
   ```bash
   git add Twoliter.toml && git commit -s -S -m "twoliter: bump kit version to vX.Y.Z"
   ```
5. **Write the changelog section** `# vX.Y.Z (YYYY-MM-DD)` (today's date) at the top of `CHANGELOG.md`, following the section hierarchy and entry rules in `document/core-kit/release-process`: every bullet ends `([#NNN])` with reference links at the bottom; third-party entries list package names with no versions; "Patch" for fixes, "Update" for bumps.
6. **Validate.** `./tools/validate-changelog.sh`.
7. **Commit 2 — changelog.**
   ```bash
   git add CHANGELOG.md && git commit -s -S -m "changelog: update for vX.Y.Z"
   ```
8. **Check.** `git log --oneline -2` shows the bump then the changelog commit; both signed (`git log --show-signature -2`). Do not push; report the commits and let the user open the PR.
