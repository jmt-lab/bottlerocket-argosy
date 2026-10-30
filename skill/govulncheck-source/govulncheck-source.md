---
type: Skill
description: Run govulncheck in source mode against Go packages in bottlerocket-core-kit inside the bottlerocket-sdk container — discover Go packages, pull the kit's SDK and find its default Go, extract each package's version and GO_MAJOR, fetch the exact upstream archive (or use sources/<group> for first-party code), scan, and report a per-package table. Use for release audits, after a Go package bump, or periodic security review.
---

# govulncheck source scan

Background (why source mode, how Go and source are chosen, quirks) is in `document/core-kit/govulncheck`. Scripts are in `references/`; `KIT` below is the path to a local `bottlerocket-core-kit` checkout.

## Prerequisites

`docker info` succeeds; `python3 --version` ≥ 3.11; `wget`, `tar`, `unzip` available.

## Input

- Package name(s) (e.g. `runc`, `containerd-2.1`); if none, scan every Go package.
- Kit checkout path (default `bottlerocket-core-kit`).

## Procedure

0. **Discover** (when no package given):
   `bash references/list-go-packages.sh "$KIT/packages"`
1. **SDK:** `python3 references/pull-sdk.py "$KIT/Twoliter.toml"` → line 1 the SDK image, line 2 the default (lowest) Go major. Capture both.
2. **Metadata** per package:
   `bash references/extract-metadata.sh <sdk-image> <default-go> "$KIT/packages" <pkg>` → `version<TAB>url<TAB>go_major<TAB>gitrev`.
3. **Source:** read `$KIT/packages/<pkg>/Cargo.toml`.
   - `external-files` present → `bash references/get-source.sh "$KIT/packages/<pkg>/Cargo.toml" <pkg>`; it prints the directory containing `go.mod` (extracted under `/tmp/govulncheck-<pkg>`). Do not `git clone` instead.
   - `source-groups = ["<group>"]` → use `$KIT/sources/<group>/`.
4. **Scan:** `mkdir -p govulncheck-results/<pkg> && bash references/run-govulncheck.sh <sdk-image> <go_major> <source-dir> > govulncheck-results/<pkg>/govulncheck.txt; echo $?` — 3 = findings, 0 = clean, anything else = error. Count `Vulnerability #` lines.
5. **Triage findings:** check whether a patch in `packages/<pkg>/` already fixes each one (the scan uses unpatched upstream source).
6. **Clean up** `/tmp/govulncheck-<pkg>` and report:

| Package | Version | Go | Vulns | Status |
|---|---|---|---|---|

Results stay in `govulncheck-results/<pkg>/govulncheck.txt`. Troubleshooting: see the document.
