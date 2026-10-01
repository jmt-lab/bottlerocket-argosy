---
type: Argosy Manifest
name: bottlerocket
argosy_version: 0.1.0
---
# bottlerocket-core-kit
Core kit documents are in documents/core-kit

# bottlerocket-kernel-kit
Kernel kit documents are in documents/kernel-kit

# bottlerocket
Bottlerocket documents are in documents/bottlerocket

# twoliter
Twoliter documents are in documents/twoliter

# Cross-repo guides
- documents/bottlerocket/local-kit-workflow: test kit changes in a variant via a local OCI registry and Twoliter.override.
- documents/bottlerocket/review-principles: how to review changes in any Bottlerocket repo.
- documents/core-kit/packaging-style-guide (spec-editing procedure and checklist), documents/core-kit/release-process, documents/twoliter/version-bump-and-local-testing.

# Styleguide
Coding and commit rules are styleguide concepts: styleguide/general (commits, complexity, refactoring, comments), styleguide/rust/<category> (error-handling, design, organization, documentation, testing, …) and styleguide/rpm-spec/<category> (kit packaging: numbering, metadata, licensing, paths, files, subpackages, fips, systemd, …). Repo and crate conventions take precedence over these defaults (styleguide/general/match-existing-conventions).

Members not yet documented: sdk, admin-container, control-container, settings-sdk.
