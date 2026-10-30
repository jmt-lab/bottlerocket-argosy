---
type: Guide
description: Spec-driven feature workflow for AI-assisted development — idea honing, concept, EARS requirements, design with Critical Constraints, test plan, TOML implementation plan, and the implement-commit TDD pipeline — with what each phase produces, where the artifacts live, which skill runs it, and what to check when reviewing it.
---

# Feature proposal workflow

Building features with AI agents works best as a conversation that narrows from "what problem are we solving?" to "what exact code changes do we make?". Each phase produces a document that is a contract for the agent implementing the feature and for the human reviewing its work. The core idea: **gaps in specifications become gaps in implementation**. When an agent meets ambiguity it guesses; front-loading the hard conversations (edge cases, error handling, performance) is cheap compared with iterating on code.

## Pipeline

```
idea-honing ─▶ concept ─▶ requirements ─▶ design ─▶ test plan ─▶ implementation plan ─▶ implement-commit
 (optional)     "why"       "what",        "how"     "verify"      "build" (TOML)         TDD pipeline
                            precisely                                                     → git commits
```

| Phase | Skill | Artifact |
|-------|-------|----------|
| Idea honing (optional) | `skill/idea-honing` | `planning/NNNN-<slug>/idea-honing.md` (scratch) |
| Concept | `skill/propose-feature-concept` | `$FEATURE_DIR/concept.md` |
| Requirements | `skill/propose-feature-requirements` | `$FEATURE_DIR/requirements.md` |
| Design | `skill/propose-feature-design` | `$FEATURE_DIR/design.md` |
| Test plan | `skill/propose-feature-test-plan` | `$FEATURE_DIR/test-plan.md` |
| Implementation plan | `skill/propose-implementation-plan` | `$FEATURE_DIR/implementation-plan.toml` |
| Implementation | `skill/implement-commit` | commits on a feature branch of the workspace |

Shortcut: `skill/ad-hoc-implementation-plan` turns an approved rough plan straight into a minimal design, minimal test plan, and full implementation plan, then hands off to `skill/implement-commit`.

Not every change needs every phase. A small bug fix needs none; a new CLI subcommand may need only a concept and requirements; an architectural change benefits from all of them. Choose the entry point and depth deliberately.

Use a fresh agent context for each phase (idea honing and concept may share one), so each document stands on its own rather than leaning on conversation history.

## Where artifacts live

- **`$FEATURE_DIR`** — one directory per feature, `docs/features/NNNN-<slug>/` in the repository being changed (e.g. a sibling checkout of `bottlerocket`, `bottlerocket-core-kit`, or `twoliter`). Four-digit, zero-padded numbers; lowercase-hyphenated slugs (`0001-kernel-lockdown-setting`). Find the next number with `ls -1d docs/features/[0-9][0-9][0-9][0-9]-* | tail -1`.
- If the upstream repo should not carry proposal documents, use a scratch planning directory outside the checkout with the same layout; only the code commits go upstream. Decide this before `implement-commit`, whose commit step stages everything in the workspace.
- **Idea-honing notes and implement-commit state** are scratch: keep them git-ignored or outside the repo.
- Templates are bundled with the skills: `skill/propose-feature-concept/references/concept-template.md`, `skill/propose-feature-requirements/references/requirements-template.md`, `skill/propose-feature-design/references/design-template.md`, `skill/propose-feature-test-plan/references/test-plan-template.md`, `skill/propose-implementation-plan/references/implementation-plan-template.toml`.

Feature status lives in the concept frontmatter:

```yaml
---
feature: 0001-kernel-lockdown-setting
status: proposed        # proposed | in-development | completed | discarded
tracking-issue: bottlerocket-os/bottlerocket#1234   # optional
---
```

## Phases and how to review them

### Concept

Narrative: the problem, the proposed solution, how a user experiences it, the benefits. Minimal technical detail. **Review:** does it explain why anyone would want this? Could a new team member follow the motivation? Is the pain concrete — *why* and *when* users hit it — or will the agent have to guess? Are there unstated assumptions about how users work?

### Requirements

Precise, testable statements in EARS notation (Easy Approach to Requirements Syntax):

> **WHILE** [condition] **WHEN** [event] **THEN** the system **SHALL** [behaviour]

EARS forbids "the system should be fast"; you must write "WHILE processing a batch, WHEN it exceeds 1000 items, THEN the system SHALL complete within 5 seconds". Requirements are functional, non-functional, and error handling, each with a short per-feature ID prefix (`KLD-1`, `KLD-NFR-1`, `KLD-ERR-1`). **Review:** trace every requirement to the concept and every part of the concept to requirements. Hunt for missing ones — empty or malformed input, cancellation, full disk, network failure. The agent only handles cases you specify.

### Design

Architecture, key types and relationships, module structure, and — most important — **Critical Constraints**: "must do it this way" rules, each with the anti-pattern a naive implementation would fall into (e.g. "memory SHALL stay constant regardless of input size; anti-pattern: loading the whole file before processing"). A Solution Mechanics table ties each concept challenge to the component that solves it. **Review:** are constraints specific enough to catch mistakes? Does every non-functional requirement have a constraint, and every error requirement an error-propagation story?

### Test plan

Maps every requirement ID and every Critical Constraint to a named test: unit (mocks allowed), integration (real resources, no mocks; CLIs tested through the binary), not testable, or out of scope (needs external auth/services). **Review:** check the coverage tables for every ID. Challenge "not testable" — a requirement that cannot be tested often cannot be implemented consistently either.

### Implementation plan

A TOML file of commits, each buildable, tested, and reviewable in one sitting (~200–400 lines), organised by **capability, not artifact** — "add config module with loading, validation and tests", not "types" → "impl" → "tests". It records a dependency graph, the files each commit touches, acceptance criteria and anti-patterns from the Critical Constraints, and assigns every test-plan test to exactly one commit; an independent subagent verifies that coverage. **Review:** does each commit tell a coherent story on its own? Are types, implementation, and tests together? Is every constraint assigned to a commit?

### implement-commit

A state-machine driver runs each commit through designer (types and stubs; compile gate) → tester (the commit's named tests; test gate must fail) → implementor (make tests pass and meet acceptance) → style review loop with an arbiter → scope review → format/lint-fix → `git commit`. The orchestrating agent only dispatches subagents and reports results, intervening when the driver escalates.

## Traceability

Requirements trace to the concept, the design to requirements, tests to requirements and constraints, commits to all of them. When something goes wrong, follow the chain backwards: did the implementation miss a constraint, the design miss a requirement, or the requirements miss part of the problem? Fix the earliest document with the gap — iterating on documents is cheaper than iterating on code.
