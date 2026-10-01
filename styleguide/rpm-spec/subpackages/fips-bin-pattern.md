---
type: Styleguide Rule
description: "Packages with FIPS-relevant binaries ship mutually exclusive -bin and -fips-bin subpackages that both provide %{name}(binaries), gated by image-feature(no-fips)/image-feature(fips), installing into parallel standard and FIPS directories with self-contained symlink trees."
language: rpm-spec
category: fips
---
# FIPS `-bin` / `-fips-bin` pattern

Reference: `packages/amazon-ssm-agent/amazon-ssm-agent.spec`. Go packages get a FIPS edition only if they use Go crypto; don't exclude hardware components from FIPS images without analysis.

## Good

```spec
%package bin
Summary: Package binaries
Provides: %{name}(binaries)
Requires: (%{_cross_os}image-feature(no-fips) and %{name})
Conflicts: (%{_cross_os}image-feature(fips) or %{name}-fips-bin)
%description bin
%{summary}.

%package fips-bin
Summary: Package binaries, FIPS edition
Provides: %{name}(binaries)
Requires: (%{_cross_os}image-feature(fips) and %{name})
Conflicts: (%{_cross_os}image-feature(no-fips) or %{name}-bin)
%description fips-bin
%{summary}.
```
Standard binaries in `%{_cross_libexecdir}`/`%{_cross_bindir}`; FIPS binaries in `%{_cross_fips_libexecdir}`/`%{_cross_fips_bindir}`.

## Bad

One `-bin` package whose `%install` picks FIPS or non-FIPS binaries with a build-time conditional, or a FIPS symlink pointing into the non-FIPS tree.
