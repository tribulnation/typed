# Error Handling

`Deribit` maps every JSON-RPC error Deribit returns onto one of these exceptions,
importable from `typed_deribit` directly:

| exception | raised on |
| --- | --- |
| `AuthError` | missing credentials; auth required (`10000`), invalid credentials (`10001`), bad/expired token (`13009`), token revoked (`13010`), missing permissions (`13011`), 2FA failed (`13668`) |
| `RateLimited` | `too_many_requests` (`10028`) |
| `BadRequest` | order/self-trade errors (`11000`-`11009`), `bad_request` (`11050`) |
| `ApiError` | any other non-empty JSON-RPC `error` |
| `ValidationError` | the response shape didn't match the expected schema (`validate=True`, the default) |
| `NetworkError` | connection failures, timeouts |
| `LogicError` | incorrect local usage of the client (e.g. a truncated pagination window) |

## Pattern

```python
from typed_deribit import (
  ApiError, AuthError, BadRequest, Deribit, NetworkError, RateLimited, ValidationError,
)

async with Deribit.new(testnet=True) as client:
  try:
    summary = await client.account.get_account_summary(currency='BTC')
  except AuthError:
    ...  # missing or rejected credentials
  except RateLimited:
    ...  # back off and retry
  except BadRequest:
    ...  # invalid parameters
  except ValidationError:
    ...  # response didn't match the expected schema
  except ApiError:
    ...  # any other venue-reported error
  except NetworkError:
    ...  # connection failure
```

Every call also accepts `validate=False` per-call, or `Deribit.new(validate=False)`
client-wide, to skip response validation and its `ValidationError`.
