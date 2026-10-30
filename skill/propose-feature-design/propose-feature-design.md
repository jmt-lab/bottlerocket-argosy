---
type: Skill
description: Write a feature's technical design.md from its concept and requirements — Critical Constraints with anti-patterns, architecture, solution mechanics, domain model, module structure, and design decisions — guiding implementors without writing the implementation; use after propose-feature-requirements and before propose-feature-test-plan.
---

# Propose feature design

Bridge requirements and code. Pipeline and review guidance: `document/bottlerocket/feature-proposal-workflow`. Template: `references/design-template.md`.

## Prerequisites

`$FEATURE_DIR/concept.md` and `$FEATURE_DIR/requirements.md` exist and are approved.

## Procedure

1. **Read** the concept, requirements, any idea-honing notes (`planning/NNNN-<slug>/idea-honing.md`), and the code the feature touches. Search this argosy for the affected repo's architecture and conventions (e.g. `document/bottlerocket/architecture`, `document/core-kit/architecture`, `document/twoliter/architecture`).

2. **Create** `$FEATURE_DIR/design.md` from `references/design-template.md`.

3. **Overview** — a high-level description of the approach, referencing the concept and requirement IDs.

4. **Critical Constraints** (the most important section). For each key operation ask: what would a wrong implementation look like? What performance characteristics are required? What invariants must hold? Record each as:

   | ID | Constraint | Rationale | Anti-pattern to avoid |
   |----|------------|-----------|-----------------------|
   | CC-1 | Memory SHALL stay constant regardless of input size | Inputs can be multi-GB images | Reading the whole file into memory before processing |

   Be specific; vague constraints catch nothing. Every non-functional requirement should map to at least one constraint.

5. **Architecture** — components, data flow, layer responsibilities, integration points; simple ASCII diagrams help.

6. **Solution Mechanics** — for each core challenge in the concept, name the architectural element that addresses it and why it works (and what would fail otherwise), as a table. A reviewer should be able to answer "how does this solve X?" by pointing at a component.

7. **Domain model** — core types (purpose, key properties, validation, relationships) and operations (conceptual signatures, behaviours, invariants, error types). For Rust, align with this argosy's styleguide (e.g. `styleguide/rust/design/domain-types-over-primitives`, `styleguide/rust/error-handling/error-per-operation`, `styleguide/rust/error-handling/snafu-for-errors`).

8. **Module structure** — directory layout and responsibilities. Respect `styleguide/general/complexity-thresholds` (about 550 lines per non-test file): if a component may exceed it, plan the split up front by capability (e.g. `builder.rs`, `searcher.rs`), not by artifact type. Keep all `impl` blocks for a type in one file; if it grows too large, delegate to helper functions or internal component types instead of scattering `impl` blocks across files.

9. **Migration from current design** (skip for greenfield) — current state, changed types/data/processes, affected modules. For Bottlerocket settings or data-store changes, call out whether a migration is needed.

10. **Design patterns and decisions** — patterns that apply and why; for each significant choice, a `DD-N` entry with the decision, alternatives, rationale, and implications.

11. **Implementation guidance and testing strategy** — reference CC IDs, performance considerations, edge cases, unit vs integration split.

12. **Keep code minimal** — illustrative snippets only; guide implementors, do not implement.

## Review

Check with the user: are the constraints specific enough to catch mistakes? Does every NFR and error requirement have a corresponding constraint or error-propagation story? Does each major component have a reason to exist tied to a problem?

## Common mistakes

- Large code blocks; or the opposite, no concrete type names or modules.
- Structure without Solution Mechanics (why it solves the problem).
- Design decisions not linked to requirement IDs.

## Next

Run `skill/propose-feature-test-plan`, then `skill/propose-implementation-plan`, each in a fresh context.
