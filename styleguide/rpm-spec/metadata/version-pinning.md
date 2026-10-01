---
type: Styleguide Rule
description: "Express upstream versions with major-version variables, pin git sources to commit hashes, make Version/Release match the real upstream artifact (no pre-release tags for stable), and avoid busywork version bumps."
language: rpm-spec
category: metadata
---
# Version pinning

- Use major-version variables where upstream has release lines (`%global gover …`, `GO_MAJOR="1.25"`).
- Pin git sources to a commit hash, not a branch.
- The version must match the artifact actually fetched; never label a beta/alpha as a stable release.
- Don't bump versions or releases without a functional reason.

## Good

```spec
%global gitrev 3f1c2e9d8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d
Source0: https://github.com/example/foo/archive/%{gitrev}/foo-%{gitrev}.tar.gz
```

## Bad

```spec
Source0: https://github.com/example/foo/archive/refs/heads/main.tar.gz
```
