# Error Handling

All exceptions live at `typed_bit2me.core.exc`:

```python
from typed_bit2me.core.exc import (
  Error,          # base of everything below
  NetworkError,   # connection failure, timeout
  ValidationError,  # response didn't match its documented schema
  ApiError,       # non-2xx HTTP response, generic
  BadRequest,     # HTTP 400, or a rejected trading_ws command/subscribe
  AuthError,      # HTTP 401/403, missing credentials, or a rejected WS authenticate
  RateLimited,    # HTTP 429/418
)
```

`BadRequest`, `AuthError`, and `RateLimited` all subclass `ApiError`; catch `ApiError` alone to handle every non-2xx response the same way.

## HTTP

```python
from typed_bit2me import Bit2Me
from typed_bit2me.core.exc import ApiError, AuthError, RateLimited, NetworkError, ValidationError

async with Bit2Me.new() as client:
  try:
    order = await client.v1.trading.orders.get('some-order-id')
  except AuthError:
    pass  # missing/invalid credentials
  except RateLimited:
    pass  # back off and retry
  except ApiError as e:
    status, payload = e.args  # HTTP status code and decoded error body
    print(status, payload)
  except ValidationError:
    pass  # Bit2Me's response no longer matches the documented shape
  except NetworkError:
    pass  # connection/timeout
```

`ApiError.args` is `(status_code, payload)`, where `payload` is the decoded JSON error body when Bit2Me returned one, else raw text.

## WebSocket

`client.trading_ws`'s `authenticate` handshake raises `AuthError` when Bit2Me rejects the token, and any rejected command or subscribe request raises `BadRequest` with Bit2Me's `error` string. `client.crypto_ws` currently surfaces an authentication failure as a `NetworkError` from `notifications()`, since Bit2Me closes the socket rather than replying with an error frame.
