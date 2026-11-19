# Error Handling

Every exception the client raises derives from `typed_evedex.Error`, and all are importable
from the top-level package.

| Exception | Raised when |
| --- | --- |
| `AuthError` | HTTP `401`/`403`; no credentials for a private call; an invalid private key, or an `EVEDEX_ADDRESS` that is invalid or does not match it; a wallet with no exchange account yet (`user_not_found_error`); a rejected EIP-712 signature (`invalid_signature_error`); a refused private channel subscription |
| `RateLimited` | HTTP `429` |
| `BadRequest` | Any other `4xx`: invalid parameters, unknown instrument or order, insufficient funds, a price outside the mark-price band, ... |
| `ApiError` | `5xx` and other venue errors; a stream the server ended for good. Base class of `AuthError`, `RateLimited` and `BadRequest` |
| `ValidationError` | A response or stream publication does not match its expected type |
| `NetworkError` | Connection failures, timeouts, a dropped WebSocket connection, a stream the server ended and asks to resubscribe |
| `LogicError` | The client was used incorrectly, before anything is sent: a signed request missing a field, an amount that is negative or not a number, an invalid API-key `expire_at` |

API errors carry the HTTP status and the venue's error body as `args`. The body's `label`
names the error (`insufficient_funds_error`, `mark_price_limit_exceeded_error`,
`order_not_found_error`, ...):

```python
from typed_evedex import ApiError, AuthError, BadRequest, Evedex, RateLimited

async with Evedex.new() as client:
  try:
    await client.exchange.orders.place_limit(
      instrument='BTCUSD', side='BUY', leverage=1, quantity='0.001', limit_price='60000'
    )
  except AuthError:
    raise  # fix credentials; do not retry
  except RateLimited:
    ...  # back off: 30 heavy requests per 60 s per account
  except BadRequest as e:
    status, body = e.args
    print(status, body)
  except ApiError:
    ...  # venue-side failure; may be retried
```

## Guidance

- Expired session tokens are refreshed automatically; an `AuthError` means the credential
  itself is wrong or missing.
- Do not blindly retry order placement after a `NetworkError`: check the order by id
  (`client.exchange.orders.get`) first. Placing with an explicit `id=` makes that easy.
- Validation can be turned off for a single call with `validate=False`, or for the whole
  client with `Evedex.new(validate=False)`. A `ValidationError` usually means the venue
  changed a response shape.
