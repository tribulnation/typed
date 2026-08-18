# Error Handling

MEXC distinguishes transport failures, authentication failures, validation failures, and API-level failures.

## Common Error Categories

1. `Error`: base package exception.
2. `NetworkError`: connection failures, timeouts, and transport errors.
3. `AuthError`: missing credentials, invalid signatures, or rejected authentication.
4. `BadRequest`: invalid request parameters or malformed payloads rejected locally or remotely.
5. `RateLimited`: provider-side rate limiting.
6. `ApiError`: the remote API returned an error payload or unsuccessful response.
7. `ValidationError`: the response shape did not match the expected schema.
8. `LogicError`: incorrect local usage of the client.

## Recommended Pattern

```python
from mexc import ApiError, AuthError, NetworkError, RateLimited, ValidationError
from mexc import MEXC

async with MEXC.new() as client:
  try:
    positions = await client.futures.position.open()
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

## Operational Guidance

1. Retry transient network failures carefully.
2. Do not blindly retry authentication failures.
3. Back off on rate limits according to the provider's documented policy.
4. Log validation failures because they often signal upstream API changes.
5. Inspect the original request context when debugging inconsistent symbol or timestamp errors.
