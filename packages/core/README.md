# Typed Core

> Shared core types and utilities for Typed Clients

Every client core builds on this package. Prefer it over a client-local copy — a client
`core/` should hold only what is genuinely venue-specific (envelope extraction, error
mapping, signing, timestamp and encoding quirks).

## What it provides

| module | contents |
| --- | --- |
| `typed_core.exceptions` | `Error`, `NetworkError`, `ValidationError`, `ApiError` (`BadRequest`, `AuthError`, `RateLimited`), `LogicError` |
| `typed_core.http` | async HTTP client and response helpers |
| `typed_core.ws` | websocket socket, streams, JSON-RPC, streams-over-RPC |
| `typed_core.util` | `RateLimit`, paging and stream helpers |

Clients re-export the exceptions users are expected to catch from their own package root, so
`from bybit import AuthError` works while implementation imports still come from
`typed_core`. Route those re-exports through `lazy_loader.attach_stub` — see
`.agents/rules/python.md`. A plain `from typed_core.exceptions import ...` in an
`__init__.py` breaks type-checking for every downstream consumer of a `py.typed` package.

## References

- Building a client: `.agents/skills/client-core/SKILL.md`, `.agents/skills/client-spec/SKILL.md`
- Production review: `docs/production_guidelines.md`
