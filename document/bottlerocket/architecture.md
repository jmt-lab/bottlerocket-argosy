---
type: Reference
description: Components of the bottlerocket top-level repo (variants, settings sources, packages, tools), how they connect to Twoliter and the kits, and the flow of a build.
---

# Architecture of the top-level repo

The repo is a **Twoliter project**: a set of Cargo workspaces whose `build.rs` scripts shell out to `buildsys`, which builds RPMs and images inside the Bottlerocket SDK container. Prebuilt **kits** (core-kit, kernel-kit) supply almost every package; this repo contributes only three first-party RPMs (settings defaults, settings plugins, settings migrations) and the variant definitions that assemble everything into images.

```
cargo make [task]                      Makefile.toml (thin shim)
   └─ tools/install-twoliter.sh        pins TWOLITER_VERSION, installs to tools/twoliter/
   └─ twoliter make <task> --project-path Twoliter.toml
        ├─ fetch SDK + kits from public.ecr.aws/bottlerocket (Twoliter.lock digests)
        ├─ cargo build -p <variant>   (root Cargo.toml workspace)
        │     └─ variants/build.rs → buildsys build-variant
        │           └─ build-deps: packages/{settings-defaults,settings-plugins,settings-migrations}
        │                 └─ packages/build.rs → buildsys build-package → rpmbuild of *.spec
        │                       └─ %cargo_build of crates in sources/ (sources/Cargo.toml workspace)
        └─ image assembled from kit RPMs + these 3 RPMs → build/images/<arch>-<variant>/
```

## Components

### 1. Build shim — `Makefile.toml`, `Twoliter.toml`, `Twoliter.lock`, `tools/install-twoliter.sh`
- `Makefile.toml` (cargo-make) defines `[env]` knobs (`BUILDSYS_*`, `PUBLISH_*`, `TESTSYS_*`, `TWOLITER_*`) and 77 tasks. Every real task is `run_task = "run-twoliter"`, which execs `twoliter make ${CARGO_MAKE_TASK}`. A few (`build-tools`, `publish-tools`, `publish-setup-tools`, `tuftool`, `test-tools`) are marked `deprecated`. `default` aliases `build`.
- `Twoliter.toml` declares `release-version`, the vendor registry, the SDK, and the two kits. `Twoliter.lock` pins image digests; both files change together in kit-bump commits.
- Twoliter itself (`buildsys`, `pubsys`, `testsys`) is *not* in this repo; it is installed to `tools/twoliter/` (git-ignored) by version.

### 2. Variants — `variants/` (root `Cargo.toml` workspace: 49 variants + `packages/settings-defaults` and `packages/settings-plugins`)
- One directory per variant containing a `Cargo.toml`; 25 of the newer AWS variants (ecs-3+, k8s-1.33+, and some FIPS siblings) also carry an `amispec.toml` identical to `variants/shared/amispec-split.toml` (IMDSv2, gp3 volumes). `[package.metadata.build-variant]` is read by buildsys: `included-packages` (kit package names such as `release` or `release-swap`, `kernel-6.18`, `containerd-2.2`, `kubelet-1.36`), `kernel-parameters`, `image-format` (`vmdk` for vmware, `raw` for metal), `supported-arches`, `image-layout.partition-plan` (`split` default or `unified`), and `image-features` (`uefi-secure-boot`, `erofs-root-partition`, `xfs-data-partition`, `systemd-networkd`, `grub-set-private-var`, `in-place-updates`, `encrypted-storage`, `external-kmod-development`).
- All variants share `variants/build.rs` (execs `buildsys build-variant`) and the empty `variants/variants.rs` as `lib`.
- Every one of the 49 variants has exactly three `[build-dependencies]`, pointing at the `packages/*` crates; that is what makes buildsys build them.
- `variants/shared/` holds OVF templates (`template-{split,unified}[-secboot[-tpm]].ovf`) and `amispec-split.toml`.
- Families present: `aws-k8s-1.31…1.36` (+`-nvidia`, `-fips`, `-nvidia-fips`), `aws-ecs-2/3` (+fips/nvidia combos), `aws-ecs-4` (+nvidia), `vmware-k8s-1.31…1.36` (+fips), `aws-dev`, `vmware-dev`, `metal-dev`. Deprecated ones are listed in `variants/README.md`, which is the canonical list and the how-to for adding a variant.

