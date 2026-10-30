---
type: Guide
description: How to bump a third-party package to a new upstream version in bottlerocket-core-kit or bottlerocket-kernel-kit — updating Cargo.toml external-files URLs and sha512 hashes (sources and signatures), the spec's Version/Release and the per-package versioning macros (gover, releasever, unversion, ...), GO_MAJOR, GPG key rotation, dropping or rebasing patches, building just that package with upstream source fallback, commit format, and what differs for kernel-kit packages.
---

# Updating third-party packages

Applies to `packages/<name>/` in `bottlerocket-core-kit` and `bottlerocket-kernel-kit`. Each package is a `Cargo.toml` (sources, hashes, build-dependencies) plus `<name>.spec` and optional patches/support files; see `document/core-kit/conventions` for layout and `document/core-kit/packaging-style-guide` plus `styleguide/rpm-spec/*` for spec rules. To *test* the result on a node, see `document/core-kit/package-test-matrix`.

Some packages are versioned by directory (`kubernetes-1.35`, `containerd-2.1`, `ecr-credential-provider-1.30`); pick the directory for the stream you are bumping. Read `Cargo.toml`, the spec, and every patch before editing.

## 1. Cargo.toml — sources and hashes

```toml
[package.metadata.build-package]
releases-url = "https://github.com/opencontainers/runc/releases/"

[[package.metadata.build-package.external-files]]
url = "https://github.com/opencontainers/runc/releases/download/v1.3.6/runc.tar.xz"
path = "runc-v1.3.6.tar.xz"          # optional: local filename override
sha512 = "f5dd1c06..."
```

- Use `releases-url` to confirm the new version exists and find the right artifact.
- In every `external-files` entry that embeds the version — the source archive, its signature (`.asc`, `.sig`, `-asc.txt`), extra tarballs — change the version in `url` **and** in `path` if present. Keep the existing URL pattern.
- Recompute each hash from the real download:
  ```bash
  tmp=$(mktemp -d); curl -fsSL -o "$tmp/f" "<new-url>"; sha512sum "$tmp/f" | cut -d' ' -f1; rm -rf "$tmp"
  ```
