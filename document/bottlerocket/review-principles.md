---
type: Guide
description: How to review code changes in Bottlerocket repositories — review as interrogation (questions → answers → implications → concerns), Correct → Readable → Maintainable → Performant priority, stating factual consequences instead of severity or approval verdicts, preferring compile-time guarantees, and treating refactors as proposals.
---

# Code review principles

Applies to reviewing changes in any Bottlerocket repository (bottlerocket, the kits, Twoliter, SDK, host containers). The concrete code rules a review checks against are the `styleguide/` rules (`styleguide/rust/*`, `styleguide/rpm-spec/*`, `styleguide/general/*`) and the per-repo `conventions` documents.

## Review is interrogation

- Work from questions to answers (or an explicit "needs author") to implications to surfaced concerns.
- State the factual consequence ("callers cannot match on error variants"), not a judgement. No severity ranks, no approve/reject verdict, no "acceptable / fine / probably ok / minor", no praise. Humans weigh the consequences.
- Priority order: **Correct → Readable → Maintainable → Performant**.

### Judgement boundaries

Binary, factual assessments are allowed: "this describes undesirable behavior", "this violates the stated requirement", "this breaks the documented invariant", "this is inconsistent with X". Graduated or subjective ones are not: "minor", "blocking", "acceptable", "probably fine", "the trade-off is worth it", "recommend approving".

When tempted to write "acceptable", state the trade-off instead:

- Not: "Using `snafu::Whatever` is acceptable for build tooling."
- Instead: "Using `snafu::Whatever` means errors cannot be programmatically distinguished; all error handling is string-based."
- Not: "The edge-case handling is sufficient." Instead: "Empty input returns `None`; callers must handle this case."

## What to look for

- **Implicit requirements**: extract what the change assumes but does not state, and check it holds. At function level, "returns sorted" means callers come to depend on order; at system level, new functionality carries requirements domain experts leave unspoken. Ask: intentional? documented? verified?
- **Where guarantees live**: prefer compile-time guarantees (newtypes, typestate, trait bounds, `NonZero`/non-empty types) over runtime checks, runtime checks over tests, tests over docs. Hierarchy of trust: what the compiler enforces > what tests verify > what documentation promises > what comments claim. Ask:
  - Could this runtime check be a compile-time guarantee?
  - Does this stringly-typed value deserve a newtype (`styleguide/rust/design/domain-types-over-primitives`, `styleguide/rust/design/validated-newtypes`)?
  - Could invalid states be made unrepresentable? Are state transitions enforced by types or only documented?
- **Tests verify what types cannot**: domain logic, edge cases, error paths. Tests of language features or library behavior add nothing (`styleguide/rust/testing/no-useless-tests`).
- **Testability is design feedback**: code that is hard to test is a design smell. Look for IO behind traits, pure functions, and injected dependencies (`styleguide/rust/testing/mock-traits-with-mockall`).
- **Customer surfaces**: CLI flags, settings and config formats, API responses, error messages, migrations and upgrade/downgrade paths. Changes there outlive the code. Ask what promises are being made or changed.
- **Readability = answerability**: can a reader answer "what does this do and why" from the code and its docs, with detail disclosed progressively? Good abstractions orchestrate smaller ones — a short, English-like orchestration function beats hundreds of lines of inline algorithm. Docs describe how abstractions interact; invariants belong in code (types), not comments. Complexity thresholds are in `styleguide/general/complexity-thresholds`.

## Refactoring suggestions

Surface refactoring opportunities as proposals with their cost, not as assumed improvements. Abstractions that are not load-bearing can be refactored freely for correctness and readability; load-bearing ones (customers depend on them) need a migration path and deprecation, not a rewrite.

## Applying the principles

The principles generate questions. Some are always relevant (requirements, invariants, coherence of the change); others apply only when the code touches their domain. Record questions and answers explicitly — they are the audit trail that lets others follow the reasoning.
