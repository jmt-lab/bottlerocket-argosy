---
type: Skill
description: Turn an approved feature concept into requirements.md — precise, testable EARS-notation (WHILE/WHEN/WHERE/THEN/SHALL) functional, non-functional, and error-handling requirements with a per-feature ID prefix and appendices; use after propose-feature-concept and before propose-feature-design.
---

# Propose feature requirements

Translate the concept into testable requirements. Pipeline and review guidance: `document/bottlerocket/feature-proposal-workflow`. Template: `references/requirements-template.md`.

## Prerequisites

`$FEATURE_DIR/concept.md` exists and the user has approved it. If not, run `skill/propose-feature-concept` first.

## Procedure

1. **Read** `$FEATURE_DIR/concept.md` and, if present, `planning/NNNN-<slug>/idea-honing.md` (it often surfaces edge cases and constraints).

2. **Create** `$FEATURE_DIR/requirements.md` from `references/requirements-template.md`.

3. **Choose an ID prefix** of 2–5 characters (e.g. `KLD` for kernel-lockdown) and use it for every ID: `KLD-1`, `KLD-NFR-1`, `KLD-ERR-1`.

4. **Overview** — a short paragraph on what the spec covers, referencing the concept.

5. **Functional requirements** in EARS form:

   ```
   **WHILE** [state or condition]
   **WHEN** [trigger or event]
   **THEN** the system **SHALL** [required behavior]
   ```

   Inline examples only if 1–3 lines; larger ones go to appendices.

6. **Non-functional requirements** (performance, usability, security, compatibility). For each major operation ask: what happens with 1000x more items? Should memory stay constant or scale with input? What latency is acceptable and does it degrade? If an operation must be O(1) memory or bounded time, state it — these become Critical Constraints in the design.

7. **Error handling** — this is where gaps hide. Cover empty and malformed input, cancellation mid-operation, missing or unreadable files, full disks, network failures, and (for Bottlerocket) invalid settings values and upgrade/downgrade (migration) paths where relevant:

   ```
   **WHILE** [operation in progress]
   **WHERE** [error condition occurs]
   **THEN** the system **SHALL** [error handling behavior]
   ```

8. **Appendices** for schemas, config formats (e.g. TOML settings), data structures, and protocols, labelled `## Appendix A: ...`.

9. **Review for completeness** with the user: every requirement uses EARS keywords, is specific and testable, has a unique prefixed ID, and traces to the concept; every part of the concept has requirements.

## Validate

```bash
grep -cE '^### [A-Z]+-' "$FEATURE_DIR/requirements.md"
grep -E 'WHILE|WHEN|WHERE|THEN|SHALL' "$FEATURE_DIR/requirements.md" | head
```

## Common mistakes

- Missing EARS keywords; vague, untestable statements ("should be fast").
- Inline examples longer than 3 lines.
- Inconsistent prefixes.
- Happy path only — no error requirements.

## Next

Once approved, run `skill/propose-feature-design` in a fresh context.