- Some versions differ in format between URL and spec (libinih: `r60` in the URL, `Version: 60` in the spec). Update both consistently.
- **Incremental upstream patches** (e.g. readline `readline83-001`…): each is its own `external-files` entry and a `PatchNNNN:` line in the spec. When new ones appear, add entries in the same pattern, and make sure the package `.gitignore` covers them (readline uses `readline83-???`) — downloaded files are not committed.
- **Kubernetes** (`kubernetes-1.NN`): sources come from EKS Distro, `https://distro.eks.amazonaws.com/kubernetes-1-NN/releases/<release>/artifacts/kubernetes/v<1.NN.P>/kubernetes-src.tar.gz`. You are usually given the EKS-D release number; find the matching Kubernetes patch version from the EKS-D release notes (or by checking which `v1.NN.P` URL exists for that release).
- **New build requirement:** add `[build-dependencies] foo = { path = "../foo" }` and refresh the lock (`cargo build` or `cargo update -w` in the kit's workspace so `Cargo.lock` picks it up).

## 2. The spec

- `Version:` → new version, unless a macro drives it (below).
- `Release:` → `1%{?dist}` for a new version (`styleguide/rpm-spec/metadata/release-field`), unless the spec uses a special form.
- Never change `Epoch:`.
- Update `SourceN:` lines whose filenames embed the version or changed (e.g. a new GPG key file).

Versioning patterns — match what the spec already does:

| Pattern | Seen in | What to edit |
|---|---|---|
| `Version:` directly | most packages | `Version:` |
| `%global gover X.Y.Z` | Go packages | `gover` only; `Version:` is derived |
| `%global releasever N` + `%global gover` | `kubernetes-1.NN` | `releasever` (EKS-D release) and `gover` (Kubernetes patch) |
| `%global unversion 2_7_2` | libexpat | underscored version; `Version:` derived via sed |
| `%global ncurses_rev YYYYMMDD` | libncurses | the date; `Version:` stays; `Release: %{ncurses_rev}%{?dist}` is not reset |
| `%global majorminor` + `%global version %{majorminor}.P` | util-linux | the patch number in `version` (and `majorminor` on a minor bump) |

If a `Source` line already references the macro (e.g. `%{gover}`), it needs no change.

**Go toolchain.** The SDK ships two Go versions; specs that need the newer one set `export GO_MAJOR="1.NN"` in `%build`. If upstream's `go.mod` now requires a newer Go than the default, set or bump it. If the SDK default already satisfies upstream, remove the `GO_MAJOR` line (and its trailing blank line). See `styleguide/rpm-spec/metadata/version-pinning`.

## 3. Patches

For each existing patch:

1. Read it; check upstream's changelog, or for a patch with a `From <sha>` header search the new release for that commit.
2. **Upstreamed:** delete the file, its `PatchNNNN:` line and any explicit `%patch` line. Mention it in the commit body.
3. **Still needed, applies cleanly:** keep it.
4. **Still needed, fails:** rebase it. Prefer regenerating from the upstream repo so provenance is preserved:
   ```bash
   git clone <upstream> && cd <upstream>
   git checkout v<new>; git cherry-pick -x <commit>   # resolve conflicts
   git format-patch -1
   ```
5. **Unsure:** keep it and let the build tell you.

Numbering and placement follow `styleguide/rpm-spec/patches/patch-conventions` and `styleguide/rpm-spec/numbering/source-ranges` (`PatchNNNN:` numbers from 1000; files named `0001-…` for upstream/backports and `9001-…` for Bottlerocket-specific changes in core-kit; kernel-kit's series are in `document/kernel-kit/conventions`). If the new version needs a new Bottlerocket-specific fix, explain why in the commit message with cite-style links (`as suggested in [1]` … `[1]: https://…`).

**GPG key rotated** — the build fails in `%gpgverify` (e.g. `gpgverify: Decoding the keyring failed.` or a bad signature):
1. Get the key ID from the new signature (`gpg --list-packets <sig>`) or upstream's release notes.
2. Fetch the public key from upstream or a keyserver; save it as `gpgkey-<FINGERPRINT>.asc` in the package dir (these are committed; other `*.asc` files are git-ignored).
3. Delete the old `gpgkey-*.asc`, update the `SourceN:` line, and update `Cargo.toml` if the key is listed as an external file.

## 4. Build just that package

From the kit repo root (Docker running; `make prep` installs Twoliter):

```bash
# after a version bump: the new sources are not in cache.bottlerocket.aws yet
PACKAGE=<name> BUILDSYS_UPSTREAM_SOURCE_FALLBACK=true make twoliter build-package

# patch-only / spec-only change at the same version
PACKAGE=<name> make twoliter build-package

# other arch
PACKAGE=<name> BUILDSYS_ARCH=aarch64 make twoliter build-package
```

`make twoliter <task>` forwards to Twoliter's embedded cargo-make tasks (`document/core-kit/development`). Build each updated package separately. For a full kit build use `make UPSTREAM_SOURCE_FALLBACK=true`.

| Problem | Fix |
|---|---|
| `invalid character '.' in package name` | Package names with dots use `_` here: `PACKAGE=kubernetes-1_35`. |
| `Failed to fetch https://cache.bottlerocket.aws/...` | Add `BUILDSYS_UPSTREAM_SOURCE_FALLBACK=true`. |
| Dependency RPM not built yet | Build the dependency first, or do a full kit build. |
| `twoliter` not found | Run from the kit root; `make prep`. |
| Docker permission denied | Daemon running and your user in the `docker` group. |
| Missing headers/libs after bump | Upstream changed build requirements: add `BuildRequires:` in the spec and the `[build-dependencies]` path entry in `Cargo.toml`. |

## 5. Validate and commit

- [ ] Every versioned URL/`path` updated; every `sha512` recomputed
- [ ] `Version:` (or the driving macro) is the new version; `Release:` reset as appropriate; `Epoch:` untouched
- [ ] `Source` lines match files; GPG key current
- [ ] Upstreamed patches removed with their spec lines; no stale references
- [ ] `GO_MAJOR` correct or removed
- [ ] Package builds (both arches if it is arch-specific)

One commit per package, signed off: header `<package-name>: update to <version>` (`styleguide/general/commits/header-format`), body noting removed or rebased patches. Write the message in a file and `git commit -s -F <file>`.

## Kernel-kit differences

- **Kernels** (`packages/kernel-<v>/`) are built from Amazon Linux kernel SRPMs, not upstream tarballs. Run `packages/kernel-<v>/latest-kernel-srpm-url.sh` to get the new SRPM URL, update `url`/`sha512` in `Cargo.toml` and `Version`/`Source0` in the spec, then run `make full-config` and commit any `config-full-bottlerocket-*` changes. Single-package builds: `PACKAGE=kernel-6_12 BUILDSYS_ARCH=x86_64 make twoliter build-package` — kernel builds are slow.
- **Neuron** uses `latest-neuron-srpm-url.sh` (and the 2.24 variant); **NVIDIA/EFA** kmods use the kmod `Cargo.toml` `releases-url`, and usually change for all supported kernels in one go.
- Kernel-kit `CHANGELOG.md` gets a line such as "Update kernel from A to B ([#PR])".

Details: `document/kernel-kit/development`, `styleguide/rpm-spec/kmod/kernel-module-packaging`.
