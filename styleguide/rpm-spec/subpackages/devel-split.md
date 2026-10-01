---
type: Styleguide Rule
description: "Put headers and the unversioned .so symlink in a -devel subpackage that Requires %{name}; keep versioned .so.* libraries in the main package."
language: rpm-spec
category: subpackages
---
# `-devel` split

## Good

```spec
%package devel
Summary: Files for development using libfoo
Requires: %{name}
%description devel
%{summary}.

%files
%{_cross_libdir}/libfoo.so.*

%files devel
%{_cross_libdir}/libfoo.so
%{_cross_includedir}/foo/
```

## Bad

```spec
%files
%{_cross_libdir}/libfoo.so*
%{_cross_includedir}/foo/
```
