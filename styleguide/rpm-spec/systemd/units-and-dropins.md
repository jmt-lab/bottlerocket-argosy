---
type: Styleguide Rule
description: "Install systemd units into %{_cross_unitdir} from the Source100–199 range, customise upstream units with drop-in directories rather than replacing them, and keep unit naming and activation consistent with sibling packages."
language: rpm-spec
category: systemd
---
# systemd units and drop-ins

## Good

```spec
Source100: foo.service
Source101: foo-override.conf
…
install -D -p -m 0644 %{S:100} %{buildroot}%{_cross_unitdir}/foo.service
install -d %{buildroot}%{_cross_unitdir}/containerd.service.d
install -p -m 0644 %{S:101} %{buildroot}%{_cross_unitdir}/containerd.service.d/10-foo.conf
…
%dir %{_cross_unitdir}/containerd.service.d
```

## Bad

Copying and editing upstream's `containerd.service` wholesale to change one setting.
