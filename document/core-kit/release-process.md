---
type: Guide
description: How to prepare a bottlerocket-core-kit release — the two strictly ordered signed commits (Twoliter.toml release-version bump, then CHANGELOG.md), how to enumerate and verify PR contents with git show --stat, changelog section hierarchy and entry rules (no version numbers for third-party updates, "Patch" vs "Update"), and validation.
---

# Preparing a core-kit release

Complements `document/core-kit/conventions` (commit format, CHANGELOG validation) and `document/core-kit/development` (CI). Run from the root of a `bottlerocket-core-kit` checkout.

## Two commits, in this order

| # | Change | Commit command |
|---|---|---|
| 1 | `Twoliter.toml`: `release-version = "X.Y.Z"` | `git add Twoliter.toml && git commit -s -S -m "twoliter: bump kit version to vX.Y.Z"` |
| 2 | `CHANGELOG.md`: new `# vX.Y.Z (YYYY-MM-DD)` section | `git add CHANGELOG.md && git commit -s -S -m "changelog: update for vX.Y.Z"` |

Both signed-off and GPG-signed (`-s -S`). Messages follow the repo's `scope: description` commitlint rule.

## Enumerate what changed

```bash
git log --oneline <last_tag>..HEAD                     # or --since="<last release date>" if untagged
git log --merges --oneline <last_tag>..HEAD            # "Merge pull request #NNN" gives PR numbers
git log --merges --grep="pull request" <last_tag>..HEAD   # same, filtered to PR merges
git show <merge_commit> --stat                         # ALWAYS: see the actual files touched
```
If merge commits show no PR numbers, scan `git log --merges --oneline | head -20` for the `Merge pull request #NNN` pattern, and confirm each number exists in the GitHub repo before citing it.

**Never** categorise from commit summaries, branch names or assumptions. A single PR can be *mixed* — e.g. PR #760 touched `sources/host-ctr/` (first-party) **and** `packages/amazon-vpc-cni-plugins/`, `packages/ecs-agent/` (third-party) — and then needs one entry in each section: ``Replace `amazon-ecr-containerd-resolver` with Docker resolver in `host-ctr` ([#760])`` under OS Changes and ``Update `amazon-vpc-cni-plugins`, `ecs-agent` ([#760])`` under Third Party Package Updates.

Categorisation: **first-party** = Bottlerocket's own code (`sources/`, Bottlerocket-specific packages); **third-party** = external software packaged under `packages/` (glibc, docker-engine, …); **Build Changes** = build system, CI, developer tooling; **Orchestrator Changes** = Kubernetes, ECS or other orchestrator-specific features.

## Changelog format

```markdown
# v12.3.0 (2026-01-20)

## OS Changes
- Replace `amazon-ecr-containerd-resolver` with Docker resolver in `host-ctr` ([#760])
- Add MPS control daemon support to `nvidia-k8s-device-plugin` ([#789])

### Third Party Package Updates
- Update `docker-cli-29`, `docker-engine-29` ([#785])
- Patch `containerd-2.1` to update GRPC ([#801])

## Build Changes
…
## Orchestrator Changes
### Kubernetes
…

[#760]: https://github.com/bottlerocket-os/bottlerocket-core-kit/pull/760
[#785]: https://github.com/bottlerocket-os/bottlerocket-core-kit/pull/785
```

Rules:
- Sections: **OS Changes** (first-party, detailed sub-bullets allowed; with a **Third Party Package Updates** subsection), **Build Changes**, **Orchestrator Changes** (with **Kubernetes** subsection when relevant).
- Every bullet ends with `([#NNN])`; reference links collected at the bottom.
- Third-party updates list package names only — **no version numbers** (`Update \`docker-cli-29\`, \`docker-engine-29\` ([#785])`, not "to v29.0.4").
- Use "Patch" for patches/fixes, "Update" for version bumps.
- Group related changes, keep chronological order within a section, match existing header patterns (`tools/validate-changelog.sh` enforces `# vX.Y.Z` headers, unique and descending, optional leading `# Unreleased`).

## Validation checklist

- Two commits in the correct order, signed.
- `Twoliter.toml` `release-version` updated; CHANGELOG has the new section with today's date.
- All entries carry PR references; third-party entries have no versions.
- Each PR's content was checked with `git show <hash> --stat`.
- Preparing the release does not push: push the branch and open the PR yourself.
