---
type: Styleguide Rule
description: "Commit headers in Bottlerocket repositories use `scope: description` (lowercase scope matching ^[a-z][a-z0-9._-]*), at most 72 characters, no trailing period, not Conventional Commit types; body lines wrap at 72 after a blank line."
language: general
category: commits
---
# Commit header format

Enforced in CI by `.commitlint.config.mjs` in bottlerocket, bottlerocket-core-kit and bottlerocket-kernel-kit.

- Header regex `^[a-z][a-z0-9._-]*: .+$`, at most 72 characters, trimmed, no trailing period.
- The scope is a component, package, crate or area: `kubernetes-1.36`, `twoliter`, `settings-plugins`, `changelog`, `release`.
- The description is lowercase, imperative, and says what the change does.
- Leave a blank line after the header; wrap body lines at 72.
- Do not use Conventional Commit types (`feat:`, `fix:`) as the scope. `chore: bump to twoliter X.Y.Z` is the one established exception and passes the regex.
- Merge commits and `Revert "…"` are exempt.

## Good

```
kubernetes-1.36: update to v1.36.2
twoliter: bump kit version to v9.1.0
changelog: update for v1.64.0
```

## Bad

```
feat(kubernetes): Update Kubernetes to v1.36.2.
Updated stuff
```
