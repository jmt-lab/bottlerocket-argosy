---
type: Skill
description: Create a feature's test-plan.md mapping every EARS requirement ID and every design Critical Constraint to a named unit, integration, not-testable, or out-of-scope test; use after propose-feature-design and before propose-implementation-plan, whose commits must cover every named test.
---

# Propose feature test plan

Map requirements and constraints to concrete tests so every requirement has verification. Pipeline and review guidance: `document/bottlerocket/feature-proposal-workflow`. Template: `references/test-plan-template.md`.

## Prerequisites

`$FEATURE_DIR/` contains approved `concept.md`, `requirements.md`, and `design.md` (with its Critical Constraints table).

## Procedure

1. **Extract IDs.** List every requirement ID (`PREFIX-N`, `PREFIX-NFR-N`, `PREFIX-ERR-N`) from requirements.md and every `CC-N` from design.md.

2. **Create** `$FEATURE_DIR/test-plan.md` from `references/test-plan-template.md`.

3. **Map each requirement** to a test type and a descriptive, unique test name (e.g. `test_parses_valid_config`):
   - **Unit** — internal logic, algorithms, transformations; mocks allowed; no filesystem or network.
   - **Integration** — file I/O, network, processes, CLI commands; no mocks.
   - **Not testable** — needs human judgment or infeasible setup; explain why. Challenge these: a requirement that cannot be tested is often too vague to implement consistently — consider tightening it.
   - **Out of scope** — needs external authentication or services (cloud APIs, authenticated registries, launching instances); document what would be tested and any manual verification, but do not plan automated tests.

4. **Map each Critical Constraint** to how it is verified — named tests, or "code review" when it cannot be automated.

5. **CLI features** — integration tests run the real binary, capture stdout/stderr, and exercise real user workflows end to end; do not test internal APIs instead.

6. **Bottlerocket images** — behaviour that can only be observed on a booted host (systemd units, settings applied through the API, kernel features) is integration testing on a launched instance; mark it out of scope for the automated plan unless the repo has a harness for it, and list the manual check.

## Validate

Every ID must appear in the plan:

```bash
for id in $(grep -oE '^### [A-Z]+(-[A-Z]+)?-[0-9]+' "$FEATURE_DIR/requirements.md" | awk '{print $2}') \
          $(grep -oE '\bCC-[0-9]+' "$FEATURE_DIR/design.md" | sort -u); do
  grep -q -- "$id" "$FEATURE_DIR/test-plan.md" || echo "missing: $id"
done
```

Test names must be unique (`grep -oE 'test_[a-z0-9_]+' "$FEATURE_DIR/test-plan.md" | sort | uniq -d` prints nothing, unless a test deliberately covers several IDs).

## Common mistakes

- Missing coverage for some requirement or constraint.
- Wrong test type (unit tests touching disk; integration tests with mocks).
- Testing internals instead of user-visible behaviour.
- Vague descriptions of what a test verifies.

## Next

Run `skill/propose-implementation-plan` in a fresh context; every test named here must be assigned to exactly one commit.
