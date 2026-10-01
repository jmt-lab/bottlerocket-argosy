---
type: Styleguide Rule
description: "The License field uses current SPDX identifiers and expressions (AND when both apply, OR for a choice) without redundant terms, verified with askalono, and includes bundled third-party licenses."
language: rpm-spec
category: licensing
---
# SPDX `License:` field

- Current SPDX ids: `LGPL-2.1-only`, not `LGPL-2.1`; `GPL-2.0-or-later`, not `GPLv2+`.
- `AND` means both apply; `OR` means a choice. Do not write redundant expressions.
- Verify with `askalono` before accepting a suggested license; document non-obvious reasoning in a comment.
- Account for vendored/third-party code (check `THIRD-PARTY-LICENSES.txt` and vendor directories).

## Good

```spec
License: Apache-2.0 AND MIT
```

## Bad

```spec
License: MIT OR (MIT AND GPLv2)
License: LGPL-2.1
```
