---
type: Styleguide Rule
description: "Spec scriptlets contain no debugging commands, no ./ prefixes, no unnecessary cat, no trailing whitespace and no pre-initialised environment variables; use pushd/popd, validate external input, and build on both x86_64 and aarch64."
language: rpm-spec
category: formatting
---
# Clean spec scriptlets

- No leftover debugging (`ls -la`, `find .`, `set -x`).
- No `./` prefixes and no useless `cat`.
- Don't pre-initialise environment variables at the top of scripts; it clobbers values inherited from the SDK.
- `pushd`/`popd` instead of bare `cd`.
- Validate external input before using it.
- Handle architecture differences with conditionals on the arch macros (`%ifarch`, `%{_cross_arch}`), not by hard-coding one architecture.
- Factor repeated install or build steps into a loop or macro; remove intermediate build artifacts that are not packaged.
- No trailing whitespace; consistent indentation and formatting with sibling specs.
- Build on both x86_64 and aarch64 before submitting.

## Good

```spec
pushd cmd/foo
go build -ldflags "${GOLDFLAGS}" -o ../../bin/foo .
popd
```

## Bad

```spec
GOFLAGS=""
cd cmd/foo
ls -la
cat ./config.in | sed 's/x/y/' > ./config
```
