---
type: Skill
description: Pass/fail gate that checks changed files against this argosy's styleguide rules (styleguide/rust, styleguide/rpm-spec, styleguide/general), selecting rules by TDD phase (designer, tester, implementor), honoring a review ledger across cycles, and returning accept or file:line violations that cite rule paths. Use in a TDD verification step or for a style-compliance check of a PR.
---

# Review style

Verify that code follows the project style rules. This is a pass/fail gate, not a feedback session.

## Inputs

**Files:**
- The changed files.
- A ledger file (optional) for multi-cycle reviews.

**Data:**
- `phase`: `designer`, `tester`, or `implementor` — selects which rules apply.
- `changed_files`: list of files to review.

## Authoritative rules

The styleguide rules in this argosy are the only source of truth. Search or list `styleguide/**` and read each applicable rule (its description, rationale, Good and Bad examples); do not rely on summaries. Also honor the target repository's `conventions` document (e.g. `document/core-kit/conventions`) and `styleguide/general/match-existing-conventions`.

| Phase | Rules |
|-------|-------|
| `designer` | `styleguide/rust/design/*`, `styleguide/rust/error-handling/*`, `styleguide/rust/documentation/*`, `styleguide/rust/organization/*` |
| `tester` | `styleguide/rust/testing/*` |
| `implementor` | `styleguide/rust/error-handling/*`, `styleguide/rust/organization/*`, `styleguide/rust/control-flow/*`, `styleguide/rust/logging/*`, `styleguide/rust/safety/*` |
| any | `styleguide/general/*`; `styleguide/rpm-spec/*` for `.spec` files; `styleguide/rust/dependencies/*` for `Cargo.toml`; `styleguide/general/commits/*` for commit messages |

Test code (`#[cfg(test)]` modules, `tests/`) always gets the `styleguide/rust/testing/*` rules regardless of phase.

Commonly hit rules, for orientation (the rule files are authoritative):

- designer: `styleguide/rust/design/bon-builders`, `styleguide/rust/design/validated-newtypes`, `styleguide/rust/error-handling/snafu-for-errors`. In the designer phase, function bodies are `todo!()`, not implementations.
- implementor: `styleguide/rust/error-handling/no-unwrap-in-production`, `styleguide/rust/error-handling/context-selector-imports`, `styleguide/rust/organization/import-layout`.
- tester: `styleguide/rust/testing/given-when-then`, `styleguide/rust/testing/test-case-parameterisation`.

## Ledger awareness

When a ledger is provided:

1. Read previous cycles: which violations were raised and how the implementer responded.
2. Verify RESOLVED items were actually fixed.
3. Do not re-raise DISPUTED items when the implementer's reason is valid.
4. Raise only NEW violations.

## Procedure

1. Select the applicable rules for the phase and file types.
2. Check each changed file against them. Flag only clear violations of a stated rule, not preferences.
3. Return the result.

## Result

```python
class StyleResult(BaseModel):
    status: Literal["accept", "violations"]
    violations: list[str] = []  # each: "file:line - description (rule path)"
    themes: str | None = None   # optional pattern across violations
```

Example:

```python
StyleResult(
    status="violations",
    violations=[
        "src/config.rs:23 - snafu selectors imported at module level (styleguide/rust/error-handling/context-selector-imports)",
        "src/parser.rs:45 - test lacks Given/When/Then comments (styleguide/rust/testing/given-when-then)",
    ],
    themes="Several violations stem from an inconsistent error-handling approach",
)
```

## Out of scope

- Improvements unrelated to violations or general constructive feedback.
- Scope or correctness — use `skill/review-scope` or `skill/review-code`.
- Style preferences that no rule states.

The result is binary: accept or violations.
