---
type: Styleguide Rule
description: "Explicitly disable optional features, docs, man pages, translations and static libraries at configure time rather than %exclude-ing them afterwards; do not override compiler flags or disable debug packages without justification; enable SELinux support and verify upstream GPG signatures when available."
language: rpm-spec
category: build
---
# Minimal, explicit build configuration

- Turn optional features off explicitly so new upstream defaults don't silently enable them.
- Disable docs/man/translations at build time; `%exclude` is a last resort.
- `--disable-static`, and remove static libraries unless there is a stated reason.
- Keep the SDK's compiler flags; don't override `CFLAGS` wholesale.
- Don't disable debuginfo packages without justification.
- Enable SELinux support when the project offers it.
- Verify GPG signatures when upstream signs artifacts (`%{gpgverify}`, `rpmkeys --checksig`).

## Good

```spec
%cross_configure --disable-static --disable-nls --without-docs --with-selinux
```

## Bad

```spec
%cross_configure
…
%files
%exclude %{_cross_mandir}
%exclude %{_cross_libdir}/*.a
```
