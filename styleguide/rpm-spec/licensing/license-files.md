---
type: Styleguide Rule
description: "Install every license file with %license, listed explicitly (no wildcards, no leading ./), mode 0644 into %{_cross_licensedir}, with license sources in the Source400–499 range."
language: rpm-spec
category: licensing
---
# License files

## Good

```spec
Source400: LICENSE-THIRD-PARTY
…
%files
%license LICENSE NOTICE
%{_cross_attribution_file}
```

## Bad

```spec
%files
%license ./COPYING.*
```
