---
type: Guide
description: Procedure for editing Bottlerocket RPM spec files in core-kit and kernel-kit — where the styleguide/rpm-spec rules live, which reference package to copy, how to commit, and the pre-submit validation checklist.
---

# Editing RPM spec files

Applies to every `.spec` under `packages/` in the kit repos (core-kit and kernel-kit). The packaging rules themselves are styleguide concepts under `styleguide/rpm-spec/` (`language: rpm-spec`), grouped by category: structure, numbering, patches, metadata, licensing, build, dependencies, paths, files, subpackages, fips, kernel-modules, systemd, formatting. Repo-level layout facts (Cargo.toml per package, `external-files`, patch series `0001-`/`9001-`) are in `document/core-kit/conventions`. `%{_cross_*}` macros are defined by the SDK.

## Procedure

1. Look up the rules that apply to the change (search the styleguide with `language: rpm-spec`).
2. Pick a similar reference package and follow its shape: Go `packages/nvidia-k8s-device-plugin/nvidia-k8s-device-plugin.spec`; C + systemd `packages/chrony/chrony.spec`; FIPS `-bin`/`-fips-bin` `packages/amazon-ssm-agent/amazon-ssm-agent.spec`; first-party Rust `packages/netdog/netdog.spec`.
3. Edit in section order (`styleguide/rpm-spec/structure/section-order`).
4. Review the result against the checklist below, ideally by a second reviewer who did not write the change.
5. Commit with the message in a file (`git commit -s -F <msgfile>`, not `-m` with escaped `\n`). Header `package-name: summary` (`styleguide/general/commits/header-format`), then a body and `Signed-off-by`.

## Validation checklist

- [ ] Sections in order; sources in the correct number ranges; `%install` order matches `Source` declarations
- [ ] All paths via `%{_cross_*}`; nothing installed into `/etc` or `/var`
- [ ] `%{_cross_attribution_file}` (and `%{_cross_attribution_vendor_dir}` for Go/Rust) in main `%files`; SBOM generation not disabled
- [ ] `%license` for every license file; `%dir` for owned directories
- [ ] `Release: 1%{?dist}`; SPDX `License:` verified
- [ ] No scripting-language or OpenSSL dependencies
- [ ] No debugging commands, redundant comments or trailing whitespace
- [ ] Builds on both x86_64 and aarch64; rpmlint-equivalent checks clean or deviations documented
