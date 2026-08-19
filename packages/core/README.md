# Typed Core

> Shared core types and utilities for Typed Clients

[![PyPI version](https://img.shields.io/pypi/v/typed-core.svg)](https://pypi.org/project/typed-core/)
[![License](https://img.shields.io/pypi/l/typed-core.svg)](LICENSE)

Every [Typed Client](https://tribulnation.com/blog/clients) builds its `core` on top of this
package. Prefer it over a client-local copy of the same logic — a client's own `core/` should
hold only what's genuinely venue-specific (envelope extraction, error mapping, signing, wire
quirks), not a reimplementation of transport, timestamps, or error types.

## Installation

```bash
pip install typed-core
```

## What it provides

| module | contents |
| --- | --- |
| `typed_core.exceptions` | `Error`, `NetworkError`, `ValidationError`, `ApiError` (`BadRequest`, `AuthError`, `RateLimited`), `LogicError` |
| `typed_core.http` | async HTTP client and response helpers |
| `typed_core.ws` | websocket socket, streams, JSON-RPC, streams-over-RPC |
| `typed_core.times` | `TimeConverter`, `EpochConverter`, `IsoConverter` — parse/dump between a venue's wire timestamp and a real `datetime` |
| `typed_core.util` | `RateLimit`, paging and stream helpers |

```python
from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds()  # epoch, milliseconds
timestamp_iso = IsoConverter()                    # RFC 3339, Z-suffixed
```

Clients re-export the exceptions users are expected to catch from their own package root, so
`from kraken import AuthError` works while implementation imports still come from
`typed_core`. Route those re-exports through `lazy_loader.attach_stub`, not a plain
`from typed_core.exceptions import ...` in an `__init__.py` — the latter breaks type-checking
for every downstream consumer of a `py.typed` package.

## License

MIT — see [LICENSE](LICENSE).
