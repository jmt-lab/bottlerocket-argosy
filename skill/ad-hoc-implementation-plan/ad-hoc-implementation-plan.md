---
type: Skill
description: Fast path from a user-approved rough plan to implement-commit-ready artifacts — a minimal design.md (overview, Critical Constraints, module structure), a minimal test-plan.md (coverage tables), and a full implementation-plan.toml — produced by subagents and cross-checked by an independent verifier; use when the change is well understood and the full concept/requirements chain would be overkill but you still want TDD verification.
---

# Ad-hoc implementation plan

Trade documentation completeness for speed while keeping `skill/implement-commit`'s rigour. Full pipeline for comparison: `document/bottlerocket/feature-proposal-workflow`.

## When to use

- The user has approved a rough plan (in conversation, a Markdown note, or an issue).
- The change is understood well enough to skip concept/requirements and extensive design iteration.
- You want the TDD pipeline and review gates of `skill/implement-commit`.

## Your role

You are a mechanical router: gather inputs, create the feature directory, dispatch one fresh subagent per phase with the relevant skill as its instructions, pass artifacts between phases, and check cross-references. Do not design the feature yourself.

## Phase 0: gather

Ask the user for, or infer from the rough plan and confirm:

1. Feature slug and number → `$FEATURE_DIR` (default `docs/features/NNNN-<slug>/` in the repo being changed, or a scratch directory if docs should not be committed; next number via `ls -1d docs/features/[0-9][0-9][0-9][0-9]-* 2>/dev/null | tail -1`).
2. Workspace (the repo checkout commits land in).
3. Files to create or modify.
4. Key constraints (become the Critical Constraints table).
5. Test names (become the test plan and each commit's `tests`).
6. A short summary of the rough plan.

Create `$FEATURE_DIR`.

## Phase 1: minimal design

Dispatch a subagent with `skill/propose-feature-design` as its instructions, plus the gathered constraints, files, and plan summary, and this directive: "Create a MINIMAL `$FEATURE_DIR/design.md`: only Overview (one paragraph), Critical Constraints table, and Module Structure. Skip architecture diagrams, solution mechanics, patterns, and design decisions." Point it at the relevant styleguide rules in this argosy for the language. It reports `{"success": bool, "artifact_path": str, "errors": [str]}`.

## Phase 2: minimal test plan

Dispatch a fresh subagent with `skill/propose-feature-test-plan`, the design from phase 1, and the gathered test names: "Create a MINIMAL `$FEATURE_DIR/test-plan.md`: only the Requirements Coverage table (one row per planned behaviour; use descriptive IDs since there is no requirements.md) and the Critical Constraints Verification table." Same report shape.

## Phase 3: implementation plan

Dispatch a fresh subagent with `skill/propose-implementation-plan`, design.md, test-plan.md, the workspace, files, and plan summary: "Create `$FEATURE_DIR/implementation-plan.toml`. All fields are required — no minimal mode. `tests` must exactly match the test-plan test names." Same report shape.

## Phase 4: verify cross-references

Dispatch a fresh, read-only subagent with design.md, test-plan.md, and implementation-plan.toml, asking it to check:

- every test in test-plan.md appears exactly once across `commits[].tests`;
- every `CC-N` in design.md has verification in test-plan.md;
- every `commits[].files` path exists or is clearly created by that commit;
- the TOML parses (`python3 -c "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))" <plan>`).

It reports `{"valid": bool, "missing_tests": [str], "orphan_tests": [str], "missing_constraints": [str]}`. If invalid, return to phase 3 with the findings (or phase 2 for missing constraints) and re-verify.

## Handoff

```
$FEATURE_DIR/
├── design.md                 # minimal: overview + CC table + module structure
├── test-plan.md              # minimal: coverage tables
└── implementation-plan.toml  # full
```

Tell the user the artifacts are ready and that `skill/implement-commit` will execute them.
