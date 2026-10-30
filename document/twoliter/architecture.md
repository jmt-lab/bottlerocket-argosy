---
type: Reference
description: Components of Twoliter, where their code lives, how the embedded tools get into the binary, and how a build/make run flows from CLI to docker build.
---

# Architecture

Twoliter is a **facade over Bottlerocket's cargo-make build system**. The CLI resolves project dependencies, extracts an embedded toolchain into the project's `build/tools/`, then execs `cargo make` on the host with a curated environment. Real work (RPM builds, image creation, publishing) happens in `Makefile.toml` tasks that call the extracted helper binaries, which in turn run `docker build` against the Bottlerocket SDK image.

## 1. Component map

### The CLI crate — `twoliter/`

| Module | Responsibility |
|---|---|
| `src/main.rs` | `#[tokio::main]`; parse args → `init_logger` → `preflight::preflight()` → `cmd::run` |
| `src/cmd/mod.rs` | clap `Args`/`Subcommand`; `build`, `fetch`, `make`, `update`, `publish_kit`, `debug`, `build_clean` submodules |
| `src/preflight.rs` | Requires `gzip` and `lz4` on `PATH` (`REQUIRED_TOOLS`) |
| `src/project/mod.rs` | `Project<L: ProjectLock>` — parsed `Twoliter.toml`; typestate `Unlocked` → `SDKLocked` → `Locked`; `find_and_load` walks up from cwd like cargo; loads `Twoliter.override`; warns on deprecated `Release.toml` |
| `src/project/migrate/` | Schema migration of `Twoliter.toml` content before validation (`parser.rs` v1/v2 structs, `migrator.rs` `MigrationRegistry`, `implementations/v1_to_v2.rs`) |
| `src/project/lock/mod.rs` | `Lock` (`Twoliter.lock`): `create` (= `twoliter update`), `load` (re-resolves and **fails if the lock is stale**), `fetch` (extract kits, 8 concurrent), `synchronize_metadata` → `build/external-kits/external-kit-metadata.json` (canonical JSON) |
| `src/project/lock/image.rs` | `LockedImage {name, version, vendor, source, digest}`; `ImageResolver` — pulls manifest/config via krane, reads kit metadata from OCI label `dev.bottlerocket.kit.v3` (base64 JSON), computes digests, `extract`s layers |
| `src/project/lock/archive.rs` | `OCIArchive` — pull image to an OCI layout dir and unpack layers (4 concurrent) |
| `src/project/lock/verification.rs` | `VerificationTagger` writes `.sdk-verified` / `.kits-verified` marker files in `build/external-kits/`; `Makefile.toml` tasks refuse to run without them |
| `src/project/vendor.rs` | `ArtifactVendor::{Verbatim, Overridden}` — registry/repo for an image, honoring `Twoliter.override` |
| `src/docker/image.rs` | `ImageUri { registry, repo, tag }` |
| `src/tools.rs` | `install_tools(dir)`: wipe dir, unpack the embedded tarball, write each embedded binary with mode 0755 and a uniform mtime (taken from `build.Dockerfile`) |
| `src/cargo_make.rs` | `CargoMake` builder: runs `cargo make --disable-check-for-updates --makefile … --cwd … -e K=V … <task>`; always sets `TLPRIVATE_SDK_IMAGE`, `BUILDSYS_OUTPUT_GENERATION_ID`, `TWOLITER_VERSION`; passes through host env matching `BUILDSYS_*`, `PUBLISH_*`, `REPO_*`, `BOOT_CONFIG*`, `AWS_*` plus an allowlist (`ENV_VARS`); **rejects** `BUILDSYS_SDK_NAME/VERSION`, `BUILDSYS_REGISTRY`, `BUILDSYS_OUTPUT_GENERATION_ID` from the host |
| `src/compatibility.rs` | `LATEST_TWOLITER_PROJECT_SCHEMA_VERSION = 2`, `SUPPORTED_TWOLITER_LOCK_SCHEMA_VERSION = 2`, `SUPPORTED_KIT_METADATA_VERSION = "v3"` |
| `src/common.rs` | `exec`/`exec_log` process helpers; `fs` wrappers (its `canonicalize` uses `path_absolutize`, see `document/twoliter/conventions`) |

