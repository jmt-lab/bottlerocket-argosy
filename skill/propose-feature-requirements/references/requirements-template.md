---
type: Reference
description: Template for a feature requirements.md — EARS-notation functional, non-functional, and error-handling requirements with a short per-feature ID prefix, and appendices for schemas and larger examples.
---

# Requirements template

Create `$FEATURE_DIR/requirements.md` with the content below, replacing `PREFIX` with the feature's 2–5 character prefix.

````markdown
# Feature Name - Requirements Specification

## Overview

Brief description of what this specification covers. Reference concept.md.

## Functional Requirements

### PREFIX-1: Requirement Name

**WHILE** [state or condition]  
**WHEN** [trigger or event]  
**THEN** the system **SHALL** [required behavior]

**WHERE** [optional condition]  
**THEN** the system **SHALL** [alternative behavior]

Example (only if truly small):
```
key = "value"
```

### PREFIX-2: Another Requirement

**WHILE** [state or condition]  
**WHEN** [trigger or event]  
**THEN** the system **SHALL** [required behavior]

## Non-Functional Requirements

### PREFIX-NFR-1: Performance

**WHILE** [operating condition]  
**THEN** the system **SHALL** [performance requirement]

### PREFIX-NFR-2: Usability

**WHILE** [operating condition]  
**THEN** the system **SHALL** [usability requirement]

## Error Handling

### PREFIX-ERR-1: Error Condition

**WHILE** [operation in progress]  
**WHERE** [error condition occurs]  
**THEN** the system **SHALL** [error handling behavior]

## Appendix A: Example Schema Name

For larger examples, schemas, or formats that would clutter the requirements.

## Notes

- Use one short prefix (2-5 chars) specific to this feature; number sequentially.
- Use EARS keywords: WHILE, WHEN, WHERE, THEN, SHALL.
- Be specific and testable.
- Keep inline examples to 1-3 lines; use appendices for anything larger.
````
