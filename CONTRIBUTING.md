# Contributing to typed

Each package mixes generated and hand-written code, and where a file sits decides how a
change to it lands.

Generated: everything under `packages/<slug>/pkg/src/<slug>/` *except* that package's
`core/` subdirectory. A bug there is best filed as an issue, not a pull request, since the
next generation run overwrites hand edits.

Hand-written, and taking PRs directly:

- `packages/<slug>/pkg/src/<slug>/core/` — the per-client core: transport, envelope,
  authentication, error mapping.
- `packages/<slug>/docs/` and `packages/<slug>/README.md`.
- `packages/core/` — typed-core itself, hand-written throughout.

## Filing a bug

Open an issue against the package it's in, using the issue template — the smallest
reproduction you can manage (the failing call, the response that didn't validate, the type
that didn't match), plus the package name and version. This still applies to generated
code: file the issue, don't PR the generated file.

## Proposing a change to hand-written code

Open a PR against the specific file(s). A maintainer reviews it directly against that
package; `packages/core/` changes are checked against every package that depends on it.
