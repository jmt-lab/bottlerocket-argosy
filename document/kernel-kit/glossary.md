---
type: Reference
description: Kit-specific jargon — kit, Twoliter, buildsys, SDK, variant/flavor capabilities, gptprio, BRSA, external-files, Neuron, EFA, MIG, IMEX, fabricmanager.
---

# Glossary

`GLOSSARY.md` in the repo is inherited from the main Bottlerocket repo and mostly describes OS components not present here. Terms that matter for this repo:

| Term | Meaning here |
|---|---|
| **Kit** | A Twoliter artifact: an OCI image of prebuilt RPMs plus metadata that variant builds pull as a dependency. This repo builds exactly one, `bottlerocket-kernel-kit` (`kits/bottlerocket-kernel-kit/`). |
| **Twoliter** | Bottlerocket's build orchestrator (`tools/twoliter/twoliter`, pinned in `Makefile`). Reads `Twoliter.toml`/`.lock`, runs builds inside the SDK container, publishes kits. |
| **SDK** | `bottlerocket-sdk` container image with cross toolchains, `rpmbuild`, `buildsys`, and the `Makefile.toml` tasks behind `make twoliter <task>`. Pinned in `Twoliter.toml`. |
| **buildsys** | Tool inside the SDK invoked by every crate's `build.rs` (`build-package`, `build-kit`). Downloads `external-files`, verifies hashes, runs rpmbuild. |
| **Variant** | A downstream Bottlerocket image definition (e.g. aws-k8s-1.33-nvidia) that consumes this kit. Specs express compatibility via `variant-platform(...)`, `variant-flavor(...)`, `image-feature(...)` RPM capabilities. |
| **`%{_cross_os}`** | SDK RPM macro prefix applied to every package name; built RPMs appear as `bottlerocket-<name>-*.rpm` under `build/rpms/`. |
| **external-files** | `[[package.metadata.build-package.external-files]]` entries: upstream URL + sha512 fetched at build time. `force-upstream` forbids using the Bottlerocket mirror. |
| **source-groups** | `[package.metadata.build-package] source-groups = [...]` names the `sources/` crate(s) a first-party package is built from; the spec then runs `%cargo_build` against `sources/Cargo.toml` (see `packages/nvidia-migmanager`). |
| **AL2023 SRPM** | Amazon Linux 2023 source RPM; the kernels, grub and libkcapi are rebuilt from these rather than from upstream tarballs. |
| **config-bottlerocket / config-full-bottlerocket** | Kconfig fragments layered on the AL2023 config vs. the fully merged, generated result used for validation (`make full-config`). |
| **gptprio** | GRUB extension (patches in `packages/grub/`) reading priority/tries/successful bits from GPT partition entries to pick the boot partition set. |
| **shim** | UEFI first-stage loader (`packages/shim/`) built in two flavors: chain-loads GRUB, or chain-loads systemd-boot for UKI images. |
| **UKI** | Unified Kernel Image; `image-feature(uki-image)` selects the systemd-boot shim and excludes grub. |
| **FIPS** | `kernel-*-fips` subpackages ship `fipsmodules-<arch>` lists and a check unit for FIPS variants. |
| **Neuron** | AWS Inferentia/Trainium driver (`aws-neuronx-dkms`) built into `kernel-*-modules-neuron` on x86_64. inf1 uses the 2.24 line. |
| **EFA** | Elastic Fabric Adapter kernel module from the AWS EFA installer (`kmod-*-efa`). |
| **Tesla / GRID / open-gpu** | NVIDIA driver variants packaged per kernel in `kmod-*-nvidia-r580|r595` (r = driver branch). |
| **fabricmanager / IMEX / nvlsm** | NVIDIA NVLink/NVSwitch fabric services: fabricmanager and IMEX config live in the nvidia kmod package; `nvlsm` is the subnet manager package. |
| **MIG** | Multi-Instance GPU partitioning; applied at boot by the first-party `nvidia-migmanager` binary from `settings.kubelet-device-plugins.nvidia.mig.profile`. |
| **gdrcopy** | NVIDIA GPUDirect RDMA copy library/module bundled in the nvidia kmod package. |
| **BRSA** | Bottlerocket Security Advisory; TOML files under `advisories/<kit-version>/` with CVE, severity and per-package patched versions. |
| **Infra.toml / Twoliter.override** | Gitignored local files: registry vendors for `make publish`; SDK/kit overrides read by `twoliter update` and `tools/docker-run.sh`. |