### 3. Settings sources — `sources/` (its own Cargo workspace, `sources/Cargo.toml`)
This is the only Rust code that is compiled into the image from this repo. `.vscode/settings.json` points rust-analyzer here.

| Crate group | Path | Responsibility | Produces |
|---|---|---|---|
| Settings plugins | `sources/settings-plugins/<family>/` (aws-dev, aws-ecs-2, aws-ecs-3, aws-ecs-4, aws-k8s, aws-k8s-nvidia, metal-dev, metal-k8s, vmware-dev, vmware-k8s) | Each is a `cdylib` with one `#[derive(SettingsPlugin)] #[model(rename="settings")]` struct composed of `bottlerocket_settings_models::*V1` types. Defines the variant's API schema. | `libsettings.so`, installed by `packages/settings-plugins/settings-plugins.spec` into `%{_cross_libdir}/settings-plugins`; loaded at runtime by the apiserver (core-kit). |
| Shared defaults | `sources/shared-defaults/*.toml` (48 files, e.g. `defaults.toml`, `updates.toml`, `aws-host-containers.toml`, `kubernetes-aws.toml`, `lockdown-integrity.toml`, `oci-defaults-docker.toml`) | **The real home of default settings.** Each file is a topic-scoped TOML fragment: `[settings]`, `[metadata.settings.*]` (incl. `setting-generator`, `affected-services`), `[services]`, `[configuration-files]`. | Not built directly; linked into variants below. |
| Settings defaults (per variant) | `sources/settings-defaults/<variant>/defaults.d/NN-*.toml` | Ordered **symlinks** into `../../../shared-defaults/` (603 links); only three real files exist (`aws-dev/…/50-aws-dev.toml`, `metal-dev/…/50-metal-dev.toml`, `vmware-dev/…/50-vmware-dev.toml`). `build-defaults.rs` calls `bottlerocket_defaults_helper::generate_defaults_toml()` to merge them in filename order. | One `settings-defaults-<variant>.toml`, installed by `packages/settings-defaults/settings-defaults.spec` to `%{_cross_datadir}/storewolf/<variant>.toml` and symlinked to `/etc/storewolf/defaults.toml` via tmpfiles. 27 defaults crates map onto variants via RPM `Provides/Requires: variant(...)` (FIPS variants share the non-FIPS defaults). |
| Settings migrations | `sources/settings-migrations/v<X.Y.Z>/<name>/src/main.rs` | Tiny binaries using `migration_helpers::{migrate, common_migrations::*}` (e.g. `AddPrefixesMigration`). 25 active; older ones under `archived/` are not built. | Built **statically** and installed as `%{_cross_datadir}/migrations/migrate_v<ver>_<name>` by `packages/settings-migrations/settings-migrations.spec`. `Release.toml` `[migrations]` lists which run between each version pair. |
| `models` | `sources/models/` | Top-level `Model {settings, services, configuration_files, os}`; `Settings` is a transparent wrapper over `BottlerocketSettings` (plugin-backed). Also `exec` (apiclient exec wire types) and `generator` (setting-generator metadata: command/strength/depth). | lib used by migration-helpers |
| `datastore` | `sources/api/datastore/` | Key/value store trait + filesystem/memory impls, dotted-key (de)serialization. Used by migrations. | lib |
| `migration-helpers` | `sources/api/migration/migration-helpers/` | `migrate()` driver, `common_migrations`, datastore helpers, handlebars-aware helpers. | lib |
| `bottlerocket-release`, `constants`, `retry-read`, `generate-readme` | `sources/<name>/` | os-release parser; shared paths (`/run/api.sock`, `/settings`, …); retrying `Read`; build.rs README generator | libs |

