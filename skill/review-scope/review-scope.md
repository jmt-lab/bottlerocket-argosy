---
type: Skill
description: Pass/fail gate that checks a change does exactly what its requirements say — no more, no less — against stated requirements, constraints, and the allowed file set, returning ACCEPT or a list of located violations plus optional refactoring flags. Use in a TDD verification step or when a PR or commit needs a scope-compliance check.
---

# Review scope

Verify that code changes do exactly what they are supposed to do — no more, no less. This is a pass/fail gate, not a feedback session.

## Inputs

**Files:**
- Implementation plan or requirements document.
- Design document, if available.
- The changed files.

**Data:**
- `commit_details`: what this change is supposed to do.
- `requirements`: the requirement IDs (e.g. `REQ-*`) being addressed.
- `constraints`: constraint IDs (e.g. `CC-*`) that must be satisfied.
- `allowed_files`: files that may be modified (the scope boundary).

## Procedure

1. **Establish scope boundaries** from the inputs: what MUST be done (requirements), what MUST NOT be done (constraints), which files MAY change, what behavior is expected.
2. **Review each changed file:**
   1. Is the file in the allowed set?
   2. Do the changes address the stated requirements?
   3. Are there changes unrelated to the requirements?
   4. Do the changes violate any constraint?
3. **Report.**

If all checks pass:

```
ACCEPT
```

Otherwise list each violation with its location and a plain explanation, and optionally a theme across violations:

```
VIOLATIONS:
- src/parser.rs:45 - Added logging infrastructure not in commit scope
- src/config.rs - Modified file outside allowed set

THEMES: Multiple changes extend beyond the stated requirements into error-handling refactoring
```

## Minimal-change bias check

Implementing agents tend to make the smallest change that achieves the goal. After identifying violations, ask: do they point to a refactoring that would make the code more maintainable? Did the implementer avoid a better structural solution in favor of a quick fix? If so, add:

```
REFACTORING: <structural improvement the implementer avoided>
```

This is a flag for the orchestrator, not a violation. Frame it as a proposal (`document/bottlerocket/review-principles`).

## Out of scope

- Improvements unrelated to violations or general constructive feedback.
- Code style — use `skill/review-style`.

The result is binary: ACCEPT or VIOLATIONS. Refactoring notes are optional flags, not blockers.
