---
type: Skill
description: Produce a machine-parseable implementation-plan.toml that splits a designed feature into atomic, capability-sized commits with a dependency graph, acceptance criteria and anti-patterns from the Critical Constraints, and every test-plan test assigned to exactly one commit, then have an independent subagent verify coverage; use after propose-feature-test-plan and before implement-commit.
---

# Propose implementation plan

Create the TOML plan that drives `skill/implement-commit`. The driver reads it mechanically, so it must parse and be complete. Pipeline and review guidance: `document/bottlerocket/feature-proposal-workflow`. Template: `references/implementation-plan-template.toml` (optional prose companion: `references/implementation-plan-template.md`).

## Prerequisites

`$FEATURE_DIR/design.md` and `$FEATURE_DIR/test-plan.md` exist and are approved.

## Output

`$FEATURE_DIR/implementation-plan.toml`:

```toml
[meta]
feature = "feature-name"
feature_dir = "docs/features/NNNN-feature-name"
workspace = "."              # repo checkout the commits land in, relative to where implement-commit runs

[dependencies]
1 = []
2 = []
3 = [1, 2]

[[commits]]
id = 1
title = "Short description"
message = "feat(scope): commit message"   # follow the target repo's commit conventions
files = ["path/to/file.rs"]               # relative to workspace
acceptance = ["Criterion (CC-N, verified by test_name)"]
anti_patterns = ["What NOT to do"]
tests = ["test_name_from_test_plan"]      # REQUIRED
```

## Procedure

1. **Study design.md** — module structure, affected files, component dependencies, the Critical Constraints table.

2. **Study test-plan.md** — list every test name. Each must land in exactly one commit; tests are the source of truth for acceptance.

3. **Find capability boundaries, not artifact boundaries.** Good commits: a new module with its types, implementation, and tests together; one user-visible capability (a CLI command, a new setting); one requirement satisfied end to end. Never split "add types" → "add impl" → "add tests" — it fragments the story and breaks test-first work within a commit. If a commit is too large, split by capability (e.g. "config loading" vs "config validation"). See `styleguide/general/commits/atomic-by-capability`.

4. **Build the dependency graph** in `[dependencies]` (commit id → ids that must land first). Independent commits can be implemented in parallel.

5. **Assign tests** to commits via `tests = [...]`, giving an auditable trace test-plan.md → plan → code.

6. **Carry the Critical Constraints** into the commits that implement them: `acceptance` lists the criteria that must hold (cite CC-N and test names); `anti_patterns` lists what reviewers must reject. These become explicit review checkpoints.

7. **Write commit messages** in the target repo's convention (see `styleguide/general/commits/header-format` and `styleguide/general/commits/scope-and-subject`, and the repo's own conventions document in this argosy).

8. **Validate the TOML:**

   ```bash
   python3 -c "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))" "$FEATURE_DIR/implementation-plan.toml"
   ```

9. **Verify independently.** Dispatch a fresh, read-only subagent with the instructions in `references/verifier.md`, pointing it at `$FEATURE_DIR/test-plan.md` and `$FEATURE_DIR/implementation-plan.toml`. It returns:

   ```json
   {"valid": bool, "total_tests_in_plan": int, "tests_assigned": int,
    "gaps": [str], "duplicates": [str], "warnings": [str]}
   ```

   If `valid` is false, fix the gaps and duplicates and re-verify. Address warnings about acceptance criteria that cite no test.

## Commit sizing

Target roughly 200–400 changed lines per commit.

- **Too small:** types without implementation; a trait without at least one impl; implementation without tests.
- **Too large:** several unrelated capabilities; more than ~500 lines; more than 5–6 files.
- **Right:** a module with types, impl, and tests; a CLI command with handler and tests; a complete adapter with tests.

## Review

Ask: does each commit tell a coherent story a reviewer can understand without the commits around it? Are types, implementation, and tests together? Is each Critical Constraint assigned to a commit?

## Next

Review sizing and feasibility with the user, then run `skill/implement-commit`.
