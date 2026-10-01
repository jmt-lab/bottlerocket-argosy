---
type: Styleguide Rule
description: "Declare BuildRequires/Requires with the %{_cross_os} prefix, alphabetised and grouped; express alternatives through %{_cross_os}<pkg>(capability) virtual provides and image-feature() conditions rather than version conditionals, never require a capability the package itself provides, and declare Conflicts between mutually exclusive packages."
language: rpm-spec
category: subpackages
---
# Requires, provides and capabilities

- `%{_cross_os}` prefix on every dependency; alphabetise and group by type.
- Self-references use `%{name}`.
- Virtual capabilities: `%{_cross_os}<pkg>(capability)`, e.g. `hostname-imds(binaries)`. Do not require a capability the same package provides; do not add compatibility `Provides` for packages that never existed.
- Conditional requirements via `%{_cross_os}image-feature(fips)` / `image-feature(no-fips)`; prefer capabilities over version-specific conditionals.
- `Conflicts:` between mutually exclusive packages.
- Kubernetes components are version-suffixed packages that can coexist; package credential providers and plugins (CNI to standard locations) along their real technical relationships.

## Good

```spec
BuildRequires: %{_cross_os}glibc-devel
BuildRequires: %{_cross_os}libcrypto-devel
Requires: %{name}(binaries)
```

## Bad

```spec
BuildRequires: libcrypto-devel
BuildRequires: %{_cross_os}glibc-devel
Requires: %{_cross_os}foo-bin
Provides: %{name}(binaries)   # in the same package that requires it
```
