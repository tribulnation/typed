# Error Handling

Every exception derives from `typed_extended.Error` and is importable from the package root.

| Exception | Raised when |
| --- | --- |
| `AuthError` | HTTP `401`/`403`; an invalid Stark key, signature or vault (codes `1100`-`1102`); no account selected (`1500`); missing or inconsistent credentials when building the client, or a signed call on a client without a Stark key |
| `RateLimited` | HTTP `429` |
| `BadRequest` | any other `4xx`, and any other error code: unknown market, invalid order, insufficient balance, ... |
| `ApiError` | HTTP `5xx` or `451` (geoblocked), and server-side error codes (`1006` unhandled error, `1010` maintenance mode) |
| `NetworkError` | the connection failed or timed out |
| `ValidationError` | a response or stream message did not match its declared type, or a successful response was not JSON |

An HTTP error status maps by its code whatever the body, including a plain-text or HTML
page from a proxy.

`ApiError`'s arguments carry the venue's error `code`, its `message` and the full response
body.

```python
from typed_extended import ApiError, AuthError, BadRequest, Extended, RateLimited

async with Extended.new() as client:
  try:
    order = await client.account.order(123456789)
  except AuthError:
    print('check EXTENDED_API_KEY')
  except RateLimited:
    print('slow down')
  except BadRequest as e:
    print('rejected:', e.args)
  except ApiError as e:
    print('venue error:', e.args)
```

## Nothing There

A read whose answer is "nothing" returns it rather than raising: `client.account.balance()`
returns `None` for a sub-account holding nothing, `client.account.spot_balances()` an empty
list, `client.account.order(...)` `None` for an id the venue does not know, and
`client.info.orderbook(...)` `None` for an inactive or unknown market. Any other `404` still
raises `BadRequest`.

## Asynchronous Rejections

An order accepted by `client.orders.create(...)` can still be rejected by the matching engine.
That is not an exception: the order's `status` becomes `REJECTED`, with the reason in
`statusReason`, on the account stream and in `client.account.order(...)`.

## Validation

Responses are validated by default. A `ValidationError` means the venue sent something the
types don't describe. Pass `validate=False` to one call, or to `Extended.new(...)`, to get
the raw payload back instead.
