---
type: Styleguide Rule
description: "When a design lint fires (complexity, too many arguments, type complexity, nesting, too many lines, file length), fix the underlying design instead of making the smallest edit that silences it."
language: general
category: refactoring
---
# Fix design lints structurally

Lints like clippy's `cognitive_complexity`, `too_many_arguments`, `type_complexity`, `excessive_nesting`, `too_many_lines`, `large_enum_variant`, `result_large_err`, `option_option`, `struct_excessive_bools`, `fn_params_excessive_bools`, or a file-length limit point at a design problem. Ask what a loosely coupled design would look like:

- A function doing too much → compose smaller, named abstractions.
- Complex types or many parameters → introduce newtypes, domain types, or a parameter struct.
- Excessive cloning → rethink ownership.
- A large struct/file → decompose it into private component modules behind an unchanged facade; or split by operation, keeping each operation's tests next to it; collapse parameterised tests with `test_case`; move fixtures into module-local helpers.

## Good

Extracting a `RetryPolicy` type that owns the four retry-related parameters.

## Bad

Adding `#[allow(clippy::too_many_arguments)]`, scattering one struct's `impl` blocks across files without decomposing it, or deleting comments and Given/When/Then markers to get under a line limit.
