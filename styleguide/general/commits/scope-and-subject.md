---
type: Styleguide Rule
description: "Use the shortest obvious scope (the package, crate or area name a maintainer would recognise) and write the subject in active voice describing the change's effect."
language: general
category: commits
---
# Commit scope and subject

- Shorten the scope to the obvious name: the package directory (`containerd-2.3`), the crate, or the area (`build`, `docs`, `changelog`), not a path or a sub-crate a reader must decode.
- The subject answers "what does this change do?" in active voice. Describe the effect, not the activity.

## Good

```
schnauzer: reject templates with unknown helpers
```

## Bad

```
sources/api/schnauzer/src/v2: changes for helper validation
```
