---
type: Reference
description: Bottlerocket domain and build-system vocabulary (variant, kit, Twoliter, buildsys, pubsys, TestSys, storewolf, setting generator, migration, sbkeys profile, host containers, waves).
---

# Glossary

| Term | Meaning |
|---|---|
| **Variant** | A named image flavour = list of kit packages + settings plugin + defaults, e.g. `aws-k8s-1.36-nvidia-fips`. Naming: `<platform>-<orchestrator>[-<k8s version>][-nvidia][-fips]`, or `<platform>-dev`. Defined in `variants/<name>/Cargo.toml`. |
| **Family / flavor** | TestSys and settings-plugin grouping: family is e.g. `aws-k8s`, flavor adds `-nvidia`; FIPS variants reuse the non-FIPS defaults and plugin. |
| **Kit** | A prebuilt, versioned bundle of RPMs published as a container image (`bottlerocket-core-kit`, `bottlerocket-kernel-kit`). Declared in `Twoliter.toml`, pinned by digest in `Twoliter.lock`. |
| **SDK** | `bottlerocket-sdk` container with the cross toolchains (musl targets like `x86_64-bottlerocket-linux-musl`) used to build packages and kmods. |
| **Twoliter** | The build tool (`bottlerocket-os/twoliter`) that `cargo make` installs and delegates to; owns `buildsys`, `pubsys`, `testsys`. |
| **buildsys** | Twoliter component invoked by every `build.rs` here: `build-package` (RPM from spec) and `build-variant` (image from packages). Reads `[package.metadata.build-package|build-variant]`. |
| **pubsys** | Twoliter component behind `repo`, `ami`, `ssm`, `upload-ova` tasks; configured by `Infra.toml`. |
| **TestSys** | Kubernetes-operator-based integration test system (`bottlerocket-test-system`); the control cluster is the "testsys cluster"; configured by `Test.toml`. |
| **Remix** | A third-party rebuild of Bottlerocket with a different `BUILDSYS_NAME`/`BUILDSYS_PRETTY_NAME`; see `TRADEMARKS.md`. |
| **Release.toml** | Holds `version` and the `[migrations]` map of `"(from, to)" = [migration binaries]`. |
| **Settings** | The typed configuration tree exposed by the API (`settings.kubernetes.cluster-name` etc.). Dotted-key form is used in docs and the datastore. |
| **Settings plugin** | `cdylib` (`libsettings.so`) defining a variant's `Settings` struct via `#[derive(SettingsPlugin)]`; loaded by apiserver at runtime. Source: `sources/settings-plugins/`. |
| **Modeled types / settings-models** | Validated field types (`SingleLineString`, `KubernetesSettingsV1`, …) from `bottlerocket-settings-sdk`. |
| **`#[model]`** | Derive macro (`model_derive`) that adds serde attrs, optional-wrapping, and datastore renames to settings structs. |
| **Defaults (`defaults.d`)** | Ordered TOML fragments per variant merged into one defaults file; also declare `services`, `configuration-files`, and `metadata`. |
| **storewolf** | Core-kit service that seeds the datastore from `/etc/storewolf/defaults.toml` on first boot. |
| **Datastore** | Key/value store with metadata and transactions backing the API (`sources/api/datastore`). Scalars are stored as JSON. |
| **Setting generator** | `metadata.settings.<key>.setting-generator` = command (e.g. `schnauzer-v2 render …`, `shibaken …`, `bork seed`) run to compute a value at boot; has `strength` (`strong`/`weak`) and `depth`. Weak values are dropped on upgrade/downgrade. |
| **affected-services / restart-commands** | Metadata tying a setting to services whose config files get re-rendered and restarted when it changes. |
| **Migration** | Small static binary (`migrate_v<ver>_<name>`) run by `migrator` when moving between versions to transform datastore keys; helpers like `AddPrefixesMigration`. Shipped in the `migrations` RPM and as `.lz4` TUF targets. |
| **A/B partitions, partition flip** | Two identical OS partition sets; updates write the inactive set and flip the boot pointer; `signpost rollback-to-inactive` reverts. |
| **TUF** | The Update Framework; update repos have `metadata` and `targets` URLs, root role `root.json` (this repo ships `8.root.json`), and a signing key (file/KMS/SSM). |
| **Waves** | Staggered rollout schedule for updates in a TUF repo (`PUBLISH_WAVE_POLICY_PATH`); `ignore-waves` setting bypasses. |
| **Expiration policy** | How long TUF metadata roles stay valid (`2w-2w-1w.toml`). |
| **kmod kit** | Tarball of kernel headers + toolchain published per variant/arch for building out-of-tree modules. |
| **Host containers** | Containers run by a separate `host-containerd` outside the orchestrator: `control` (SSM agent, enabled by default on AWS), `admin` (SSH, `sheltie` root shell, superpowered, off by default), `bootstrap` containers/commands (run at boot). |
| **apiclient / apiserver** | CLI and Unix-socket HTTP server (`/run/api.sock`) for settings, updates, `exec`, reboot. In core-kit. |
| **early-boot-config** | Reads TOML user data (file, IMDS, CD-ROM/OVF, guestinfo) and posts it to the API at boot. |
| **sbkeys profile** | Directory of Secure Boot keys/certs/EFI vars used to sign shim/GRUB/kernel; `local` (openssl/gpg) or AWS (Private CA + KMS). |
| **image-features / image-layout** | Variant manifest knobs read by buildsys: secure boot, erofs root, xfs data, systemd-networkd, in-place updates, encrypted storage, unified vs split partition plan, image sizes. |
| **FIPS variant** | Variant built with FIPS-validated crypto; shares defaults/plugin with its non-FIPS sibling. |
| **NVIDIA variant** | Includes NVIDIA driver/toolkit packages; requires a `Licenses.toml` to build. |
