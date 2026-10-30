---
type: Skill
description: Clarify a rough feature idea through one-question-at-a-time Q&A with the user, recording each answer in idea-honing.md so it can seed the concept document; use before propose-feature-concept when the idea's scope, use cases, edge cases, or trade-offs are still fuzzy.
---

# Idea honing

Refine a feature idea through structured questioning before writing the concept. Pipeline and artifact layout: `document/bottlerocket/feature-proposal-workflow`.

## When to use

- The user has a rough idea that is not fully formed.
- Before `skill/propose-feature-concept` (which offers this skill as step 0).
- To explore the design space and trade-offs.

## Procedure

1. **Pick the feature directory.** Agree `NNNN-<slug>` with the user and where artifacts live (`$FEATURE_DIR`, default `docs/features/NNNN-<slug>/` in the repo being changed; find the next number with `ls -1d docs/features/[0-9][0-9][0-9][0-9]-* 2>/dev/null | tail -1`). Idea-honing notes are scratch material: keep them in a planning directory that is not committed (default `planning/NNNN-<slug>/`, git-ignored or outside the repo).

2. **Initialise the notes file** `planning/NNNN-<slug>/idea-honing.md`:

   ```markdown
   # Idea Honing: Feature Name

   ## Initial Idea

   [The user's rough description]

   ## Questions & Answers
   ```

3. **Draft a private question list** covering use cases and workflows, scope and boundaries, integration points (for Bottlerocket: which repo — `bottlerocket`, a kit, `twoliter`, the SDK — settings/API surface, migrations, variants affected), edge cases, constraints and trade-offs, and success criteria.

4. **Ask ONE question at a time.** For each: ask clearly, wait for the answer, discuss until it is settled, then append it before moving on:

   ```markdown
   ### Q: [Question]

   **A**: [Answer]
   ```

   Never batch questions, and write each answer immediately rather than at the end.

5. **Let the list evolve.** Add questions as new ambiguity appears; drop ones that became irrelevant. If a question is about how existing code behaves, note it as "needs research" and move on — answer it later by reading the code or searching this argosy rather than guessing.

6. **Conclude when clear.** Summarise the key insights at the end of the file, confirm with the user that they are ready to write the concept, and leave the file in place.

## Common mistakes

- Asking several questions at once.
- Recording answers in batches instead of after each one.
- Stopping before the user is confident about scope and approach.

## Next

Run `skill/propose-feature-concept` in the same context, using the Q&A as material for the narrative.
