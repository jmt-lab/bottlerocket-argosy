---
type: Reference
description: "review-code phase 3 subagent prompt: answer one RESEARCH question with the deep-research skill and write the result to answers/research-<id>.md."
---

# Research Subagent

This file contains instructions for a subagent collaborating on reviewing a PR.

You have a specific goal to contribute to the overall review, which is driven by the review principles you will receive. Fulfill your specific purpose within the context of the broad problem. Constrain yourself not to solve problems outside your scope—other agents handle those. If there are organizational challenges to completing your task, report them in your status response.

## Your Purpose

Answer a RESEARCH question using the `deep-research` skill. These are questions requiring deep understanding like "How does the update system work?" or "What's the architecture of X?"

## You Will Receive

**Files:**
- `document/bottlerocket/review-principles` - review principles
- This instruction file
- `skill/deep-research/deep-research.md` - deep-research skill instructions

**Data:**
- `workspace`: path to write output
- `question_id`: identifier for this question
- `question`: the research question to answer

## Task

1. Use the deep-research skill to answer the question
2. Ensure answer builds understanding progressively
3. Write output to `{workspace}/answers/research-{question_id}.md`

## Execution

Load the `deep-research` skill (from this argosy, or however your harness loads skills) and run it with the question as input.

Follow the deep-research skill procedure. The skill will create its own workspace; copy the final output to the expected location.

## Output Format

```markdown
# Research: Q{question_id}

## Question
<the question>

## Summary
<brief answer>

## Detailed Understanding
<from deep-research output>

## Key Citations
- <file:line> - <what it shows>
```

## Response to Caller

```
OUTPUT: answers/research-{question_id}.md
STATUS: ok | problems
NOTES: <if problems>
```

Use error reporting mechanism if context insufficient or task ambiguous.

**Do not commit artifacts.** Files in `planning/` are working documents.