`twoliter/src/docker/Twoliter.dockerfile` exists but is referenced nowhere — treat as orphaned. `twoliter/Cargo.toml` lists `[build-dependencies]` although the crate has no `build.rs` (vestigial).

### Embedding pipeline

Three mechanisms put the tools inside the `twoliter` binary:

1. **Cargo artifact deps (`bindeps`, nightly)** — root `Cargo.toml` `[workspace.dependencies]` declares each helper with `artifact = ["bin:<name>"]`; cargo builds it and exposes `CARGO_BIN_FILE_<NAME>`. Enabled by `.cargo/config.toml` `[unstable] bindeps = true`.
2. **Shim crates** `twoliter/src/tool-crates/<tool>/src/lib.rs` — one line each: `pub const X: Archive = include_archive_from_env!("CARGO_BIN_FILE_…")`. The macro (`tools/include-env-compressed/`) embeds the file **zstd-compressed in release builds**, raw in debug.
3. **Script bundle** — `twoliter/src/tool-crates/embedded-bundle/build.rs` tars an explicit allowlist from `twoliter/embedded/` (symlinked as `embedded-bundle/embedded`) into `$OUT_DIR/tools.tar.gz` (zlib-compressed); `lib.rs` exposes `EMBEDDED_BUNDLE`. Files not on the allowlist (e.g. `embedded/tests/`) are not shipped.

`krane` (go-containerregistry **0.21.8**) is not built from source: `tools/krane/build.rs` runs `tools/build-cache-fetch hashes/<platform>` to download the SHA512-pinned release tarball from `https://cache.bottlerocket.aws` (GitHub fallback only with `UPSTREAM_SOURCE_FALLBACK=true`) and embeds it the same way. `tools/krane` is not in `[workspace] members` but is a workspace member implicitly via path dependency.

Binaries written by `install_tools`: `advisory-checker buildsys pcrsys pipesys tuftool ukisys eif-builder unplug krane pubsys-setup pubsys`. `tuftool` is the crates.io crate (`0.17`), everything else is in `tools/`.

### Embedded scripts — `twoliter/embedded/`

| File | Role |
|---|---|
| `Makefile.toml` (≈1.8k lines) | The whole build/publish task graph (see §3). `[env]` defines every `BUILDSYS_*`/`PUBLISH_*`/`REPO_*` default; `[env.private] TLPRIVATE_SDK_IMAGE` must be set by Twoliter |
| `build.Dockerfile` | Multi-stage: Section 1 builds RPMs from spec (`buildsys build-package`), Section 2 makes kits, Section 3 makes images. Needs Dockerfile syntax 1.4.3 ⇒ Docker ≥ 23.0.0 |
| `rpm2img`, `img2img`, `imghelper`, `partyplanner` | Turn RPMs into disk images / repack existing images; partition layout GUIDs; dm-verity; Secure Boot |
| `rpm2eif`, `eif2eif`, `eif-sign-helper` | Nitro Enclave EIF build/repack; translate `Infra.toml [eif]` into `eif-builder` flags |
| `rpm2kit`, `ocihelper` | Build a kit image (yum repo as OCI image) |
| `rpm2kmodkit`, `rpm2migrations`, `guest-images-helper` | kmod-kit archive; migration tarballs; embed guest variant images into a host variant |
| `docker-cargo`, `docker-go` | Run cargo/go in the SDK container for vendoring |
| `metadata.spec`, `builder-group.spec` | RPM specs generated per build |
| `waves/*.toml` | Update-wave policies for `pubsys repo` |
| `tests/*.sh` | Bash unit tests (run via `embedded-bundle/tests/*.rs` wrappers; three scripts have no wrapper — see `document/twoliter/development`) |

### Helper crates — `tools/`

