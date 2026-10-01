---
type: Styleguide Rule
description: "Create symlinks as relative links (ln -rs) shipped in the same package as their target; never link across packages or across the FIPS/non-FIPS boundary, and use versioned directories to avoid library or driver collisions."
language: rpm-spec
category: files
---
# Symlinks

## Good

```spec
ln -rs %{buildroot}%{_cross_libexecdir}/foo/foo %{buildroot}%{_cross_bindir}/foo
```

## Bad

```spec
ln -s /usr/libexec/foo/foo %{buildroot}%{_cross_bindir}/foo
ln -s %{_cross_fips_bindir}/foo %{buildroot}%{_cross_bindir}/foo   # crosses FIPS domains
```
