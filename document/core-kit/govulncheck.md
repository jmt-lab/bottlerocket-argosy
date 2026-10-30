---
type: Guide
description: How to scan Go packages in bottlerocket-core-kit for known vulnerabilities with govulncheck in source mode inside the bottlerocket-sdk container — finding Go packages by their cross_go spec macros, resolving the SDK image and default Go version from Twoliter.toml, picking each package's Go toolchain (GO_MAJOR), scanning the exact upstream archive from Cargo.toml or the first-party sources/ tree, and reading the results.
---

# govulncheck for core-kit Go packages

Use before a release, after bumping a Go package (`document/core-kit/updating-third-party-packages`), or for a periodic audit. `skill/govulncheck-source` wraps these steps in scripts. Needs Docker and Python 3.11+ (`tomllib`).

## Why source mode, in the SDK

- `govulncheck` in source mode reports only vulnerabilities whose affected symbols are reachable from the package's code, which is far less noisy than a module-list scan.
- It must use the **same Go toolchain the package builds with**, so the scan runs in the `bottlerocket-sdk` image pinned by the kit.
- It must scan the **exact source that ships**: the archive listed in the package's `Cargo.toml` `external-files`, not a `git clone` (a clone can drift from the released tarball).

## Which packages are Go

A package is Go if its spec uses any SDK Go macro; all contain `cross_go` (`%set_cross_go_env`, `%set_cross_go_flags[_static]`, `%cross_go_setup`, `%cross_go_configure`). Grepping only for `%set_cross_go_flags` misses packages that call `%cross_go_configure`.

```bash
grep -rl cross_go --include='*.spec' packages | xargs -n1 dirname | xargs -n1 basename | sort -u
```

## Which SDK and which Go

- SDK image = `<[vendor.bottlerocket].registry>/<[sdk].name>:v<[sdk].version>` from the kit's `Twoliter.toml`, e.g. `public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.70.0`.
- The SDK installs Go toolchains under `/usr/libexec/go-<major>/`; it ships two, and the **default is the lower one**.
- A spec that needs the newer toolchain sets `export GO_MAJOR="1.NN"` in `%build`. Expand the spec with `rpmspec -P` inside the SDK (after copying `/usr/lib/rpm/platform/x86_64-bottlerocket/macros` to `~/.rpmmacros`) to read `GO_MAJOR`, `Version` and `URL`; fall back to the SDK default when `GO_MAJOR` is absent.

## Where the source comes from

| Package kind | Cargo.toml has | Source to scan |
|---|---|---|
| Upstream (third-party) | `[[package.metadata.build-package.external-files]]` | Download the first entry whose `url`/`path` is an archive (`.tar.gz`, `.tgz`, `.tar.xz`, `.tar.bz2`, `.tar.zst`, `.zip`), skipping signatures and patches; extract; descend into the single top-level directory |
| First-party | `source-groups = ["<group>"]` | `sources/<group>/` in the kit (e.g. `host-ctr`) |

Quirks: moby/docker ship `vendor.mod`/`vendor.sum` instead of `go.mod` — copy them to `go.mod`/`go.sum` before scanning. Some archives keep `go.mod` in a subdirectory; search a few levels down.

## Running the scan

Inside the SDK, mounting the source read-only:
```bash
export GOBIN=/tmp/bin PATH=/usr/libexec/go-<major>/bin:/tmp/bin:$PATH
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck -C <dir-with-go.mod> -show verbose ./...
```
Exit code 3 means vulnerabilities were found, 0 means clean. Count findings by `Vulnerability #` lines.

The scan sees pristine upstream source, so Bottlerocket patches from the spec are not applied. Before reporting a finding as open, check whether a `packages/<name>/*.patch` already fixes it.

Report as a table:

| Package | Version | Go | Vulns | Status |
|---|---|---|---|---|
| runc | 1.3.6 | 1.25 | 0 | clean |

## Troubleshooting

| Problem | Fix |
|---|---|
| Docker not running | Start the daemon; check `docker info`. |
| SDK pull fails | `aws ecr-public get-login-password --region us-east-1 \| docker login --username AWS --password-stdin public.ecr.aws` (public ECR also allows anonymous pulls at lower rate limits). |
| `no go.mod` | Archive layout differs: look for `go.mod` deeper, or `vendor.mod` (moby). |
| Download fails | Check the `external-files` URL is still reachable; use it as-is. |
