---
type: Skill
description: Create a narrative concept.md for a new feature — the problem, the proposed solution, how a user experiences it, and its benefits — in a numbered feature directory; use as the first step of the spec-driven feature workflow, before requirements, design, test plan, and implementation plan.
---

# Propose feature concept

Write the concept document that pitches a feature and explains why it matters. Pipeline, artifact layout, and review guidance: `document/bottlerocket/feature-proposal-workflow`. Template: `references/concept-template.md`.

## Procedure

0. **Offer idea honing.** Ask: "Would you like to work through the idea one question at a time first, to clarify scope and edge cases?" If yes, run `skill/idea-honing`, then return here.

1. **Choose the feature directory.** Agree with the user where artifacts live (`$FEATURE_DIR`, default `docs/features/NNNN-<slug>/` in the repo being changed, or a scratch planning directory if proposal docs should not be committed). Find the next number:

   ```bash
   ls -1d docs/features/[0-9][0-9][0-9][0-9]-* 2>/dev/null | tail -1
   ```

   Start at `0001` if none exist. The slug is lowercase-hyphenated, 2–4 words (e.g. `kernel-lockdown-setting`, `kit-local-registry`).

2. **Check for idea-honing notes** at `planning/NNNN-<slug>/idea-honing.md`; if present, mine them for the narrative.

3. **Create** `$FEATURE_DIR/concept.md` from `references/concept-template.md` with `feature: NNNN-<slug>`, `status: proposed`, and an optional `tracking-issue:` (e.g. `bottlerocket-os/bottlerocket#1234`).

4. **Fill it in with the user, as prose:**
   - **Problem** — the current situation, the concrete pain, when users hit it, why it matters. Make the pain specific; vague pain gets filled with guesses later.
   - **Solution** — what users will experience; "what" and "why", not "how".
   - **How It Works** — a story of someone using the feature end to end.
   - **Benefits** — the value, tied back to the problem.
   - **Technical Notes** — brief constraints or hints only; detail belongs in design.md.

5. **Review for narrative flow.** It should read like a story, prefer prose over bullet lists, focus on user experience and value, and explain why before what. Ask: could a new team member understand the motivation? Are there unstated assumptions about how users work?

## Validate

```bash
cat "$FEATURE_DIR/concept.md"
```

## Common mistakes

- Too technical (reads like a design doc) — refocus on problem and user experience.
- Too abstract — add concrete examples of the pain.
- List-heavy — rewrite as prose.

## Next

Once the user approves the concept, run `skill/propose-feature-requirements`, ideally in a fresh agent context.
