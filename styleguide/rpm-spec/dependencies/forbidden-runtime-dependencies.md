---
type: Styleguide Rule
description: "Packages must not depend on scripting-language runtimes (Python, Bash, Ruby, Perl) or on OpenSSL; use Bottlerocket's libcrypto, and prefer actively maintained upstreams."
language: rpm-spec
category: dependencies
---
# Forbidden dependencies

Bottlerocket images ship no general-purpose interpreters and use their own crypto library.

## Good

```spec
BuildRequires: %{_cross_os}libcrypto-devel
Requires: %{_cross_os}libcrypto
```

## Bad

```spec
Requires: %{_cross_os}python3
BuildRequires: %{_cross_os}openssl-devel
```
