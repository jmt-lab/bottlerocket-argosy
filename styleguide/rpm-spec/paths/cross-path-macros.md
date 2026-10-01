---
type: Styleguide Rule
description: "Install only through %{_cross_*} path macros and never into /etc or /var: factory defaults go to %{_cross_factorydir}%{_cross_sysconfdir}, runtime directories come from tmpfiles.d, and build-time configuration points tools at /usr/share instead of moving files."
language: rpm-spec
category: paths
---
# `%{_cross_*}` paths, nothing in `/etc` or `/var`

`/etc` is a tmpfs and `/var` is runtime state, so packaged files there are lost or wrong.

- Use `%{_cross_bindir}` (over `_cross_sbindir`), `%{_cross_libdir}`, `%{_cross_libexecdir}`, `%{_cross_datadir}`, `%{_cross_unitdir}`, `%{_cross_tmpfilesdir}`, `%{_cross_templatedir}`, `%{_cross_fips_bindir}`, `%{_cross_fips_libexecdir}`.
- Factory defaults for `/etc`: `%{_cross_factorydir}%{_cross_sysconfdir}/…`; runtime directories: a tmpfiles.d entry.
- Prefer configuring the build to use `%{_cross_datadir}` (`SOMETHINGDIR='%{_cross_datadir}'`) over relocating files after install.
- pkg-config files go under `/usr/lib/pkgconfig`, not `/usr/share/pkgconfig`.

## Good

```spec
install -D -m 0644 %{S:1} %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/foo/foo.conf
```

## Bad

```spec
install -D -m 0644 %{S:1} %{buildroot}/etc/foo/foo.conf
mkdir -p %{buildroot}/var/lib/foo
```