| Crate | Kind | Responsibility | Talks to |
|---|---|---|---|
| `buildsys` | bin + lib | Called from package/kit/variant `build.rs`; subcommands `build-package`, `build-kit`, `build-variant`, `repack-variant`; assembles `docker build` against `build.Dockerfile`; `manifest.rs` defines the `[package.metadata.build-*]` schema (incl. `image-format`, `guest-images`); `cache.rs` is the SHA512-verified lookaside source fetcher | Docker CLI, `https://cache.bottlerocket.aws`, `pipesys` server |
| `pipesys` | bin + lib | Pass a directory FD over an abstract Unix socket so build containers can write to host dirs (`serve`, `link`) | Linux UDS/SCM_RIGHTS, inotify |
| `pubsys` | bin | `repo`, `validate-repo`, `check-repo-expirations`, `refresh-repo`, `fetch-variant`, `ami`, `publish-ami`, `validate-ami`, `ssm`, `promote-ssm`, `validate-ssm`, `upload-ova`, `publish-kit` | TUF via `tough`, AWS EC2/EBS/KMS/SSM/STS, `coldsnap`, `govc` in SDK container, krane |
| `pubsys-setup` | bin | Fetch or generate TUF root role + key (shells out to `tuftool`) | HTTPS |
| `pubsys-config` | lib | `Infra.toml`/`Infra.lock` schema (repos, signing keys `file|kms|ssm|env`, AWS, VMware `GOVC_*`, OCI vendors, `[eif]` signing) | — |
| `eif-builder` | bin + lib | Build / `resign` / `describe` Nitro Enclave EIFs; PCR0 COSE signing locally or via KMS | AWS KMS, aws-lc-rs |
| `pcrsys` | bin | Predict TPM PCR values from a disk image (`disk`) or AMI (`ami`) | AWS EC2/EBS |
| `ukisys` | bin | `derive-stub`: strip signature/sections from a signed UKI | — |
| `unplug` | bin | seccomp wrapper denying non-`AF_UNIX` sockets (network-free builds) | Linux seccomp |
| `advisory-checker` | bin | Check kit RPM specs against BRSA advisory TOMLs | `rpm`, `rpmspec` in SDK |
| `oci-cli-wrapper` | lib | `ImageTool` trait over krane: pull/config/manifest/push/index | krane |
| `krane` (`krane-bundle`) | lib | Embedded prebuilt krane | cache.bottlerocket.aws at build time |
| `amispec`, `serde-templated(-derive)` | lib | Typed, handlebars-templatable EC2 RegisterImage spec | — |
| `update-metadata`, `parse-datetime` | lib | TUF `manifest.json` model with waves/migrations; RFC3339-or-"in 7 days" parsing | — |
| `bottlerocket-variant` | lib | Parse `platform-runtime-version-flavor` variant strings, emit cargo cfgs | env `VARIANT` |
| `buildsys-config`, `error-utils`, `include-env-compressed(-macro)` | lib | Path constants; AWS error formatting; the embedding macro | — |
| `attribution/`, `build-cache-fetch` | scripts | License attribution tarball (in SDK container); pinned cache download | Docker, curl |

## 2. Project model (what users write)

```
<project>/
├── Twoliter.toml        # schema-version (2), release-version, project-vendor, [sdk], [vendor.<name>] registry, [[kit]] name/version/vendor
├── Twoliter.lock        # written by `twoliter update`; sdk + kit sources/digests; schema 2
├── Twoliter.override    # optional: [<vendor>.<artifact>] name=/registry= to redirect an image (used by tests)
├── Infra.toml           # publishing config (pubsys-config); optional
├── packages/ kits/ variants/ sources/ sbkeys/   # cargo workspaces whose build.rs call buildsys
└── build/               # outputs: tools/ external-kits/ rpms/ kits/ images/ state/ logs/ metadata/
```

Schema-1 files (no `project-vendor`) are migrated in memory on load. Images are addressed as `<vendor.registry>/<name>:v<version>`. Kit images carry their own dependency metadata in the `dev.bottlerocket.kit.v3` label; `Lock::resolve` walks that graph transitively and errors on two versions of one kit. Fixture examples: `tests/projects/local-kit/Twoliter.toml` (+ `.override`), `tests/projects/external-kit/Twoliter.toml`.

