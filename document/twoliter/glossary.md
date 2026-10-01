---
type: Reference
description: Domain vocabulary used across Twoliter code, docs, and Makefile.toml (kit, variant, SDK, vendor, override, lock, EIF, UKI, repack…).
---

# Glossary

| Term | Meaning | Where it shows up |
|---|---|---|
| **Variant** | A Bottlerocket image definition (`variants/<name>/Cargo.toml` with `[package.metadata.build-variant]`); name format `platform-runtime[-version[-flavor]]`, e.g. `aws-k8s-1.32-nvidia` | `tools/bottlerocket-variant`, `BUILDSYS_VARIANT` |
| **Out-of-tree (OOTB)** | Building variants from a repo other than the Bottlerocket monorepo — Twoliter's reason to exist | `docs/design/README.md` |
| **Kit** | A yum repository shipped whole as an OCI image (`FROM scratch`, `/repodata` + `/Packages`), built from `kits/<name>` with `[package.metadata.build-kit]`. **Local kit** = built from this project; **external kit** = pulled from a registry | `rpm2kit`, `build/kits`, `build/external-kits` |
| **Kit metadata** | JSON (name, version, arch, sdk, dependencies) stored base64-encoded in image label `dev.bottlerocket.kit.v3`; drives dependency resolution | `twoliter/src/project/lock/image.rs`, `compatibility.rs` |
| **SDK** | `bottlerocket-sdk` container image with cross toolchains; every kit in a build must have been built with the same SDK. Passed to `cargo make` as `TLPRIVATE_SDK_IMAGE` | `[sdk]` in `Twoliter.toml`, `fetch-sdk` task |
| **Vendor** | A named container registry prefix (`[vendor.<name>] registry = …`); images resolve to `<registry>/<name>:v<version>` | `twoliter/src/project/vendor.rs` |
| **Override** | `Twoliter.override` entry `[<vendor>.<artifact>]` with `name`/`registry` redirecting one image (e.g. to a local registry) without editing `Twoliter.toml` | `ArtifactVendor::Overridden` |
| **Lock** | `Twoliter.lock` (schema 2): resolved SDK + kits, each with `name`, `version`, `vendor`, `source` URI and `digest`. Every command that loads a project (all except `update` and `debug`) re-resolves and fails if the lock no longer matches — `twoliter update` rewrites it | `twoliter/src/project/lock/mod.rs`, `lock/image.rs::LockedImage` |
| **Verification tags** | `.sdk-verified` / `.kits-verified` marker files in `build/external-kits/` proving the lock was checked this run; `Makefile.toml` tasks refuse to proceed without them | `lock/verification.rs`, `fetch-sdk`, `validate-kits` |
| **Project vendor / release-version** | `Twoliter.toml` keys: who is building (required from schema 2), and the version stamped on artifacts (`BUILDSYS_VERSION_IMAGE`) | `twoliter/src/project/migrate/parser.rs` |
| **Package** | An RPM built from `packages/<name>` (`[package.metadata.build-package]`, spec file, sources from a **lookaside cache**) | `buildsys build-package` |
| **Lookaside cache** | `https://cache.bottlerocket.aws` — SHA512-addressed mirror of upstream source tarballs; `BUILDSYS_UPSTREAM_SOURCE_FALLBACK=true` allows upstream URLs | `tools/buildsys/src/cache.rs`, `tools/build-cache-fetch` |
| **Repack** | `repack-variant` task: take an existing image (built or `fetch-variant`ed from TUF), swap CA bundle / `root.json` / Secure Boot keys, rebuild dm-verity, re-sign — no package builds | `img2img`, `eif2eif` |
| **Image format** | `[package.metadata.build-variant] image-format`: `raw`, `qcow2`, `vmdk`, `eif`, `uki` | `tools/buildsys/src/manifest.rs::ImageFormat` |
| **EIF** | AWS Nitro Enclave Image File; variants with `image-format = "eif"` produce `.eif` + `-disk.img`; PCR0 signed with a cert/key from `Infra.toml [eif]` | `tools/eif-builder`, `rpm2eif`, `eif2eif`, `eif-sign-helper` |
| **UKI** | Unified Kernel Image (`image-format = "uki"`, added 0.23.0); `ukisys derive-stub` recovers the unsigned stub | `tools/ukisys`, `img2img` |
| **Guest images** | Disk images of one variant embedded into another's rootfs (`[package.metadata.build-variant.guest-images]`) | `guest-images-helper`, `tests/projects/guest-images-kit` |
| **kmod kit** | Tarball of kernel dev headers + toolchain for out-of-tree modules | `rpm2kmodkit`, `BUILDSYS_KMOD_KIT` |
| **Infra.toml** | Publishing config: TUF repos + signing keys (`file|kms|ssm|env`), AWS regions/roles, VMware, OCI vendors, `[eif]` | `tools/pubsys-config` |
| **Waves** | Staged update rollout policy for TUF `manifest.json` (`waves/default-waves.toml` etc.) | `tools/update-metadata`, `PUBLISH_WAVE_POLICY_PATH` |
| **BRSA / advisory** | Bottlerocket Security Advisory TOML; `advisory-checker` ensures kit packages meet patched versions | `tools/advisory-checker` |
| **pipesys / bypass** | FD-passing trick so `docker build` stages can write into host dirs; "bypass dir" is served by a `pipesys serve` container | `tools/pipesys`, `tools/buildsys/src/builder.rs` |
| **krane** | Static build of go-containerregistry's `crane`; Twoliter's only OCI client (pull/push/manifest/config) | `tools/krane`, `tools/oci-cli-wrapper` |
| **TLPRIVATE_*** | `Makefile.toml` variables only Twoliter may set (currently `TLPRIVATE_SDK_IMAGE`) | `[env.private]` |
| **`twoliter make`** | Passthrough to any `Makefile.toml` task; how the Bottlerocket monorepo's own `cargo make` is implemented | `twoliter/src/cmd/make.rs` |
