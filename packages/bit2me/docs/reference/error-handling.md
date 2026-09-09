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

### Withdrawal Fees From A Failed Proforma

Bit2Me publishes no withdrawal fee schedule. The only place a fee appears is a wallet proforma (`client.v1.wallet.transactions.preview`), and when the pocket can't cover the amount, the `412 not-enough-funds` error body still carries the fee Bit2Me would have charged. `not_enough_funds` reads that body off the exception, typed as `ProformaShortfall`, and returns `None` for any other error:

```python
from typed_bit2me import Bit2Me
from typed_bit2me.core.exc import ApiError, not_enough_funds

async with Bit2Me.new() as client:
  try:
    proforma = await client.v1.wallet.transactions.preview(
      amount='0.01',
      currency='ETH',
      destination={'address': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', 'network': 'ethereum'},
    )
    print(proforma.get('fee'))  # {'network': {'amount': Decimal('0.00020000'), 'currency': 'ETH'}}
  except ApiError as e:
    shortfall = not_enough_funds(e)
    if shortfall is None:
      raise
    print(shortfall['fee'])  # Decimal('0.00020000'), what the withdrawal would have cost
```

`ProformaShortfall` carries `code` (`'not-enough-funds'`), `fee` (a `Decimal`, in the requested currency), and usually the request echo too: `amount`, `currency` and `minimumAmount`. Two things to keep in mind:

1. It's the withdrawal fee for that exact request, not a schedule: quote each asset/network pair you care about.
2. The key needs the wallet-withdrawal permission, else `preview` raises `AuthError` before any body is produced.

## WebSocket

`client.trading_ws`'s `authenticate` handshake raises `AuthError` when Bit2Me rejects the token, and any rejected command or subscribe request raises `BadRequest` with Bit2Me's `error` string. `client.crypto_ws` currently surfaces an authentication failure as a `NetworkError` from `notifications()`, since Bit2Me closes the socket rather than replying with an error frame.