## 3. Flow of a run

`twoliter build variant hello-ootb --arch aarch64` (`twoliter/src/cmd/build.rs`):

1. `main` → `preflight` (gzip, lz4 present) → `cmd::run`.
2. `project::load_or_find_project` — find `Twoliter.toml`, migrate schema, validate vendors, load `Twoliter.override`, clean stale `.sdk-verified`/`.kits-verified` tags.
3. `project.load_lock::<Locked>()` — re-resolve SDK + kit graph with krane, compare to `Twoliter.lock`; mismatch ⇒ error "run `twoliter update`". Write verification tags.
4. `project.fetch(arch)` — extract every locked kit into `build/external-kits/<kit>/` and write `external-kit-metadata.json`.
5. `install_tools(build/tools)` — unpack scripts + binaries.
6. `CargoMake::new(sdk_uri).env(...).makefile(build/tools/Makefile.toml).project_dir(...).exec("build")` — runs **on the host**: `cargo make -e TLPRIVATE_SDK_IMAGE=… -e BUILDSYS_ARCH=… -e BUILDSYS_VARIANT=… -e BUILDSYS_VERSION_IMAGE=<release-version> -e GO_MODULES=… -e TWOLITER_TOOLS_DIR=… build`.
7. Inside `Makefile.toml`: `build` = `check-licenses` + `build-variant`; `build-variant` depends on `fetch` (`fetch-sdk` — refuses without `.sdk-verified`, `krane pull` + `docker load` the SDK; `fetch-sources`; `fetch-vendored`), `build-sbkeys`, `publish-setup`, `validate-kits`, then runs `cargo build --manifest-path variants/${BUILDSYS_VARIANT}/Cargo.toml`. Cargo runs each package/kit/variant `build.rs`, which execs `${TWOLITER_TOOLS_DIR}/buildsys build-package|build-kit|build-variant`. (`twoliter build kit` runs task `build-kit`, whose deps are `check-cargo-version`, `fetch`, `publish-setup`, `validate-kits`.)
8. `buildsys` starts a `pipesys` server for the output dir and runs `docker build -f build/tools/build.Dockerfile --build-arg SDK=$TLPRIVATE_SDK_IMAGE …`; inside, `rpm2img`/`rpm2kit`/… produce artifacts under `build/rpms`, `build/kits`, `build/images/<arch>-<variant>/<version>/`.

`twoliter make` (`src/cmd/make.rs`) is the same pipeline but for any task; it skips kit verification (only `SDKLocked`) when the task is not one of `build-package build-kit build-variant build-all build default` **and** `Twoliter.toml` names an explicit `[sdk]`. `twoliter update` stops after step 3's `Lock::create`; `twoliter fetch` after step 4; `twoliter publish kit` runs task `publish-kit` with `PUBLISH_VENDOR`/`PUBLISH_KIT_REPO`.

Task inventory in `Makefile.toml` (grep `^[tasks.`): setup/fetch family, `unit-tests`, `check*` lints, `build-sbkeys`, `boot-config`, `validate-kits`, `cargo-metadata`, `build-package|kit|variant|all`, `repack-variant`, `check-licenses`, `publish-setup`, `repo`, `validate-repo`, `fetch-variant`, `fetch-ova`, `check-repo-expirations`, `refresh-repo`, `ami*`, `grant-ami`/`revoke-ami`, `ssm`/`promote-ssm`/`validate-ssm`, `publish-kit`, `upload-ova`, `vmware-template`, `clean*`, `purge-*`, `default` (alias of `build`).

## 4. Design-vs-reality notes

`docs/design/README.md` is the rationale; where it diverges from the code it says so inline: kit metadata lives in an image **label** (not a `-metadata` image); `cargo make` and `docker` run **on the host** (no docker-socket container); `twoliter new` is unimplemented; Cargo-registry-based `twoliter update` was replaced by the krane-driven resolver in `src/project/lock/`. `docs/design/custom-variant-considerations.md` explains why a custom variant name still needs its own `settings-defaults` subpackage in Bottlerocket.
