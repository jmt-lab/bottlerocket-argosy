---
type: Styleguide Rule
description: "Package names are %{_cross_os}<name>; shared libraries are prefixed lib; subpackages use only the -devel, -bin, -fips-bin and -extras suffixes (no -utils, -misc, -common); use full words over abbreviations."
language: rpm-spec
category: metadata
---
# Package naming

## Good

```spec
Name: %{_cross_os}libjson-c
%package devel
%package fips-bin
```

## Bad

```spec
Name: json-c
%package utils
%package common
```
