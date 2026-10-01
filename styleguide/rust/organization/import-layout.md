---
type: Styleguide Rule
description: "Put all imports at the top of the module with no blank lines between them (pub use separated by one blank line), group items within one module path but not across modules, use crate-local types unqualified, and qualify ambiguous third-party types."
language: rust
category: imports
---
# Import layout

- All `use` statements at the top, no blank lines between them; `pub use` re-exports follow after one blank line.
- Group within a module path (`use serde::{Deserialize, Serialize};`), but not across modules (`use std::{path::Path, io::Error};` is wrong).
- Import crate-local types and use them unqualified.
- Qualify third-party types whose names are ambiguous: `serde_json::Value`, `sqlx::Error`.
- The only function-level imports are snafu context selectors (`styleguide/rust/error-handling/context-selector-imports`).

## Good

```rust
use crate::manifest::Manifest;
use serde::{Deserialize, Serialize};
use std::io::Read;
use std::path::Path;

pub use crate::lock::Lock;
```

## Bad

```rust
use std::{io::Read, path::Path};

use serde::Deserialize;
use serde::Serialize;
use serde_json::*;
```
