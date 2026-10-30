---
type: Reference
description: Template for a feature test-plan.md — tables mapping every requirement ID and Critical Constraint to a named unit, integration, not-testable, or out-of-scope test, plus a test inventory.
---

# Test plan template

Create `$FEATURE_DIR/test-plan.md` with the content below.

````markdown
---
feature: NNNN-feature-name
---

# Test Plan: Feature Name

## Overview

Brief description of the testing approach.

## Test Types

- **Unit**: internal logic in isolation; mocks allowed.
- **Integration**: real resources (filesystem, network, processes); NO mocks. CLI programs are tested through the actual CLI.
- **Not testable**: cannot be verified automatically (explain why).
- **Out of scope**: needs external authentication or services; documented, not implemented.

## Requirements Coverage

| Req ID | Test Type | Test Name | Description |
|--------|-----------|-----------|-------------|
| PREFIX-1 | unit | test_example | What it verifies |
| PREFIX-2 | integration | test_cli_example | What it verifies |
| PREFIX-3 | not-testable | - | Why not testable |

## Critical Constraints Verification

| CC ID | Verification Approach | Test Name(s) |
|-------|----------------------|--------------|
| CC-1 | How the constraint is verified | test_name or "Code review" |

## Test Inventory

### module_name

- `test_function_name` - what it tests

## Notes

Additional context, manual verification steps for out-of-scope tests.
````
