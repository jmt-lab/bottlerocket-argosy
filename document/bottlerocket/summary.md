---
type: Reference
description: One-page orientation to the bottlerocket-os/bottlerocket repository — what it is, what it contains today, and where to look next.
---

# Bottlerocket (top-level repository)

Bottlerocket is a free, open-source, Linux-based operating system built by AWS for hosting containers. It has no shell or SSH server in the image, uses an immutable dm-verity root filesystem, updates by flipping between two partition sets (A/B) using images secured by TUF, and is configured entirely through a local HTTP API whose settings are migrated automatically across updates. Nearly all first-party code is Rust.

This repository (`https://github.com/bottlerocket-os/bottlerocket`, branch `develop`) is the **top-level "project" repo**. Since the 2024 kit split (see `document/decisions/kits-and-twoliter`), almost all OS components live in separate repos and are consumed here as prebuilt **kits**. What remains here is:

| Concern | Where | Owner doc |
|---|---|---|
| Which images exist and what goes in them (49 variants) | `variants/` | `document/architecture` |
| Per-variant settings model (plugins), defaults, and settings migrations | `sources/` | `document/architecture` |
| RPM packaging glue for those three source groups | `packages/` | `document/architecture` |
| Build/publish/test task surface (`cargo make …`) | `Makefile.toml`, `Twoliter.toml` | `document/development` |
| Release version and migration list | `Release.toml` | `document/development` |
| Publishing/test helpers and policies | `tools/`, `sbkeys/` | `document/architecture` |
| User-facing guides | top-level `*.md` files | this doc, below |

Current release version (from `Release.toml` and `Twoliter.toml`): **1.64.0**. Kits pinned: core-kit 15.1.0, kernel-kit 9.0.2, SDK 0.78.0 (see `document/tech`).

## Who it is for

- **Operators** running containers on EKS, ECS, VMware vSphere, or bare metal. They consume published AMIs/OVAs/images and never build. Start with `QUICKSTART-EKS.md`, `QUICKSTART-ECS.md`, `QUICKSTART-VMWARE.md`, `PROVISIONING-METAL.md`, `QUICKSTART-LOCAL.md`.
- **Builders/remixers** producing their own images or variants. Start with `BUILDING.md`, then `PUBLISHING.md` (+ `PUBLISHING-AWS.md`, `PUBLISHING-VMWARE.md`), `TESTING.md`, `sbkeys/README.md`.
- **Contributors** changing variants, settings defaults, or migrations here, or bumping kit versions. See `CONTRIBUTING.md` and `document/conventions`.

## Top-level documents in the repo

| File | Covers |
|---|---|
| `README.md` | Feature overview, exploration via control/admin containers, updates, settings (now mostly links to bottlerocket.dev), logs, NVIDIA/Neuron notes, packaging list |
| `BUILDING.md` | Prereqs, `cargo make` build, licenses (`Licenses.toml`), NVIDIA variants, AMI registration, kmod kits |
| `PUBLISHING.md` / `-AWS.md` / `-VMWARE.md` | `Infra.toml`, TUF repos, waves, expiration, AMIs, SSM params, OVAs |
| `TESTING.md` | `cargo make unit-tests`, TestSys integration tests (kind cluster, `Test.toml`), migration and workload tests |
| `SECURITY_FEATURES.md` / `SECURITY_GUIDANCE.md` | dm-verity, SELinux, lockdown, Secure Boot; operator hardening advice |
| `PROVISIONING-METAL.md`, `SUPPORTED-HARDWARE.md` | Bare-metal install, net.toml network config, bootconfig |
| `CHANGELOG.md`, `ROADMAP.md`, `CHARTER.md`, `TRADEMARKS.md` | Release notes, roadmap pointer, tenets (Secure/Open/Small/Simple), naming rules for remixes |
| `variants/README.md` | What a variant is, list of current and deprecated variants, how to add one |

Note: several README links still point at in-repo paths that moved to core-kit (e.g. `sources/updater/`, `sources/api/apiclient/`, `tools/buildsys`, `tools/testsys`). Those directories no longer exist here; the code is in `bottlerocket-core-kit` and `twoliter`.

## Sibling repositories you will need

| Repo | Role |
|---|---|
| `bottlerocket-os/twoliter` | The build tool. `cargo make` here just installs and delegates to it. Contains `buildsys`, `pubsys`, `testsys`. |
| `bottlerocket-os/bottlerocket-core-kit` | Nearly all packages and first-party sources (apiserver, updater, netdog, kernel-agnostic packages, containerd, kubelet, …) |
| `bottlerocket-os/bottlerocket-kernel-kit` | Kernel packages (`kernel-6.1`, `kernel-6.18`, …) |
| `bottlerocket-os/bottlerocket-sdk` | Cross-compilation SDK container |
| `bottlerocket-os/bottlerocket-settings-sdk` | `bottlerocket-settings-models`, `model_derive`, settings-plugin framework (git dependency of `sources/`) |
| `bottlerocket-os/bottlerocket-test-system` | TestSys operator and agents |
| admin-container, control-container, bootstrap-container, update-operator, ecs-updater | Host containers and updaters referenced from defaults |