`sources/deny.toml` (cargo-deny: license allowlist, no duplicate versions, only the settings-sdk git source allowed) and `sources/clarify.toml` (license clarifications) govern this workspace.

### 4. Package glue — `packages/`
Three crates (`settings-defaults`, `settings-plugins`, `settings-migrations`), each `Cargo.toml` + `.spec`. Shared `packages/build.rs` execs `buildsys build-package`; `packages/packages.rs` is the empty lib. `[package.metadata.build-package].source-groups` names the `sources/` subdirectory to ship as the RPM source. The specs enumerate variants explicitly, so **adding a variant requires editing both the defaults and plugins specs** as well as `sources/Cargo.toml`, root `Cargo.toml`, and `variants/`.

### 5. Publishing, signing, and test support — `tools/`, `sbkeys/`, `8.root.json`
- `tools/pubsys/Infra.toml.example` — template for the git-ignored `Infra.toml` consumed by `cargo make repo|ami|ssm|upload-ova` (TUF root/keys, AWS regions/roles, vSphere datacenters).
- `tools/pubsys/policies/repo-expiration/2w-2w-1w.toml` and `policies/ssm/defaults.toml` — default expiration policy and SSM parameter templates (`PUBLISH_*_PATH` env vars select them).
- `tools/pubsys/support/vmware/import_spec.template` — OVA import spec.
- `tools/start-local-vm` — QEMU/KVM launcher for a built image (see `QUICKSTART-LOCAL.md`); `tools/diff-kernel-config` — compares kernel configs across git revs; `tools/bootconfig/` — QEMU bootconfig data.
- `sbkeys/generate-local-sbkeys`, `generate-aws-sbkeys` — create a Secure Boot key "profile" under `sbkeys/<profile>/` (git-ignored); `BUILDSYS_SBKEYS_PROFILE` defaults to `local` and is auto-generated.
- `8.root.json` — the current TUF root role (version 8) for the official repos.

### 6. Runtime pieces referenced from here but living elsewhere
Apiserver, apiclient, storewolf (loads `/etc/storewolf/defaults.toml` into the datastore on first boot), sundog/schnauzer/shibaken/bork (setting generators named in the defaults), migrator, updog/thar-be-updates, netdog, early-boot-config, host-ctr — all in `bottlerocket-core-kit`. Kernels in `bottlerocket-kernel-kit`.

## Flow of a typical build (`cargo make -e BUILDSYS_VARIANT=aws-k8s-1.36 -e BUILDSYS_ARCH=x86_64`)
1. `install-twoliter` fetches the pinned Twoliter binary (sha256 checked) into `tools/twoliter/`.
2. `fetch-external-kits` pulls SDK and kits by digest from `Twoliter.lock`.
3. Twoliter runs `cargo build -p aws-k8s-1_36` in the root workspace with `--offline --locked`.
4. Cargo builds the three `packages/*` build-dependencies first; each `build.rs` calls `buildsys build-package`, which runs `rpmbuild` on the spec inside the SDK container, compiling the relevant `sources/` crates (defaults → TOML, plugins → `.so`, migrations → static binaries). RPMs land in `build/rpms/`.
5. `variants/build.rs` calls `buildsys build-variant`, which resolves `included-packages` against kit RPMs plus the local RPMs, applies `image-features`/`image-layout`, signs with the sbkeys profile, and writes images to `build/images/x86_64-aws-k8s-1.36/<version>-<sha>/` (raw/vmdk, plus kmod kit, OVA when applicable).
6. Optional: `cargo make repo` (pubsys builds a TUF repo under `build/repos/`), `cargo make ami`, `cargo make test` (TestSys).

## How settings reach a running host
`shared-defaults/*.toml` → symlinked as `defaults.d/NN-*.toml` per variant → merged `settings-defaults-<variant>.toml` → RPM → `/etc/storewolf/defaults.toml` → storewolf populates the datastore at first boot → apiserver loads the variant's `libsettings.so` plugin to type-check the `settings` tree → setting generators listed in `[metadata.settings.*]` fill runtime values → on update, `migrator` runs the `migrate_v*` binaries named in `Release.toml` between the old and new version.
