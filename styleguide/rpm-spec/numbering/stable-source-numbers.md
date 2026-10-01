---
type: Styleguide Rule
description: "Never renumber existing Source entries when removing one (leave the gap), and install files in %install in the same order as their Source declarations."
language: rpm-spec
category: numbering
---
# Stable source numbers and install order

Renumbering creates noisy diffs and breaks `%{S:n}` references elsewhere in the spec. Leave gaps when a source is removed; small renumbering within the same hundreds block is tolerated. Install sources in `%install` in declaration order so reviewers can check one against the other.

## Good

```spec
Source100: foo.service
# Source101 removed
Source102: foo-cleanup.service
```

## Bad

```spec
Source100: foo.service
Source101: foo-cleanup.service   # was Source102
```
