---
type: Styleguide Rule
description: "Number Source entries by range: 0–99 main tarball and miscellaneous files, 100–199 systemd units, 200–299 tmpfiles.d configs, 300–399 udev rules, 400–499 license files; patches start at 1000 in related groups."
language: rpm-spec
category: numbering
---
# Source and patch number ranges

| Range | Content |
|---|---|
| `Source0–99` | main tarball and miscellaneous files |
| `Source100–199` | systemd units |
| `Source200–299` | tmpfiles.d configs |
| `Source300–399` | udev rules |
| `Source400–499` | license files |
| `Patch1000+` | patches, related ones grouped in ranges |

The patch *file* names follow the repo's series conventions (`0001-…` upstream/backport, `9001-…` Bottlerocket-specific in core-kit; `1001-…`/`2001-…` in kernel-kit; see `document/core-kit/conventions`, `document/kernel-kit/conventions`).

## Good

```spec
Source0: https://example.org/foo-%{version}.tar.gz
Source100: foo.service
Source200: foo-tmpfiles.conf
```

## Bad

```spec
Source0: https://example.org/foo-%{version}.tar.gz
Source1: foo.service
Source2: foo-tmpfiles.conf
```
