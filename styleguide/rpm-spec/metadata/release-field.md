---
type: Styleguide Rule
description: "The Release field is exactly `1%{?dist}` for a new version: never `1.%{?dist}`, and always %{?dist} rather than %{dist}; add an Epoch only when needed."
language: rpm-spec
category: metadata
---
# Release field

## Good

```spec
Release: 1%{?dist}
```

## Bad

```spec
Release: 1.%{?dist}
Release: 1%{dist}
```
