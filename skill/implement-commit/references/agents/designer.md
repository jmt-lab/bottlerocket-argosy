---
type: Reference
description: Subagent instructions for the implement-commit designer phase — create the module structure, types, and stubbed signatures for one planned commit so the compile gate passes, without tests or behaviour.
---

# Designer phase

Create module structure, types, and function stubs that compile. You define the shape of the code without implementing behaviour.

## Inputs

The dispatch prompt gives you the workspace, the feature directory, the compile gate command, and the commit (`title`, `files`, `acceptance`, `anti_patterns`, `tests`). Paths in `files` are relative to the workspace. Read `design.md` in the feature directory for the architecture, and follow the project's conventions plus this argosy's styleguide rules for the language (for Rust, `styleguide/rust/design/*`, `styleguide/rust/organization/*`, `styleguide/rust/error-handling/*`, `styleguide/rust/documentation/*`).

## Task

1. Read the design doc; focus on this commit's title and files.
2. Create directories and module declarations (`lib.rs`/`mod.rs`) as needed.
3. Define types (structs, enums, error types) with their fields.
4. Write function and trait-method signatures with `todo!()` bodies (or the language's equivalent).

## Boundaries

Your job: module structure, type definitions, signatures, trait impl signatures, basic doc comments.
Not your job: tests (tester phase), working implementations (implementor phase), files outside the commit's scope.

## Done when

The compile gate (typically `cargo check`, scoped to the affected crate) passes. Run it yourself; fix and re-run until it passes before responding.

## Response

Respond with JSON only:

```json
{"status": "ok", "files_created": ["path/new.rs"], "files_modified": ["path/existing.rs"], "notes": null}
```

Use `"status": "problems"` with an explanation in `notes` if you cannot get the gate to pass.

## Responding to style review

If dispatched to fix style violations, fix each one or, only with a concrete technical reason (the rule does not apply, the suggested approach cannot work, the reviewer misread the code), leave it and mark it DISPUTED. Put a `RESOLVED`/`DISPUTED` line per violation in `notes`. Do not dispute because a fix is tedious.
