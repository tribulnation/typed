# Error Handling

Every exception the client raises for a failed request or stream derives from `typed_risex.Error` and is importable from `typed_risex`. The one exception is a usage error: subscribing to a WebSocket channel that is already open on the client raises a plain `RuntimeError` (see [Listen To Live Streams](../how-to/listen-to-live-streams.md#changing-a-channels-filter)).

| Exception | Raised when |
| --- | --- |
| `AuthError` | a key the call needs is missing or invalid, the signer is not registered or its allowance expired, a login or WebSocket authentication is rejected, or the API answers `Unauthenticated`/`PermissionDenied` |
| `RateLimited` | HTTP 429 (RISEx allows 500 REST requests per 10 seconds and 10 WebSocket requests per second, per IP) |
| `BadRequest` | the API rejects the request: invalid arguments, unknown order or market, failed preconditions such as insufficient margin, or business limits such as the open-order limit |
| `ApiError` | any other API failure, including internal and unavailable errors |
| `NetworkError` | the connection fails or times out |
| `ValidationError` | a response does not match its expected type |
| `LogicError` | the API's signing domain names a different chain than the configured network; the client refuses to sign |

`BadRequest`, `AuthError` and `RateLimited` are subclasses of `ApiError`. An API error's `args` are the venue's error code (a gRPC status name such as `InvalidArgument`, or the HTTP status when the body is not a RISEx error), its message, and, for RISEx errors, the raw response body.

```python
from typed_risex import RISEx, ApiError, AuthError, BadRequest, NetworkError, RateLimited, ValidationError

async with RISEx.new(network='testnet') as client:
  try:
    await client.orders.cancel(1, order_id='0x...')
  except AuthError as e:
    print('check your keys and signer registration:', e)
  except RateLimited:
    print('slow down')
  except BadRequest as e:
    print('rejected:', e)
  except ApiError as e:
    print('venue error:', e)
  except ValidationError as e:
    print('unexpected response shape:', e)
  except NetworkError as e:
    print('connection problem:', e)
```

Writes are never retried automatically: a timed-out order may still have been submitted, so check `client.orders.open(...)` before placing it again. If a signature fails because of a nonce conflict, the client reloads its nonce state before the next signature.

To skip response validation for one call, pass `validate=False`; for the whole client, `RISEx.new(validate=False)`.
