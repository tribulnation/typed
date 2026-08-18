# Error Handling

All exceptions live at `kraken.core.exc`, not the top-level package:

```python
from kraken.core.exc import ApiError, AuthError, BadRequest, LogicError, NetworkError, RateLimited, ValidationError
```

- `AuthError` -- missing/invalid credentials, invalid signature, invalid nonce, permission
  denied, temporary lockout.
- `BadRequest` -- invalid parameters (e.g. order below the pair's minimum size/cost) or
  general/trade/funding errors.
- `RateLimited` -- Kraken's own or Trading Engine rate limits were exceeded.
- `ApiError` -- any other application-level error Kraken returned (order-management,
  service, or business-model errors).
- `ValidationError` -- the response did not match the expected schema.
- `NetworkError` -- connection failures, timeouts, transport-level errors.
- `LogicError` -- incorrect local usage of the client.

## How Errors Arrive

Kraken answers HTTP 200 for almost every logical failure: the body carries
`{"error": ["<Category>:<Description>", ...], "result": {...}}`, and a non-empty `error`
array is what raises. Streams errors follow the same `<Category>:<Description>` shape as a
single string on the reply frame, e.g. `EOrder:Cost minimum not met` raises `BadRequest`.

| Category | Exception |
|---|---|
| `EAPI`, `EAuth`, `EAccount` | `AuthError` |
| `EGeneral`, `ETrade`, `EFunding` | `BadRequest` |
| `EOrder`, `EService`, `EBM` | `ApiError` |

A handful of messages are re-mapped by substring regardless of category, matching
Kraken's own [error reference](https://docs.kraken.com/exchange/guides/general/errors):
rate-limit messages always raise `RateLimited`; `Invalid key`/`Invalid signature`/
`Invalid nonce`/`Permission denied`/`Temporary lockout` always raise `AuthError`; and
`Invalid price`/tick-size/minimum-size messages always raise `BadRequest`.

## Recommended Pattern

```python
from kraken import Kraken
from kraken.core.exc import ApiError, AuthError, BadRequest, RateLimited

async with Kraken.new() as client:
  try:
    order = await client.spot.trading.add_order(
      pair='XBTUSD', type='buy', ordertype='market', volume='0.0001',
    )
  except RateLimited:
    ...  # back off and retry
  except AuthError:
    ...  # credentials are wrong, don't retry blindly
  except BadRequest:
    ...  # e.g. below the pair's order minimum -- fix the request, don't retry as-is
  except ApiError:
    ...  # some other application-level failure
```
