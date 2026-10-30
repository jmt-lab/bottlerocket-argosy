---
type: Reference
description: Template for a feature concept.md — narrative Problem, Solution, How It Works, Benefits, and brief Technical Notes sections, plus the feature/status frontmatter the concept file must start with.
---

# Concept template

Create `$FEATURE_DIR/concept.md` with the content below (everything inside the fence), replacing the guidance text. Keep it narrative prose, not lists.

````markdown
---
feature: NNNN-feature-name
status: proposed
# tracking-issue: bottlerocket-os/bottlerocket#1234   (optional)
---

# Feature Name

## Problem

Describe the problem this feature solves. Paint a picture of the current situation and the pain it causes. What's missing today? Why does this matter?

## Solution

Describe the proposed solution as a narrative. Walk through what users will experience and how it addresses the problem. Focus on the "what" and "why" rather than the "how."

## How It Works

Explain the feature from a user's perspective as a story. Describe the workflow naturally, showing how someone would actually use this feature in practice.

## Benefits

Explain the value this feature provides. How does it improve the user's experience? What becomes possible that wasn't before? Connect benefits back to the problem statement.

## Technical Notes

Brief technical considerations, constraints, or implementation hints. Keep this section short — detailed design goes in design.md.
````

Status values: `proposed` (under review), `in-development` (approved, being implemented), `completed` (merged), `discarded` (not pursued).
