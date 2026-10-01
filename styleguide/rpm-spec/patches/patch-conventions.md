---
type: Styleguide Rule
description: "Apply patches with -p1, document each patch's purpose and upstream issue, keep traceability to upstream commits (git cherry-pick -x), and keep invasive patches to a minimum."
language: rpm-spec
category: patches
---
# Patch conventions

- Use `-p1`, not `-p0001`.
- Each patch documents why it exists and links the upstream issue or commit; backports keep the `(cherry picked from commit …)` trailer (`git cherry-pick -x`).
- Prefer small, upstreamable patches; carry invasive ones only with a stated reason and exit plan.

## Good

```spec
# Backport of upstream fix for CVE-XXXX-YYYY; drop on next release.
Patch1001: 1001-fix-buffer-overflow-in-parser.patch
```
