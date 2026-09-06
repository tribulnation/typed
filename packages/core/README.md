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

### Paging

Every generated `<method>_paged` returns a `PaginatedResponse`: awaitable (every row,
flattened) and async-iterable (one page of rows at a time). Each page is one pure
`next(state)` call, so a caller can retry or resume a single page rather than the whole walk.

```python
from typed_core import PaginatedResponse

paging = client.market.kline_paged(symbol='BTCUSDT', interval='1', start=start, end=end)
candles = await paging                       # every row, flattened
async for rows in paging: ...                # one page at a time
async for page in paging.pages():            # Page(rows, state, next), for checkpointing
  checkpoint(page.next)
paging.resume(saved_state)                   # restart from a checkpointed state
paging.via(retried)                          # route every page fetch through a middleware
```

`via(call)` hands each page fetch to `call` as one zero-argument coroutine function, so a
retry or logging layer wraps a page without unrolling the loop by hand.

Clients re-export the exceptions users are expected to catch from their own package root, so
`from kraken import AuthError` works while implementation imports still come from
`typed_core`. Route those re-exports through `lazy_loader.attach_stub`, not a plain
`from typed_core.exceptions import ...` in an `__init__.py` — the latter breaks type-checking
for every downstream consumer of a `py.typed` package.

## License

MIT — see [LICENSE](LICENSE).
