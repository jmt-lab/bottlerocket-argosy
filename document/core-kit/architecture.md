---
type: Reference
description: Components of bottlerocket-core-kit (build pipeline, package layer, first-party sources, kit manifest), where each lives, how they connect, and the flow of a kit build and of a Bottlerocket boot through the API system.
---

# Architecture

Two distinct "systems" live in this repo: the **build system** that turns the tree into a kit image, and the **runtime software** (first-party daemons) that the kit ships. Both are described here.

## 1. Build system: how a kit gets built

```
make  →  tools/install-twoliter.sh (installs twoliter to tools/twoliter/)
      →  twoliter fetch  (pulls SDK image + external kits per Twoliter.lock)
      →  twoliter build kit bottlerocket-core-kit --arch $ARCH
           └─ cargo build of root workspace (Cargo.toml)
                ├─ each packages/<pkg>/Cargo.toml  → build.rs runs `buildsys build-package`
                │     └─ Docker container from bottlerocket-sdk + dep RPMs; rpmbuild <pkg>.spec; RPMs → build/rpms/
                └─ kits/bottlerocket-core-kit/Cargo.toml → build.rs runs `buildsys build-kit`
                      └─ bundles all package RPMs into the kit OCI image
```

| Piece | Path | Role |
|---|---|---|
| Root Cargo workspace | `Cargo.toml` | Members = 126 `packages/*` + `kits/bottlerocket-core-kit` (4 more packages — `libjson-c`, `libudev`, `perf`, `rottweiler` — join implicitly as path deps). Cargo is only a dependency-ordering driver; no Rust is compiled here (`packages/packages.rs`, `kits/kit.rs` are empty libs) |
| Package build shim | `packages/build.rs` | Shared by all packages; execs `buildsys build-package` |
| Kit build shim | `kits/build.rs` | Execs `buildsys build-kit` |
| Twoliter config | `Twoliter.toml`, `Twoliter.lock` | Kit version, vendor registry, pinned SDK image + digest. `kit = []`: this kit depends on no other kits |
| buildsys / twoliter | external ([bottlerocket-os/twoliter](https://github.com/bottlerocket-os/twoliter)) | Reads `[package.metadata.build-package]`, fetches `external-files` from the `cache.bottlerocket.aws` mirror, runs the containerized RPM build. Twoliter's embedded `Makefile.toml` supplies the `check-*`/`unit-tests` tasks reachable via `make twoliter <task>` |
| SDK | external ([bottlerocket-sdk](https://github.com/bottlerocket-os/bottlerocket-sdk)) | Cross toolchains (C, Rust, Go), RPM macros (`%cross_*`), host tools |

**Package dependency graph.** `[build-dependencies]` in a package's `Cargo.toml` = RPM `BuildRequires` (must build first); `[dependencies]` = RPM `Requires` (must be built, not needed for this build). Almost everything depends on `packages/glibc`. See `packages/README.md` §Dependencies for the omission rules.

**First-party packages** use `source-groups` instead of `external-files` to pull directories from `sources/` into the build:

| Package | `source-groups` (dirs under `sources/`) | Ships |
|---|---|---|
| `packages/os` | api, constants, generate-readme, aws-smithy-experimental, bottlerocket-release, metricdog, parse-datetime, pciclient, ghostdog, updater, logdog, models, imdsclient, retry-read, driverdog, cfsignal, bloodhound, xfscli, brush, whippet | 51 RPM subpackages (apiserver, apiclient, updog, migrator, …; `-fips-bin` variants for several); `os.spec` also carries the systemd units and TOML config templates for them |
| `packages/early-boot-config` | early-boot-config/*, api, constants, imdsclient | `early-boot-config` + user-data provider binaries |
| `packages/netdog` | netdog, dogtag | network/hostname helpers |
| `packages/rottweiler` | rottweiler | storage encryption helper |
| `packages/static-pods` | static-pods | kubelet static-pod manifests from settings |
| `packages/host-ctr` | host-ctr (Go) | host-container launcher |
| `packages/ecs-gpu-init` | ecs-gpu-init (Go) | writes NVIDIA GPU info for the ECS agent |

`packages/release` has no sources: it is the systemd unit/drop-in/target collection that assembles a bootable system (mounts, `repart-*`, `prepare-*`, `encrypt-*`/`unlock-*`, `measure-*`, boot-phase targets `preconfigured.target`/`configured.target`) with subpackages `managed`, `fips`, `crypt`, `ephemeral-crypt`, `swap`.

**Third-party packages** (the other ~120) are `Cargo.toml` + `<name>.spec` + patches. Multiple versions of one upstream are separate directories (`kubernetes-1.31`…`1.36`, `containerd-1.7`/`2.2`/`2.3`, `docker-*-25`/`-29`, `systemd-252`/`257`, `ecr-credential-provider-1.31`…`1.36`) with `package-name` overriding the dot-less crate name. Go packages without a vendored tree set `bundle-modules = ["go"]` so buildsys pre-vendors modules (network is unavailable inside the build container). No kernel is built in this kit.

## 2. Runtime software: the first-party workspace

`sources/Cargo.toml` is an independent Rust workspace (resolver 1, 59 members) with shared `deny.toml`, `clippy.toml`, `clarify.toml`. It is the project rust-analyzer opens (`.vscode/settings.json`). Groups:

### Settings API system (`sources/api/`) — starts in this order at boot (per `sources/api/README.md`)

| Component | Path | Responsibility |
|---|---|---|
| migrator | `api/migration/migrator` | Runs data-store migrations when on-disk datastore version ≠ booting image version (`/etc/os-release`) |
| storewolf | `api/storewolf` | Creates the filesystem datastore and populates defaults into a pending `bottlerocket-launch` transaction |
| apiserver | `api/apiserver` | HTTP-over-Unix-socket server (actix-web) exposing `/settings` etc.; OpenAPI spec at `api/openapi.yaml`; owns the datastore (`api/datastore` lib) |
| early-boot-config | `early-boot-config/` | Discovers user-data providers in `/usr/libexec/early-boot-config/data-providers.d` (IMDS, EC2 identity doc, local file/defaults/overrides, VMware guestinfo/CD-ROM) and sends user data to the API |
| sundog | `api/sundog` | Runs *setting generators* (bork, pluto, schnauzer, shibaken, netdog subcommands, dogtag) for settings needing runtime info |
| settings-committer | `api/settings-committer` | Commits the launch transaction |
| settings-applier / thar-be-settings | `api/thar-be-settings` | Renders handlebars config templates and restarts affected services after commits |
| apiclient | `api/apiclient` | CLI + library for the API (`get`, `set`, `update`, `exec`, `raw`, `network configure`) |
| others | `api/certdog`, `corndog`, `host-containers`, `bootstrap-containers`, `prairiedog`, `thar-be-updates`, `thar-be-registries`, `simple-settings-plugin` | CA certs, sysctls, host/bootstrap containers, boot ops, update API backend, registry mirrors, settings plugin (uses `abi_stable`) |

The settings **data model** lives in `sources/models` and delegates to a settings plugin (cdylib) loaded at runtime; model types come from the external [bottlerocket-settings-sdk](https://github.com/bottlerocket-os/bottlerocket-settings-sdk) (git dependency, see `document/tech`).

### Update system (`sources/updater/`)
`updog` (TUF client via `tough`, downloads image to inactive partition, honors waves) → `signpost` (flips GPT priority bits so GRUB boots the new partition set); `update_metadata`, `block-party`, `waves` are libraries. Driven by `thar-be-updates` behind `apiclient update`. Long version: `sources/updater/README.md`.

### Storage & encryption
`rottweiler` (LUKS2 block devices, fscrypt directories, TPM2 PCR measurements; design in `docs/ENCRYPTED_STORAGE.md`), `ghostdog` (ephemeral disks, EFA/NVIDIA PCI detection), `xfscli`, `bottlerocket-image-features` (reads `/usr/share/bottlerocket/image-features.env`: `IN_PLACE_UPDATES`, `ENCRYPTED_STORAGE`, `EPHEMERAL_ENCRYPTION_KEYS`).

### Networking
`netdog` (systemd-networkd helper: resolv.conf, hostname, `net.toml`; includes `systemd-derive` proc-macro), `dogtag` (hostname detectors), `imdsclient` (IMDSv2 library), `pciclient`.

### Operations & compliance
`logdog` (support tarball), `metricdog` (anonymous health pings), `bloodhound` (CIS/FIPS check orchestrator), `cfsignal` (CloudFormation signals), `driverdog` (link/load kernel modules), `bootstrap-commands`, `static-pods`, `image-verifiers` (containerd image-verifier plugins: notation, digest), `whippet` (dbus-broker launcher), `brush` (sanitizing `sh -c` shim, installed as `/usr/bin/sh`).

### Shared libraries
`constants` (e.g. `API_SOCKET`, `LAUNCH_TRANSACTION`), `bottlerocket-release`, `bottlerocket-crypto-provider` (rustls provider with runtime FIPS detection), `parse-datetime`, `retry-read`, `generate-readme` (build.rs README generation), `aws-smithy-experimental` (vendored smithy-rs crate).

### Go modules
`sources/host-ctr` (starts host containers on the "host" containerd; ECR auth; urfave/cli v2) and `sources/ecs-gpu-init` (NVML → `/var/lib/ecs/gpu/nvidia-gpu-info.json`). Listed in `Makefile` as `GO_MODULES`.

## 3. Flow of a settings change at runtime
`apiclient set k=v` → HTTP to `/run/api.sock` → apiserver writes pending key to datastore → commit → apiserver invokes thar-be-settings with changed keys → queries metadata for affected config files/services → renders templates → restarts services.

## 4. Periphery
- `advisories/<kit-version>/BRSA-*.toml` — security / end-of-life advisories: `[advisory]` header plus `[[advisory.products]]` entries naming affected package and patched version/epoch, and an `[updateinfo]` block.
- `tools/` — `install-twoliter.sh`, `validate-changelog.sh` (CI), `collect-kernel-config`/`diff-kernel-config` (kernel config diff helpers; they expect kernel RPMs that this kit does not build).
- `.github/workflows/` — see `document/development`.
