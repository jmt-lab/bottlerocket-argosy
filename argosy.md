---
type: Argosy Manifest
name: bottlerocket
argosy_version: 0.2.0
okf_version: "0.2"
description: Documentation, workflow skills, and coding/packaging styleguide rules for developing Bottlerocket OS — the bottlerocket, bottlerocket-core-kit, bottlerocket-kernel-kit and twoliter repositories.
---
# bottlerocket-core-kit
Core kit documents are in document/core-kit: architecture, conventions, development, tech, release-process, packaging-style-guide, updating-third-party-packages, package-test-matrix, govulncheck.

# bottlerocket-kernel-kit
Kernel kit documents are in document/kernel-kit.

# bottlerocket
Bottlerocket documents are in document/bottlerocket, including migrations (datastore migrations), testing-on-aws (launch, node join, conformance, smoke pods), host-access-and-debugging (control/admin containers, sheltie, apiclient, SSM) and feature-proposal-workflow.

# twoliter
Twoliter documents are in document/twoliter, including pcr-prediction (pcrsys).

# Cross-repo guides
- document/bottlerocket/local-kit-workflow: test kit changes in a variant via a local OCI registry and Twoliter.override.
- document/bottlerocket/review-principles: how to review changes in any Bottlerocket repo.
- document/bottlerocket/feature-proposal-workflow: idea → concept → requirements → design → test plan → implementation plan → implement-commit.
- document/core-kit/packaging-style-guide (spec-editing procedure and checklist), document/core-kit/release-process, document/twoliter/version-bump-and-local-testing.

# Skills
Procedures under skill/<name>/<name>.md; each points at the documents above for background.
- Kits and packages: build-kit-locally, update-package, edit-spec-file, test-third-party-package, govulncheck-source, prepare-core-kit-release, update-twoliter, test-local-twoliter.
- OS: write-migration, predict-pcr-values.
- Testing on AWS: launch-bottlerocket-ec2, eks-smoke-test, conformance-runner, simple-pod-runner, nvidia-smoke-test-runner, soci-snapshotter-tester, ssm-executor, k8s-node-executor.
- Feature workflow: idea-honing, propose-feature-concept, propose-feature-requirements, propose-feature-design, propose-feature-test-plan, propose-implementation-plan, ad-hoc-implementation-plan, implement-commit.
- Review and research: review-code, review-scope, review-style, fact-find, deep-research.

# Styleguide
Coding and commit rules are styleguide concepts: styleguide/general (commits, complexity, refactoring, comments), styleguide/rust/<category> (error-handling, design, organization, documentation, testing, tooling, dependencies, …) and styleguide/rpm-spec/<category> (kit packaging: numbering, metadata, licensing, paths, files, subpackages, fips, systemd, maintenance, …). Repo and crate conventions take precedence over these defaults (styleguide/general/match-existing-conventions).

Members not yet documented: sdk, admin-container, control-container, settings-sdk.
