# Error Handling

All exceptions live in `binance.core.exc`, re-exporting `typed_core`'s exception hierarchy:

```python
from binance.core.exc import (
  Error,
  NetworkError,
  ValidationError,
  ApiError,
  BadRequest,
  AuthError,
  RateLimited,
  LogicError,
)
```

- `NetworkError` — connection failures, timeouts, transport errors.
- `AuthError` — missing or invalid credentials, a rejected or malformed signature.
- `RateLimited` — Binance's rate limits, including IP bans (HTTP 418) and WAF blocks (HTTP 403).
- `BadRequest` — any other rejected request (invalid parameters, unknown symbol, and so on).
- `ApiError` — any other unsuccessful response, including HTTP 5xx.
- `ValidationError` — a response didn't match its expected shape; only raised when `validate=True` (the default).
- `LogicError` — incorrect local usage, such as an unsupported call for the current transport.

`Error` is the common base class — catch it to handle every case uniformly.

```python
from binance.core.exc import ApiError, AuthError, NetworkError, RateLimited, ValidationError

try:
  ...
except ValidationError:
  ...
except AuthError:
  ...
except RateLimited:
  ...
except ApiError:
  ...
except NetworkError:
  ...
```

## Notes

- Binance's own docs say a 5xx response's execution status is unknown — it may have
  succeeded despite the error. `ApiError` is still raised, but don't blindly retry order
  placement on it without checking whether the order actually went through.
- Back off on `RateLimited` according to the response's own rate-limit headers rather than a
  fixed delay.
