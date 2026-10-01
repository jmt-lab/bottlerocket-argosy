---
type: Styleguide Rule
description: "Spec builds are reproducible: create archives with --sort=name --owner=0 --group=0 --numeric-owner, honour source_date_epoch, and never embed timestamps or hostnames."
language: rpm-spec
category: build
---
# Reproducible builds

## Good

```spec
tar --sort=name --owner=0 --group=0 --numeric-owner --mtime="@${SOURCE_DATE_EPOCH}" -cf bundle.tar dir/
```

## Bad

```spec
echo "built on $(hostname) at $(date)" > %{buildroot}%{_cross_datadir}/foo/BUILDINFO
```
