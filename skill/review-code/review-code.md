---
type: Skill
description: Deep, multi-agent review of a GitHub PR in a Bottlerocket repository — derives questions from the review principles, answers every one (fact-find, deep-research, design, correctness, or needs-author), reviews each commit, filters implications, and writes a local REVIEW.md of ready-to-post comments grouped by category without severity or approval verdicts. Use when asked to review a PR thoroughly.
---

# Review code

Review a PR by generating and answering **all** questions derived from `document/bottlerocket/review-principles`, then surfacing what is unclear or concerning as ready-to-post comments with references to the reasoning artifacts.

Produces: questions, an answer for every question (or explicit "needs author"), implications, and surfaced concerns grouped by category (correctness, assumption, type-system, intent). Does **not** produce severity rankings, blocking/non-blocking labels, or approval recommendations.

Question types and handlers:

| Type | Meaning | Handler |
|------|---------|---------|
| FACT | concrete, citable answer | `skill/fact-find` |
| RESEARCH | needs deep understanding of a system | `skill/deep-research` |
| DESIGN | evaluates a choice | propose alternatives, compare factually |
| CORRECTNESS | verifies behavior | trace the code |
| INTENT | only the author knows | mark needs-author |

## Input

- PR reference (URL, number, or branch).
- Optional: user-identified issues or linked documentation.

## Setup

Prerequisites: working directory is the repository containing the PR, no uncommitted changes (fail early if dirty), GitHub CLI authenticated.

```bash
gh pr checkout <PR-number>
```

Capture `base_ref` from the PR metadata. From here on, all subagents read code from the local checkout (`git diff {base_ref}...HEAD`, `git show <sha>`), not via `gh`.

## Workspace

Create `planning/<pr-slug>/` for artifacts. Do not commit them.

```
planning/<pr-slug>/
├── 00-scout.md                 # initial territory map
├── 01-questions.md             # refined, classified question backlog
├── 02-answers.md               # consolidated Q&A
├── answers/                    # fact-Q1.md, design-Q2.md, ...
├── 03-commit-NN.md             # per-commit reviews
├── 04-holistic-pre.md
├── filtered-implications.md
├── 05-holistic-post.md
└── REVIEW.md                   # final output
```

## Subagent protocol

You orchestrate; subagents analyze. For every phase, dispatch a subagent (using whatever subagent mechanism your harness provides) and give it:

- **Files:** `document/bottlerocket/review-principles`, the phase's prompt file under `references/agents/`, and the prior-phase artifacts listed below.
- **Data:** `workspace`, `repo_path`, `base_ref`, plus phase-specific data.

Each subagent replies:

```
OUTPUT: <filename>
STATUS: ok | problems
NOTES: <if problems>
```

Trust `STATUS: ok`. On `problems`, read the notes and decide. If your harness cannot dispatch subagents, run each phase yourself in order, using the artifacts as memory between phases.

## Phases

| # | Phase | Prompt | Extra inputs | Output |
|---|-------|--------|--------------|--------|
| 1 | Scout | `references/agents/01-scout.md` | `pr_number`, user context | `00-scout.md` |
| 2 | Refine questions | `references/agents/02-refine-questions.md` | `00-scout.md`, linked issues/docs | `01-questions.md` |
| 3 | Answer questions | `references/agents/03`–`06` (by type) | one question each | `answers/<type>-<id>.md` |
| 4 | Holistic pre | `references/agents/07-holistic-pre.md` | `01-questions.md`, `02-answers.md`, PR description, commit messages | `04-holistic-pre.md` |
| 5 | Per-commit review | `references/agents/08-commit-review.md` | `01-questions.md`, `02-answers.md`, `commit_sha`, `commit_message`, `commit_number`, `total_commits`, `all_commit_messages` | `03-commit-NN.md` |
| 5.5 | Filter implications | `references/agents/085-filter-implications.md` | all `03-commit-*.md` | `filtered-implications.md` |
| 6 | Holistic post | `references/agents/09-holistic-post.md` | `01`, `02`, `04-holistic-pre.md`, all `03-commit-*.md`, `filtered-implications.md` | `05-holistic-post.md` |
| 7 | Synthesize | `references/agents/10-synthesize.md` | all artifacts | `REVIEW.md` |

### Phase 3 details

Dispatch one subagent per question, in parallel where possible:

| Type | Prompt | Output |
|------|--------|--------|
| FACT | `references/agents/03-answer-fact.md` | `answers/fact-{id}.md` |
| RESEARCH | `references/agents/04-answer-research.md` | `answers/research-{id}.md` |
| DESIGN | `references/agents/05-answer-design.md` | `answers/design-{id}.md` |
| CORRECTNESS | `references/agents/06-answer-correctness.md` | `answers/correctness-{id}.md` |
| INTENT | none — record as needs-author | |

Then consolidate into `02-answers.md`:

```markdown
# Answered Questions

| ID | Type | Question | Answer Summary | Detail |
|----|------|----------|----------------|--------|
| Q1 | FACT | ... | ... | [answers/fact-Q1.md] |

## Needs Author
| ID | Question | Why We Can't Answer |
```

### Phases 4 and 5

Phase 4 may run in parallel with phase 5. In phase 5, dispatch **one subagent per commit** (do not batch commits); they run in parallel. Commit reviewers check style against this argosy's `styleguide/**` rules and cite rule paths.

### Phase 5.5

Binary surface/skip decision on every implication and author question from the commit reviews, then categorization: **correctness** (logic errors, wrong behavior), **assumption** (unstated assumptions), **type-system** (runtime checks or stringly-typed values that could be compile-time), **intent** (needs author clarification).

## Deliver

Present `REVIEW.md` to the user. This skill is **local only**: do not post comments or otherwise interact with GitHub beyond the initial `gh pr checkout`. The user acts on the output.

## Context preservation

Do not read intermediate artifacts except when a subagent reports `problems`, the user asks a question, or you are debugging a failure. Always read status responses and the final `REVIEW.md`.
