---
type: Guide
description: How to review code changes in Bottlerocket repositories — review as interrogation (questions → answers → implications → concerns), Correct → Readable → Maintainable → Performant priority, stating factual consequences instead of severity or approval verdicts, preferring compile-time guarantees, and treating refactors as proposals.
---

# Code review principles

Applies to reviewing changes in any Bottlerocket repository (bottlerocket, the kits, Twoliter, SDK, host containers). The concrete code rules a review checks against are the `styleguide/` rules (`styleguide/rust/*`, `styleguide/general/*`) and the per-repo `conventions` documents.

## Review is interrogation

- Work from questions to answers (or an explicit "needs author") to implications to surfaced concerns.
- State the factual consequence ("callers cannot match on error variants"), not a judgement. No severity ranks, no approve/reject verdict, no "acceptable / fine / probably ok / minor", no praise. Humans weigh the consequences.
- Priority order: **Correct → Readable → Maintainable → Performant**.

## What to look for

- **Implicit requirements**: extract what the change assumes but does not state, and check it holds.
- **Where guarantees live**: prefer compile-time guarantees (newtypes, typestate, trait bounds, `NonZero`/non-empty types) over runtime checks, runtime checks over tests, tests over docs. Code that is hard to test is a design smell.
- **Customer surfaces**: CLI flags, settings and config formats, API responses, error messages, migrations and upgrade/downgrade paths. Changes there outlive the code.
- **Readability = answerability**: can a reader answer "what does this do and why" from the code and its docs, with detail disclosed progressively? Complexity thresholds are in `styleguide/general/complexity-thresholds`.

## Refactoring suggestions

Surface refactoring opportunities as proposals with their cost, not as assumed improvements. Load-bearing abstractions need a migration path, not a rewrite.
