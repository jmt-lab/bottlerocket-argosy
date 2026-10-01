---
type: Styleguide Rule
description: "Install executables 0755 and config files, units and templates 0644, using install -p to preserve mtimes and install -D to create parent directories; label sensitive data secret_t via SELinux."
language: rpm-spec
category: files
---
# Install modes

## Good

```spec
install -d %{buildroot}%{_cross_bindir}
install -p -m 0755 foo %{buildroot}%{_cross_bindir}
install -D -p -m 0644 %{S:100} %{buildroot}%{_cross_unitdir}/foo.service
```

## Bad

```spec
cp foo %{buildroot}%{_cross_bindir}/
chmod 777 %{buildroot}%{_cross_bindir}/foo
```
