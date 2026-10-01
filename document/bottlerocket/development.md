---
type: Guide
description: How to build, test, lint, publish, and run Bottlerocket from this repo — the actual cargo make commands, env knobs, prerequisites, and CI behaviour.
---

# Development

Everything goes through `cargo make` (cargo-make reading `Makefile.toml`), which installs the pinned Twoliter and delegates to `twoliter make <task>`. Run commands from the repo root. Put `-e VAR=value` overrides **before** the task name.

## Prerequisites (from `BUILDING.md` and `.github/actions/setup-node/action.yml`)
| Need | Detail |
|---|---|
| Disk / CPU | >80 GB free; scales to 32+ cores; first build 12 min (fast box) to 3–4 h |
| OS packages | Ubuntu: `apt install build-essential openssl libssl-dev pkg-config liblz4-tool`. Fedora: `yum install make automake gcc openssl openssl-devel pkg-config lz4 perl-FindBin perl-lib` |
| Rust | stable via rustup (≥1.51); `cargo install cargo-make`; CI also adds `rustup component add rustfmt` |
| Docker | ≥20.10.10 with BuildKit, user in `docker` group (`DOCKER_BUILDKIT=1` is set by Makefile.toml) |
| Twoliter | auto-installed to `tools/twoliter/` by `cargo make install-twoliter` (binary download with sha256 check, falls back to `cargo install` from git) |
| Network | pulls SDK/kits from `public.ecr.aws/bottlerocket`; `BUILDSYS_UPSTREAM_SOURCE_FALLBACK=false` by default (lookaside cache only) |
| Optional | `qemu` for `tools/start-local-vm`; AWS CLI for AMI/SSM tasks; `kind` for TestSys |

## Build
```shell
cargo make                                   # default task = build; default variant aws-k8s-1.32, arch = uname -m
cargo make -e BUILDSYS_VARIANT=aws-k8s-1.36 -e BUILDSYS_ARCH=aarch64
cargo make -e BUILDSYS_JOBS=4                # concurrent docker builds (default 8)
cargo make build-all                         # what CI runs
cargo make -e BUILDSYS_VARIANT=aws-k8s-1.36-nvidia -e BUILDSYS_UPSTREAM_SOURCE_FALLBACK=true   # needs Licenses.toml, see BUILDING.md
cargo make -e BUILDSYS_ALLOW_FAILED_LICENSE_CHECK=true      # local hacking without license data
```
Outputs: RPMs in `build/rpms/`, images in `build/images/<arch>-<variant>/<version>-<gitsha>/`, state in `build/state/`. Version comes from `Release.toml`; build id from `git describe`.

Other build-related tasks: `build-package`, `build-variant`, `repack-variant`, `fetch-variant`, `fetch-friendly-variant`, `fetch-ova`, `build-sbkeys`, `boot-config`, `validate-boot-config`, `fetch-licenses`, `check-licenses`, `clean`, `clean-{sources,packages,images,repos,state}`, `purge-cache`, `purge-cargo`, `purge-go-vendor`.

Secure Boot keys: a `local` profile is auto-generated under `sbkeys/local/`; choose another with `-e BUILDSYS_SBKEYS_PROFILE=<name>` (and `BUILDSYS_SBKEYS_DIR`). See `sbkeys/README.md`.

## Check / lint (what a PR must pass)
```shell
cargo make check            # "review and patch readiness" umbrella; CI runs this before build-all
cargo make check-fmt
cargo make check-clippy
cargo make check-lints
cargo make check-shell
cargo make check-golangci-lint
cargo make check-migrations
cargo make check-cargo-version
```
`Makefile.toml` only forwards these names; which sub-checks `check` bundles is defined inside Twoliter. They operate on `sources/` and the shell scripts. `sources/deny.toml` governs cargo-deny license/duplicate policy.

## Unit tests
```shell
cargo make unit-tests
cargo make -e BUILDSYS_VARIANT=aws-ecs-2 -e BUILDSYS_ARCH=x86_64 unit-tests   # some code is variant-conditional
```
Tests live inline in `sources/` crates (e.g. `sources/models/src/generator.rs`, `sources/api/datastore/`). There is no top-level `tests/` directory in git (`/tests` is git-ignored and reserved for TestSys files).

## Integration tests (TestSys) — see `TESTING.md`
Requires a built image + AMI and a "testsys cluster" (kind for dev). Key env: `TESTSYS_KUBECONFIG`, `TESTSYS_TEST` (`quick` default | `conformance` | `migration` | `workload` | custom), `TESTSYS_AWS_SECRET_NAME`, `TESTSYS_INSTANCE_TYPE`, `TESTSYS_REGION`; optional `Test.toml` at repo root (git-ignored). `TESTING.md` links to `tools/testsys/Test.toml.example`, which no longer exists here (it lives with testsys in the Twoliter repo).
```shell
cargo make setup-test
cargo make testsys add secret map --name creds access-key-id=... secret-access-key=...
cargo make -e BUILDSYS_VARIANT=aws-k8s-1.32 -e BUILDSYS_ARCH=x86_64 -e PUBLISH_REGIONS=us-west-2 ami
cargo make -e BUILDSYS_VARIANT=aws-k8s-1.32 -e BUILDSYS_ARCH=x86_64 test
cargo make watch-test            # also: watch-test-all, log-test, clean-test, reset-test, reset-single-test, uninstall-test, purge-test
cargo make -e TESTSYS_TEST=migration test
```

