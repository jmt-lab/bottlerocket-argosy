---
type: Styleguide Rule
description: "Spec comments add packaging context (why a patch, flag or workaround exists and when it can go), never restate the command, and never speculate about vendor roadmaps; keep related specs consistent with each other."
language: rpm-spec
category: formatting
---
# Packaging comments

## Good

```spec
# Patch needed until upstream fixes issue #1234.
# Custom flags because upstream defaults break cross-compilation.
```

## Bad

```spec
# Install the binary
install -p -m 0755 foo %{buildroot}%{_cross_bindir}
# Vendor will probably add arm64 support next year.
```
