---
type: Styleguide Rule
description: "Kernel module specs use standard kernel source locations, determine the kernel version dynamically, install via cross macros into version-specific module and header directories, ship module-loading config, separate open from closed components, and document deviations from upstream."
language: rpm-spec
category: kernel-modules
---
# Kernel module packaging (kernel-kit)

- Build against the standard kernel source/devel locations; derive the kernel version from the installed kernel package rather than hard-coding it.
- Install modules and headers into version-specific directories via cross macros.
- Ship the module-loading configuration (`modules-load.d`, modprobe options) with the module.
- Keep open and closed (proprietary) components in separate subpackages.
- Mind kernel ABI stability; document every adaptation from upstream install instructions.
- Per-kernel `kmod-<kver>-*` siblings are updated together but not identical: diff them before applying a change to all.