## Run locally (QEMU/KVM) — see `QUICKSTART-LOCAL.md`
```shell
cargo make -e BUILDSYS_VARIANT=metal-dev
tools/start-local-vm --variant metal-dev --arch $(uname -m) --inject-file net.toml
```
`start-local-vm` (flags: `--arch`, `--variant`, `--product-name`, `--host-port-forwards`, `--vm-memory`, `--vm-cpus`, `--force-extract`, `--inject-file LOCAL[:IMAGE_PATH]`, `--firmware-code/--firmware-vars`, `--os-image-size/--data-image-size`) forwards host 2222→guest 22 by default and injects files such as `net.toml` into the private partition.

## Publish — see `PUBLISHING.md`, `PUBLISHING-AWS.md`, `PUBLISHING-VMWARE.md`
Copy `tools/pubsys/Infra.toml.example` to `Infra.toml` (git-ignored), then:
```shell
cargo make repo                          # TUF repo under build/repos/<repo>/<name-version>/
cargo make validate-repo | check-repo-expirations | refresh-repo
cargo make -e PUBLISH_REGIONS=us-west-2 ami      # register/copy AMI; also ami-public, ami-private, grant-ami, revoke-ami, validate-ami
cargo make ssm | promote-ssm | validate-ssm     # SSM parameters from tools/pubsys/policies/ssm/defaults.toml
cargo make upload-ova | vmware-template
```
Relevant knobs: `PUBLISH_REPO` (default `default`), `PUBLISH_INFRA_CONFIG_PATH`, `PUBLISH_EXPIRATION_POLICY_PATH`, `PUBLISH_WAVE_POLICY_PATH`, `RELEASE_START_TIME`, `PUBLISH_AMI_NAME`, `ALLOW_CLOBBER`, `VMWARE_DATACENTERS`, `VMWARE_VM_NAME`, `BUILDSYS_NAME`/`BUILDSYS_PRETTY_NAME` (for remixes; read `TRADEMARKS.md`).

## CI (`.github/workflows/`)
| Workflow | Trigger | Does |
|---|---|---|
| `build.yml` | PR to `develop` (ignores `*.md`, `*.yaml`, `*.example`, images) | matrix x86_64/aarch64 on 32-core runners: `cargo make check` then `cargo make -e BUILDSYS_ARCH=… -e BUILDSYS_JOBS=12 build-all` |
| `weekly.yml` | Mon 02:15 UTC | same build with `GOPROXY=direct` to catch yanked Go modules |
| `cache.yml` | push to `develop` touching `.github/**`, `sources/Cargo.lock`, `tools/pubsys*` | warms `~/.cargo` and `.cargo` caches, `cargo make install-twoliter` |
| `commitlint.yml` | PR opened/edited/sync | `npx commitlint -g .commitlint.config.mjs --from base --to head` |
`dependabot.yaml`: GitHub Actions weekly; cargo/gomod security-only (PR limit 0).

## Contribution workflow (`CONTRIBUTING.md`, `.github/pull_request_template.md`)
Work against `develop`; open an issue first for significant work; PR template asks for issue number, description, testing done, and dual-license (Apache-2.0 OR MIT) agreement. Release tags are `vX.Y.Z`; patch branches `X.Y.x` only when needed. Commit message format is enforced — see `document/conventions`.

## Common change recipes
- **Test unreleased kit changes in a variant**: publish the kit to a local registry and redirect it with `Twoliter.override` — `document/bottlerocket/local-kit-workflow`.
- **Bump a kit/SDK**: edit `Twoliter.toml` and regenerate `Twoliter.lock` (kit-bump commits such as `1dea89e2` touch exactly these two files); commit as `twoliter: Bump <kit> to X`.
- **Bump Twoliter**: edit `TWOLITER_VERSION` and both `TWOLITER_SHA256_*` in `Makefile.toml`.
- **Change a default setting**: edit the topic file in `sources/shared-defaults/` (shared by every variant that links it). To add a variant-specific default, add a new `NN-name.toml` under that variant's `defaults.d/` (symlink to a new shared file, or a real file as the `*-dev` variants do). A new key also needs a migration.
- **Add a migration**: new crate `sources/settings-migrations/v<next>/<name>/`, register in `sources/Cargo.toml`, add its `migrate_v<next>_<name>.lz4` to `Release.toml` `[migrations]`; `cargo make check-migrations`.
- **Add a variant**: follow `variants/README.md` → new `variants/<name>/Cargo.toml`, root `Cargo.toml` member, `sources/settings-defaults/<name>/defaults.d` (symlinks) + `sources/Cargo.toml`, and add subpackages in both `packages/settings-defaults/settings-defaults.spec` and `packages/settings-plugins/settings-plugins.spec`.
