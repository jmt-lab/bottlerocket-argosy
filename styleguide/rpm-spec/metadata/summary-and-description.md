---
type: Styleguide Rule
description: "Summaries are sentence case; %description text starts with %{_cross_os}, is complete and non-circular, prefers upstream's official description, and makes no ambiguous support claims; a subpackage %description is exactly `%{summary}.`."
language: rpm-spec
category: metadata
---
# Summary and description

## Good

```spec
Summary: Network time synchronization daemon
%description
%{_cross_os}chrony is an implementation of the Network Time Protocol.

%package bin
Summary: Chrony binaries
%description bin
%{summary}.
```

## Bad

```spec
Summary: CHRONY NTP DAEMON
%description
The chrony package contains chrony. Fully supported for all workloads.
```
