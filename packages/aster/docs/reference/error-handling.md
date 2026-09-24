# Error Handling

Every exception is importable from `typed_aster` and derives from `typed_aster.Error`.

| Exception | Raised when |
| --- | --- |
| `AuthError` | Missing or mismatched wallets, a rejected signature, an unknown agent, an expired nonce, or an account that has not deposited yet (`-5050`) |
| `RateLimited` | Aster answers `429`, `418` (IP ban) or `403`, or a rate-limit error code |
| `BadRequest` | Any other `4XX` rejection, such as invalid parameters or an order failing a symbol filter; also a rejected WebSocket subscription |
| `ApiError` | Server errors (`5XX`) and other failures. `AuthError`, `RateLimited` and `BadRequest` are subclasses |
| `ValidationError` | The response did not match the expected type |
| `NetworkError` | The connection failed or timed out |

API errors carry the HTTP status and Aster's `{code, msg}` body as their arguments.

## Recommended Pattern

Catch the specific subclasses before `ApiError`:

```python
from typed_aster import (
  ApiError,
  Aster,
  AuthError,
  BadRequest,
  NetworkError,
  RateLimited,
  ValidationError,
)

async with Aster.new() as client:
  try:
    await client.futures.account.balance()
  except AuthError as e:
    print('check your wallets, or deposit first:', e)
  except RateLimited:
    ...  # back off before retrying
  except BadRequest as e:
    print('rejected:', e)
  except ApiError:
    ...  # a 5XX is not proof the request failed; check the order state
  except ValidationError:
    ...  # the response shape changed
  except NetworkError:
    ...  # retry
```

## Notes

- `503` means the execution status is unknown: query the order before retrying a placement.
- A signature over the wrong network answers `Signature check failed`. Match `mainnet=` to
  where your API wallet was approved.
- Pass `validate=False` to one call, or to `Aster.new()`, to skip response validation.
