# Error Handling

Typed Coinbase raises `typed_core`'s standard exceptions, re-exported from `coinbase.core.exc`:

```python
from coinbase.core.exc import (
  ApiError, AuthError, BadRequest, RateLimited, ValidationError, NetworkError, LogicError,
)
```

- `AuthError` — missing/invalid credentials, or an HTTP `401`/`403`.
- `BadRequest` — any other HTTP `4xx`.
- `RateLimited` — HTTP `429`.
- `ApiError` — HTTP `5xx`, or any other non-2xx status.
- `ValidationError` — the response didn't match its declared schema.
- `NetworkError` — connection failures, timeouts.
- `LogicError` — incorrect local usage, e.g. an authenticated call on a `public=True` client.

HTTP status is the only failure signal on both `accounts` (v2) and `advanced_trade` (v3) — there is no embedded error code on a `200` response to branch on instead. The response body (`{"error", "message", "error_details"}` on v3, `{"error", "code", "message", "details"}` on v2) rides along on the raised exception for debugging.

## Pattern

```python
from coinbase import Coinbase
from coinbase.core.exc import ApiError, AuthError, RateLimited, ValidationError

async with Coinbase.new() as client:
  try:
    accounts = await client.advanced_trade.accounts.list()
  except AuthError:
    ...
  except RateLimited:
    ...
  except ApiError:
    ...
  except ValidationError:
    ...
```

## WebSocket

A rejected (un)subscribe on `market_data`/`user` raises the same split: `AuthError` for an authentication failure, `BadRequest` for anything else. That only covers a bad channel *name* — a bad channel *argument* (e.g. an unknown `product_id`) is not rejected by Coinbase at all; the acknowledgement comes back with an empty subscription instead, so check that it actually covers what was requested.
