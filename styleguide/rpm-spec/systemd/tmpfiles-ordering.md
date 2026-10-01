---
type: Styleguide Rule
description: "Install tmpfiles.d configs into %{_cross_tmpfilesdir} from the Source200–299 range and name them with lexicographic ordering in mind, since tmpfiles are applied in lexicographic order and downstream overrides depend on it."
language: rpm-spec
category: systemd
---
# tmpfiles.d ordering

Unlike other systemd configuration, tmpfiles.d files are processed in lexicographic order across all directories, so a name decides whether a later package can override an entry.

## Good

```spec
Source200: foo-tmpfiles.conf
…
install -D -p -m 0644 %{S:200} %{buildroot}%{_cross_tmpfilesdir}/foo.conf
```

## Bad

Naming a base config `zz-foo.conf` so nothing downstream can override it, or installing it to `/usr/lib/tmpfiles.d` directly.
