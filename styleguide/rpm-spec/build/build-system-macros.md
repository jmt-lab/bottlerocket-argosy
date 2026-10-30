---
type: Styleguide Rule
description: "Use the SDK's cross build macros: %cross_configure for autotools, %{cross_cmake} with CMAKE_INSTALL_PREFIX and a separate cmake --build, and %cross_go_setup/%cross_go_configure/%set_cross_go_flags with vendored modules for Go (gofips build for FIPS binaries)."
language: rpm-spec
category: build
---
# Cross build macros

| Build system | Use |
|---|---|
| Autotools | `%cross_configure` |
| CMake | `%{cross_cmake} -DCMAKE_INSTALL_PREFIX:PATH=%{_cross_prefix}` then a separate `cmake --build` |
| Go | `%global goproject/gorepo/goimport/gover/rpmver`, `%cross_go_setup`, `%cross_go_configure`, `%set_cross_go_flags`, vendored modules (`-mod=vendor` where not already implied); FIPS binaries with `gofips build` |
| Rust | vendored crates (`cargo vendor`) so the build is offline and reproducible; attribution as in `styleguide/rpm-spec/licensing/attribution-and-sbom` |

Go specifics:

- Define the upstream version and the git revision as separate `%global`s, and pass version information through linker flags (`-ldflags "${GOLDFLAGS} -X …"`) rather than patching sources.
- Remove `%global` macros the spec no longer uses.
- Keep build flags consistent with sibling Go packages; don't hand-set `GOOS`/`GOARCH`/`CC`.

Reference packages: Go `nvidia-k8s-device-plugin.spec`; C + systemd `packages/chrony/chrony.spec`.

## Good

```spec
%build
%set_cross_go_flags
go build -ldflags "${GOLDFLAGS}" -o foo ./cmd/foo
```

## Bad

```spec
%build
GOOS=linux GOARCH=arm64 CC=aarch64-linux-gnu-gcc go build -o foo ./cmd/foo
```
