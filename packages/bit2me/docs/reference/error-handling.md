# Error Handling

Bit2Me distinguishes transport errors, response validation failures, and non-2xx API responses.

## Common Error Categories

- `Error`: base exception type for this package
- `NetworkError`: connection failures, timeouts, transport errors
- `ValidationError`: the response shape did not match the expected schema
- `ApiError`: the remote API returned a non-2xx response
- `BadRequest`: API returned HTTP 400
- `Unauthorized`: API returned HTTP 401
- `NotFound`: API returned HTTP 404
- `RateLimited`: API returned HTTP 429
- `InternalServerError`: API returned HTTP 5xx

## Recommended Pattern

```python
from bit2me.core import ApiError, NetworkError, ValidationError, Unauthorized, RateLimited

try:
  ...
except ValidationError:
  ...
except Unauthorized:
  ...
except RateLimited:
  ...
except ApiError:
  ...
except NetworkError:
  ...
```

## Operational Guidance

- retry transient network failures carefully
- do not blindly retry `Unauthorized`
- log validation failures because they often signal upstream API changes
- inspect `ApiError.status` and `ApiError.payload` when debugging endpoint failures
