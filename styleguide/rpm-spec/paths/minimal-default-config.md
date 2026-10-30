---
type: Styleguide Rule
description: "Ship as little default configuration as possible: rely on the application's built-in defaults, point the build at %{_cross_datadir} instead of /etc when a default file is needed, use the factory-defaults pattern only for files that must appear under /etc, and verify the application actually reads the new location."
language: rpm-spec
category: paths
---
# Minimal default configuration

Bottlerocket's `/etc` is a tmpfs populated at boot, and most runtime configuration is rendered from settings templates. Every packaged default file is something to maintain and something that can disagree with the rendered config.

- First check whether the application's built-in defaults are sufficient; if so, ship no config file.
- If a default file is needed, prefer a read-only location under `%{_cross_datadir}`, selected at build time (`SOMETHINGDIR='%{_cross_datadir}'`, a configure flag, or a compiled-in path) rather than moving files after install.
- Only files that must live under `/etc` go to `%{_cross_factorydir}%{_cross_sysconfdir}/…` (`styleguide/rpm-spec/paths/cross-path-macros`).
- Before relocating a file, confirm the application reads it from the new path (environment variables and flags are not always honoured); note the reason for the location in a comment.

## Good

```spec
%build
%cross_configure --sysconfdir=%{_cross_datadir}/foo
```

## Bad

```spec
Source2: foo.conf    # identical to upstream's compiled-in defaults
…
install -D -m 0644 %{S:2} %{buildroot}%{_cross_factorydir}%{_cross_sysconfdir}/foo/foo.conf
```
