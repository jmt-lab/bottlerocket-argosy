---
type: Guide
description: End-to-end local loop for testing kit changes in a Bottlerocket variant without cloud credentials — run a local OCI registry, publish a kit to it via a git-ignored Infra.toml vendor, redirect the variant's kit to it with Twoliter.override, update the lock, build the image, clean up; plus host prerequisites and troubleshooting.
---

# Local kit → registry → variant workflow

Use this to test changes in `bottlerocket-core-kit` or `bottlerocket-kernel-kit` inside a variant image built from `bottlerocket`, without publishing to ECR. Repo-level detail lives in `document/core-kit/development`, `document/kernel-kit/development`, `document/bottlerocket/development` and `document/twoliter/*`. The examples assume sibling checkouts of the kit and `bottlerocket` repos.

## Mental model

```
bottlerocket-core-kit ──make build──▶ RPMs ──make publish VENDOR=local──▶ local OCI registry
bottlerocket-kernel-kit ───────────────────────────────────────────────▶   localhost:5000
                                                                              │ twoliter fetch
bottlerocket (variants, settings, migrations) ── cargo make ──────────────◀──┘
                                                     └──▶ build/images/…
```

Use the repos' Makefile targets rather than calling `twoliter` directly (exception: `./tools/twoliter/twoliter update` in `bottlerocket` to refresh the lock). Kits use GNU `make`; the `bottlerocket` repo uses `cargo make`.

## Step 1 — run a local registry

```bash
docker run -d --name kit-registry -p 5000:5000 -v kit-registry-data:/var/lib/registry registry:2
curl -s localhost:5000/v2/_catalog          # {"repositories":[]}
```
Any free port works; use it consistently below.

## Step 2 — build and publish a kit

In the kit repo, create a git-ignored `Infra.toml` with a `local` vendor:
```toml
[vendor.local]
registry = "localhost:5000"
```
```bash
make build                             # ARCH=x86_64|aarch64 ; UPSTREAM_SOURCE_FALLBACK=true for restricted sources (e.g. NVIDIA)
make publish VENDOR=local
curl -s localhost:5000/v2/_catalog     # kit should appear
```
Other kit targets: `make fetch`, `make update` (refresh `Twoliter.lock`), `make twoliter <task>` (forward to Twoliter's cargo-make tasks), `make prep` (install pinned Twoliter).

## Step 3 — point the variant at the local kit

In `bottlerocket`, set the kit's `version` in `Twoliter.toml` to the version you published (the kit's `Twoliter.toml` `release-version`). Then redirect just that kit image to the local registry with a git-ignored `Twoliter.override`; entries are `[<vendor>.<artifact>]` tables, so other kits keep coming from upstream:
```toml
[bottlerocket.bottlerocket-core-kit]   # <vendor name used in Twoliter.toml>.<kit name>
registry = "localhost:5000"
```
```bash
./tools/twoliter/twoliter update       # refresh Twoliter.lock against the override
```

## Step 4 — build the variant

```bash
cargo make                                       # default variant (aws-k8s-1.32)
cargo make -e BUILDSYS_VARIANT=aws-k8s-1.31
cargo make -e BUILDSYS_ARCH=aarch64
cargo make -e BUILDSYS_JOBS=4                    # limit parallelism
cargo make -e PUBLISH_REGIONS=us-west-2 ami      # register an AMI
ls -lh build/images/
```

## Step 5 — clean up

```bash
rm Twoliter.override                   # in bottlerocket; also revert the Twoliter.toml version and Twoliter.lock
rm Infra.toml                          # in the kit repo (only if you created it for this)
docker rm -f kit-registry              # add `docker volume rm kit-registry-data` to drop published kits
```
Never commit `Infra.toml`, `Twoliter.override`, or a `Twoliter.lock` that resolved against the local registry.

## Host prerequisites

- Ubuntu: `apt install build-essential openssl libssl-dev pkg-config liblz4-tool cmake clang libclang-dev`; Fedora: `dnf install make automake gcc openssl openssl-devel pkg-config lz4 perl-FindBin perl-lib cmake clang`.
- rustup + `cargo install cargo-make`; Docker ≥ 20.10.10 with BuildKit and containerd-snapshotter enabled in `/etc/docker/daemon.json`, or `crane` (recommended, daemonless). User in the `docker` group.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `twoliter not found` | `make prep` |
| kit build: `vendor 'local' not found` | `Infra.toml` missing or lacks `[vendor.local]` |
| variant build: `failed to pull kit` / `kit not found in registry` | check `localhost:5000/v2/_catalog`; ensure `make publish` ran and the `Twoliter.toml` version matches |
| lock out of sync | rerun `./tools/twoliter/twoliter update` |
| stale build cache | `rm -rf build/ && make build` |
| `connection refused` | registry container not running: `docker start kit-registry` |
| port already in use | pick another host port and update `Infra.toml` / `Twoliter.override` |
| docker permission denied | `sudo usermod -aG docker $USER`, re-login |
