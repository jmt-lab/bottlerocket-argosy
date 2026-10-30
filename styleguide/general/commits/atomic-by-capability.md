---
type: Styleguide Rule
description: "Split a change into commits by capability (a type with its implementation and tests, a command with its handler and tests), never by artifact; target 200–400 changed lines and at most 5–6 files per commit, never more than 500 lines."
language: general
category: commits
---
# Atomic commits by capability

Each commit tells one coherent story and builds and tests on its own.

- Split by capability: a module with its types, implementation and tests; a CLI subcommand with its handler and tests; a package update with its spec, sources and patch changes.
- Do not split by artifact ("add types" → "add impl" → "add tests").
- Target 200–400 changed lines and at most 5–6 files; never exceed 500 lines unless the change is mechanical (vendoring, generated files, a version bump across many files).

## Good

1. `netdog: add bond interface parsing` (types, parser, unit tests)
2. `netdog: render bond interfaces to systemd-networkd` (renderer, tests)

## Bad

1. `netdog: add types`
2. `netdog: add implementation`
3. `netdog: add tests`
