---
type: Styleguide Rule
description: "In %files, mark owned directories with %dir and list them first, group entries by function, exclude info, locale, man and doc directories, and keep explanatory comments out of %files."
language: rpm-spec
category: files
---
# `%files` section

- `%dir` for every directory the package owns, listed before its contents.
- Group entries by function (binaries, units, config, data).
- Exclude `%{_cross_infodir}`, `%{_cross_localedir}`, `%{_cross_mandir}`, `%{_cross_datadir}/doc/*`, `%{_cross_datadir}/locale/*` (better: don't build them, `styleguide/rpm-spec/build/minimal-build-configuration`).
- Put explanations in `%build`/`%install`, not `%files`.

## Good

```spec
%files
%license LICENSE
%{_cross_attribution_file}
%dir %{_cross_datadir}/foo
%{_cross_datadir}/foo/defaults.toml
%{_cross_bindir}/foo
%{_cross_unitdir}/foo.service
```

## Bad

```spec
%files
%{_cross_bindir}/foo
# this is the data dir, needed by foo
%{_cross_datadir}/foo/*
%{_cross_mandir}/*
```
