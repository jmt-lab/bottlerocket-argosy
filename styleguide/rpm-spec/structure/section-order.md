---
type: Styleguide Rule
description: "Bottlerocket spec files keep sections in a fixed order: %global, metadata (Name, Version, Release, Summary, License, URL), Sources, Patches, BuildRequires/Requires, %description, subpackages, %prep, %build, %install, %files."
language: rpm-spec
category: structure
---
# Spec section order

1. `%global` definitions
2. Metadata: `Name`, `Version`, `Release`, `Summary`, `License`, `URL`
3. `Source*`
4. `Patch*`
5. `BuildRequires` / `Requires`
6. `%description`
7. Subpackages (`%package` + `%description` each)
8. `%prep`
9. `%build`
10. `%install`
11. `%files` (main, then subpackages)

Keep build logic out of `%prep`; it only unpacks and patches.
