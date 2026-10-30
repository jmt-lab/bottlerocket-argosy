---
type: Styleguide Rule
description: "When moving files, binaries or capabilities between packages, update every dependent package's Requires, symlinks and %files in the same change so no image is left with a broken reference or a file owned by two packages."
language: rpm-spec
category: maintenance
---
# Moving components between packages

A file that moves from one package to another changes which package other specs must require and which package owns the path. Doing half the move leaves images with dangling symlinks, missing binaries, or file conflicts at image build time.

- Search the kit for every `Requires:`, symlink and `%files` entry that refers to the moved path or package and update them together.
- Keep backward compatibility (for example a `Provides:` for a capability consumers already require) unless the break is intentional and called out in the commit message.
- Build every variant that pulls in the affected packages, not just the package you edited.

## Good

One commit that moves `foo-helper` from `foo` into `foo-bin`, adds `Requires: %{name}(binaries)` to `foo`, and updates the `bar` package that symlinked to it.

## Bad

Moving `%{_cross_bindir}/foo-helper` to a new subpackage while `bar.spec` still has `Requires: %{_cross_os}foo` and expects the binary to be present.
