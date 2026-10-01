---
type: Decision
description: Why each variant's settings model is a runtime-loaded cdylib plugin (sources/settings-plugins) built from bottlerocket-settings-sdk types rather than compiled into the apiserver (2024-06).
---

# Decision: per-variant settings model as a runtime plugin

**Date (from git):** `settings-plugins: add aws-k8s plugin` on 2024-06-01 (`a4d00d10`), coinciding with the kit split (`document/decisions/kits-and-twoliter`).

## Context
The API `Settings` type differs per variant (ECS vs Kubernetes vs dev). Before the kit split, `sources/models/src/<variant>/mod.rs` selected the struct at compile time, so the apiserver and every consumer had to be rebuilt per variant, which is incompatible with shipping one prebuilt apiserver in core-kit.

## Decision
- `sources/models` keeps only the variant-agnostic `Model {settings, services, configuration_files, os}`; `Settings` wraps `bottlerocket_settings_plugin::BottlerocketSettings`.
- Each variant family gets a `cdylib` crate in `sources/settings-plugins/<family>/` whose single struct uses `#[derive(SettingsPlugin)] #[model(rename = "settings", impl_default = true)]` and composes versioned types (`KubernetesSettingsV1`, `UpdatesSettingsV1`, …) from `bottlerocket-settings-sdk` (pulled by git tag in `sources/Cargo.toml`).
- The `settings-plugins` RPM installs the `.so` as `libsettings.so` (soname forced via `-Wl,-soname=libsettings.so`) under `settings-plugins/`, with RPM `Provides: settings-plugin(<variant>)` mapping many variants (FIPS/NVIDIA siblings) to one plugin. ABI stability comes from `abi_stable`.
- Defaults remain per-variant TOML (`sources/settings-defaults`) merged at build time by `bottlerocket-defaults-helper`.

## Consequences
- Adding a setting usually means bumping the settings-sdk tag (new `*V1` field or type), adding defaults, and adding a migration — no apiserver change here.
- A new variant family needs a new plugin crate plus spec subpackage; a new k8s minor within a family needs only defaults.
- Plugins must be built with the same SDK/toolchain as core-kit's apiserver to keep the ABI compatible; hence the shared `bottlerocket-sdk` pin in `Twoliter.toml`.
- `sources/models/src/variant/.keep` is a leftover directory Twoliter still expects to exist.
