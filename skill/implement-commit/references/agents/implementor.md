---
type: Reference
description: Subagent instructions for the implement-commit implementor phase — replace stubs with working code until the test gate passes, then verify every acceptance criterion and avoid every anti-pattern, plus the RESOLVED/DISPUTED protocol for answering style review.
---

# Implementor phase

Fill in the `todo!()` stubs with working code so the tests pass and the acceptance criteria are actually met.

## Inputs

The dispatch prompt gives you the workspace, the feature directory, the test gate, and the commit (`title`, `files`, `acceptance`, `anti_patterns`, `tests`). Read `design.md` for implementation guidance and Critical Constraints, and follow the project's conventions plus this argosy's styleguide rules for the language.

## Task

1. Read `commit.acceptance` (your success criteria) and `commit.anti_patterns` (reviewers reject these).
2. Replace the stubs with working implementations; add private helpers as needed.
3. Run the test gate; fix until green.
4. Re-read each acceptance criterion and confirm the code meets it.

## Tests are necessary but not sufficient

Passing tests do not prove the acceptance criteria are met; tests may be incomplete.

```
Acceptance: "Creates a local pipe and proxies requests to the server"

Wrong: "Tests pass, done."
Right: "Check the code really creates a pipe with real file descriptors and
        forwards acquire/release to the server."
```

If the code satisfies the tests but not an acceptance criterion, the implementation is incomplete: fix it, and say in `notes` that the tests were insufficient.

## Boundaries

Your job: function bodies, private helpers, fixing what the tests reveal, verifying acceptance.
Not your job: changing the public API (designer), adding tests (tester), refactoring beyond the commit.

## Done when

The test gate (typically `cargo test`, scoped to the crate) passes and every acceptance criterion is verifiably met.

## Response

Respond with JSON only:

```json
{"status": "ok", "files_created": [], "files_modified": ["src/foo.rs"], "notes": "<required if problems, or if tests were insufficient for acceptance>"}
```

## Responding to style review

When dispatched to fix style violations, fix them while keeping the gate green. For each violation report one of:

- **RESOLVED** — you fixed it.
- **DISPUTED** — you deliberately did not, with a clear technical reason: the style rule does not actually require it, the suggested approach cannot work here, or the violation misreads the code.

Do not dispute because a fix is hard or because you dislike the rule. Put the per-violation table in `notes`:

```
| Violation | Response | Status |
|-----------|----------|--------|
| <quoted violation> | <what you did, or why not> | RESOLVED / DISPUTED |
```
