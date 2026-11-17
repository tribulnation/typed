# Error Handling

Every exception the client raises derives from `typed_nado.Error`, and every class is
importable from the top-level package:

```python
from typed_nado import (
  Error,            # base class of everything below
  NetworkError,     # connection failure or timeout
  ValidationError,  # a response did not match its declared type
  ApiError,         # the venue reported a failure
  BadRequest,       # the request was rejected (bad parameters, failed order checks, ...)
  AuthError,        # missing or invalid key, bad signature, unauthorized, blocked location
  RateLimited,      # a rate limit was hit
  LogicError,       # an inconsistency the client detected itself
)
```

`BadRequest`, `AuthError` and `RateLimited` are subclasses of `ApiError`.

## How Nado Errors Map

Nado reports most failures as a JSON body carrying an `error` and an `error_code`, often
with HTTP 200. When a response names an error this way — `{error, error_code}`, or an
engine envelope with `status: "failure"` — the code decides the exception, whatever the
HTTP status:

| `error_code` | Exception |
| --- | --- |
| 1000, 1015 | `RateLimited` |
| 1001-1003 (blacklisted or blocked location), 2014 (cancel for another subaccount), 2027-2029, 2034, 2035 (signature), 2050 (unauthorized) | `AuthError` |
| 1004, 2068 (maintenance), 2053, 2063, 5000 (internal), 4003 (EVM revert), any other code from 4001 to 4999 | `ApiError` |
| any other code (every other 1xxx, 2xxx and 3xxx code, and 4000) | `BadRequest` |
| no code: `RateLimited` when the message mentions a rate limit, otherwise | `ApiError` |

A non-2xx response that names no error (a plain-text body, or JSON without `error` or
`status: "failure"`) is mapped by its HTTP status instead:

| HTTP status | Exception |
| --- | --- |
| 401, 403 | `AuthError` |
| 429 | `RateLimited` |
| any other 4xx (e.g. the plain-text 422 for a body that did not parse as a request) | `BadRequest` |
| 5xx | `ApiError` |

A plain-text reply on the gateway WebSocket (a frame that did not parse as a request)
raises `BadRequest`, and a 2xx body that is not JSON, or not the expected envelope, raises
`ValidationError`. A signed call on a `public=True` client, a call or stream that defaults
to your own subaccount (`subaccount`/`sender` left out) on a `public=True` client, or
`Nado.new()` with no key found, raises `AuthError` before anything is sent.

The venue's own message and code are kept in the exception's message.

Nado answers `403` to any HTTP request without an `Accept-Encoding` header; the client
always sends `Accept-Encoding: gzip, deflate`, so you never need to set it.

## Example

Try error handling on testnet: an order that passes the venue's checks really executes.

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado, AuthError, BadRequest, RateLimited, order_appendix

async with Nado.new(network='testnet') as client:  # NADO_TESTNET_PRIVATE_KEY
  try:
    await client.gateway.place_order(
      product_id=2,
      order={
        'priceX18': 50_000 * 10**18 + 1,  # off the price tick: rejected
        'amount': 2 * 10**15,
        'expiration': datetime.now(timezone.utc) + timedelta(days=1),
        'appendix': order_appendix('post_only'),
      },
    )
  except BadRequest as e:
    print('rejected:', e)  # e.g. a price off the tick, or a post-only order that would cross
  except RateLimited:
    print('slow down')
  except AuthError as e:
    print('check NADO_TESTNET_PRIVATE_KEY / NADO_TESTNET_ADDRESS:', e)
```

A public client shows `AuthError` with nothing sent at all:

```python
from typed_nado import Nado, AuthError

async with Nado.new(public=True) as client:
  try:
    await client.trigger.list_trigger_orders()
  except AuthError as e:
    print('needs a key:', e)
```

## Validation

Responses are validated by default. Turn it off per client with `Nado.new(validate=False)`
or per call with `validate=False`; a mismatch raises `ValidationError` naming the field.
