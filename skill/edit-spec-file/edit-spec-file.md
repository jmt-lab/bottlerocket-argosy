---
type: Skill
description: Edit a Bottlerocket RPM spec file in bottlerocket-core-kit or bottlerocket-kernel-kit (add sources, patches, systemd units, templates, subpackages or FIPS variants; change %build/%install/%files) so it follows the styleguide/rpm-spec rules, then validate it with an independent review and commit it. Use for any change to a packages/<name>/<name>.spec file.
---

# Edit a spec file

Background and the full validation checklist: `document/core-kit/packaging-style-guide`. The rules themselves are the `styleguide/rpm-spec/**` concepts; repo layout and patch-series conventions are in `document/core-kit/conventions` and `document/kernel-kit/conventions`.

## 1. Load the rules

Search this argosy for styleguide rules with `language: rpm-spec` that touch the change (for example "systemd unit", "license", "fips", "tmpfiles"). Always read:

- `styleguide/rpm-spec/structure/section-order`
- `styleguide/rpm-spec/numbering/source-ranges` and `styleguide/rpm-spec/numbering/stable-source-numbers`
- `styleguide/rpm-spec/paths/cross-path-macros`
- `styleguide/rpm-spec/licensing/attribution-and-sbom`

## 2. Pick a reference package

Open the closest existing spec in the same kit and follow its shape:

| Kind | Reference |
|---|---|
| Go | `packages/nvidia-k8s-device-plugin/nvidia-k8s-device-plugin.spec` |
| C + systemd | `packages/chrony/chrony.spec` |
| `-bin` / `-fips-bin` | `packages/amazon-ssm-agent/amazon-ssm-agent.spec` |
| First-party Rust | `packages/netdog/netdog.spec` |

## 3. Make the change

Edit section by section in the fixed order. Common recipes:

- **systemd unit**: `Source1xx: foo.service` → `install -D -p -m 0644 %{S:1xx} %{buildroot}%{_cross_unitdir}/foo.service` → list it in `%files` (`styleguide/rpm-spec/systemd/units-and-dropins`).
- **drop-in directory**: `install -d %{buildroot}%{_cross_unitdir}/foo.service.d` → `%dir %{_cross_unitdir}/foo.service.d`.
- **template**: `Source<100: foo-conf` → `install -D -p -m 0644 %{S:n} %{buildroot}%{_cross_templatedir}/foo-conf` → `%{_cross_templatedir}/foo-conf`.
- **tmpfiles.d**: `Source2xx` into `%{_cross_tmpfilesdir}` (`styleguide/rpm-spec/systemd/tmpfiles-ordering`).
- **FIPS binaries**: `-bin`/`-fips-bin` pair (`styleguide/rpm-spec/subpackages/fips-bin-pattern`).
- **files moving between packages**: `styleguide/rpm-spec/maintenance/moving-components`.

Install sources in `%install` in the order they are declared. When removing a source, leave the number gap.

## 4. Build

Build the package for both `x86_64` and `aarch64` with the kit's build targets (see `document/core-kit/development`). Fix failures at the root rather than with `%exclude`.

## 5. Independent review

Dispatch a subagent that did not write the change. Give it the diff, `document/core-kit/packaging-style-guide` (validation checklist) and the rules from step 1, and ask it to report every checklist item that fails, with line references. Fix the findings and repeat until it reports none.

## 6. Commit

Header `package-name: summary` (`styleguide/general/commits/header-format`). Write the message to a file and commit with `git commit -s -F <file>` (`styleguide/general/commits/message-body`).
