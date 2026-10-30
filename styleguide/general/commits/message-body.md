---
type: Styleguide Rule
description: "After the header and a blank line, the commit body explains what changed and why and ends with a Signed-off-by trailer (git commit -s); write multi-line messages to a file and commit with -F so newlines are real, never -m with escaped \\n."
language: general
category: commits
---
# Commit message body

- The body, after one blank line, says what changed and why: the motivation, upstream issue or release notes link, and anything a reviewer cannot see from the diff.
- End with a `Signed-off-by:` trailer (`git commit -s`).
- Compose multi-line messages in a file and commit with `git commit -s -F <file>`. Passing a string with escaped `\n` to `-m` (common when a tool builds the command) writes literal backslash-n into the history.

## Good

```
chrony: update to 4.6.1

Picks up the upstream fix for leap-second smearing on aarch64.

Signed-off-by: Jane Doe <jane@example.com>
```

## Bad

```
chrony: update to 4.6.1\n\nPicks up upstream fix.\n
```
