---
type: Styleguide Rule
description: "Every package lists %{_cross_attribution_file} in its main %files and keeps SBOM generation enabled (first-party specs override %global cross_generate_sbom to run sbomtool over their sources); Go and Rust packages also run %cross_scan_attribution (with --clarify when a clarify.toml exists) and list %{_cross_attribution_vendor_dir}."
language: rpm-spec
category: licensing
---
# Attribution and SBOM

- Main `%files` always contains `%{_cross_attribution_file}`.
- Go/Rust packages scan vendored dependencies with `%cross_scan_attribution` (pass `--clarify <clarify.toml source>` when one exists) and list `%{_cross_attribution_vendor_dir}`.
- SBOMs are produced by the SDK's `cross_generate_sbom` macro. Don't disable it; first-party specs redefine it at the top (`%global cross_generate_sbom %{shrink: … sbomtool generate --name <pkg> … }`), as in `packages/netdog/netdog.spec`.

## Good

```spec
%install
…
%cross_scan_attribution --clarify %{S:1000} go-vendor vendor

%files
%license LICENSE
%{_cross_attribution_file}
%{_cross_attribution_vendor_dir}
```

## Bad

A Go package whose `%files` lists only the binary, with no attribution file or vendor attribution directory.
