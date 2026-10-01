---
type: Decision
description: Why the bottlerocket repo builds through Twoliter and consumes prebuilt core/kernel kits instead of building every package in-tree (2023-07 Twoliter, 2024-06 kit split).
---

# Decision: build via Twoliter and out-of-tree kits

**Dates (from git):** `build: use twoliter make` on 2023-07-26 (`ac5f7bb7`); `core-kit: use v2.0.0` and `packages: remove unnecessary packages` on 2024-06-17 (`5e340b2d`, `ab4a79e4`).

## Context
Historically this repo held every package spec (`packages/kernel-*`, `containerd`, `glibc`, …) and every first-party crate (`sources/api/apiserver`, `sources/updater`, …), plus the build tools (`tools/buildsys`, `tools/pubsys`, `tools/testsys`). Building any variant meant compiling the whole OS, and downstream "remixes" had to fork the entire tree.

## Decision
1. Move the build tooling into a standalone, versioned CLI, **Twoliter**. `Makefile.toml` became a shim that installs a pinned Twoliter and forwards each task (`run_task = "run-twoliter"`).
2. Move packages and first-party sources into **kits** — container images of prebuilt RPMs — `bottlerocket-core-kit` and `bottlerocket-kernel-kit`, declared in `Twoliter.toml` and digest-locked in `Twoliter.lock`.
3. Keep in this repo only what is variant-specific: variant manifests, settings plugins, settings defaults, settings migrations, publishing policies, and user docs.

## Consequences
- Contributing to the OS itself (apiserver, kernel, containerd) happens in the kit repos; this repo mostly sees kit bumps (`twoliter: Bump core-kit to …`), variant additions/removals, defaults, and migrations.
- Build times here are dominated by image assembly, not package compilation.
- Several README/TESTING links to `sources/updater`, `tools/testsys`, `tools/buildsys` are stale in-tree but valid in the kit/Twoliter repos.
- Twoliter and kit versions must be bumped together when a kit needs a newer Twoliter schema (`schema-version = 2`).
- Remixes can now depend on the official kits and add their own kit or variants without forking everything.
